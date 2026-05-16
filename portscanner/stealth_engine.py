"""
stealth_engine.py — SYN (half-open) scan engine via Scapy.
Runs Scapy's blocking sr1() inside a ThreadPoolExecutor so the event loop
stays unblocked.  Requires root / CAP_NET_RAW.
Part of the GhostRunner Ecosystem | Author: liragbr
"""
from __future__ import annotations

import asyncio
import os
import random
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict

from tqdm import tqdm

from .scanner import ScanResult

try:
    from scapy.all import IP, TCP, conf, sr1  # type: ignore[import]
    conf.verb = 0          
    _SCAPY_OK = True
except ImportError:
    _SCAPY_OK = False

_RED    = "\033[91m"
_RESET  = "\033[0m"
_BOLD   = "\033[1m"
_DIM    = "\033[2m"


_SYN_ACK = 0x12 
_RST     = 0x04   

class StealthPortScanner:
    """
    SYN half-open scanner.

    Architecture note
    -----------------
    Scapy's ``sr1()`` is purely synchronous (it drops into a raw-socket
    select loop).  Running it directly inside a coroutine would block the
    entire event loop for the duration of each probe.

    Solution: every probe is dispatched via ``loop.run_in_executor()`` into a
    ``ThreadPoolExecutor``.  The coroutine ``_scan_one`` simply awaits the
    executor future, so the event loop remains free to schedule other tasks.
    The semaphore still caps how many threads are alive concurrently — keeping
    memory and file-descriptor usage bounded exactly as in the TCP engine.
    """

    def __init__(
        self,
        host:        str,
        ports:       list[int],
        timeout:     float,
        concurrency: int,
    ) -> None:
        if not _SCAPY_OK:
            raise RuntimeError(
                "scapy is not installed.\n"
                "  pip install scapy\n"
                "Stealth mode requires root / CAP_NET_RAW privileges."
            )
        if os.geteuid() != 0:
            raise PermissionError(
                "SYN scan requires root privileges (or CAP_NET_RAW).\n"
                "  sudo python -m portscanner <target> --stealth ..."
            )

        self.host        = host
        self.ports       = ports
        self.timeout     = timeout
        self.sem         = asyncio.Semaphore(concurrency)
       
        self._executor   = ThreadPoolExecutor(max_workers=min(concurrency, 200))

    async def run(self) -> list[ScanResult]:
        results: list[ScanResult] = []
        tasks = [
            asyncio.create_task(self._scan_one(port))
            for port in self.ports
        ]

        bar_fmt = (
            "  {l_bar}{bar}| {n_fmt}/{total_fmt} ports"
            " [{elapsed}<{remaining}, {rate_fmt}]"
        )

        with tqdm(
            total=len(tasks),
            desc=f"  {'SYN Stealth':12}",
            unit="port",
            colour="red",
            bar_format=bar_fmt,
            dynamic_ncols=True,
        ) as pbar:
            for fut in asyncio.as_completed(tasks):
                result: ScanResult = await fut
                pbar.update(1)

                if result.open:
                    line = (
                        f"  {_RED}{_BOLD}[SYN-ACK]{_RESET}"
                        f"  {result.port:>5}/tcp"
                        f"  {_DIM}latency={result.latency_ms}ms{_RESET}"
                    )
                    tqdm.write(line)

                results.append(result)

        self._executor.shutdown(wait=False)
        return results

    async def _scan_one(self, port: int) -> ScanResult:
        async with self.sem:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(
                self._executor,
                self._syn_probe,
                port,
            )

    def _syn_probe(self, port: int) -> ScanResult:
        """
        Forge a TCP SYN, wait for SYN-ACK, then immediately RST.

        Flow
        ----
        Client   →  SYN            (we forge this)
        Server   →  SYN-ACK        (port is OPEN)   or  RST/nothing (CLOSED/filtered)
        Client   →  RST            (we send to clean up — no full handshake logged)
        """
        src_port = random.randint(49152, 65535) 

        pkt = IP(dst=self.host) / TCP(
            sport=src_port,
            dport=port,
            flags="S",
            seq=random.randint(1_000_000, 4_000_000_000),
        )

        t0 = time.perf_counter()
        try:
            resp = sr1(pkt, timeout=self.timeout, verbose=0)
            latency_ms = (time.perf_counter() - t0) * 1000

            if resp is None:
                return ScanResult(self.host, port, False)

            if not resp.haslayer(TCP):
                return ScanResult(self.host, port, False)

            flags = resp[TCP].flags
            if int(flags) == _SYN_ACK:
                rst_pkt = IP(dst=self.host) / TCP(
                    sport=src_port,
                    dport=port,
                    flags="R",
                    seq=resp[TCP].ack, 
                )
                sr1(rst_pkt, timeout=0.15, verbose=0)
                return ScanResult(self.host, port, True, None, round(latency_ms, 2))

            return ScanResult(self.host, port, False)

        except Exception:
            return ScanResult(self.host, port, False)

    @staticmethod
    def to_dict(results: list[ScanResult]) -> list[dict]:
        return [asdict(r) for r in results]
