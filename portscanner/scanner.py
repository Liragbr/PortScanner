from __future__ import annotations

import asyncio
import socket
from dataclasses import dataclass, asdict

from tqdm import tqdm

_GREEN  = "\033[92m"
_YELLOW = "\033[93m"
_RESET  = "\033[0m"
_BOLD   = "\033[1m"
_DIM    = "\033[2m"

_HTTP_PROBE_TEMPLATE = (
    "GET / HTTP/1.1\r\n"
    "Host: {host}\r\n"
    "User-Agent: Mozilla/5.0 (compatible; GhostScanner/1.0)\r\n"
    "Accept: */*\r\n"
    "Connection: close\r\n\r\n"
)

@dataclass(slots=True)
class ScanResult:
    host:       str
    port:       int
    open:       bool
    banner:     str | None  = None
    latency_ms: float | None = None

class AsyncPortScanner:
    """
    Asynchronous TCP Connect scanner with:
    • Real-time tqdm progress bar (open ports printed inline via tqdm.write)
    • Two-stage banner grabbing: passive read → active HTTP probe fallback
    """

    def __init__(
        self,
        host:        str,
        ports:       list[int],
        timeout:     float,
        concurrency: int,
        grab_banner: bool,
    ) -> None:
        self.host        = host
        self.ports       = ports
        self.timeout     = timeout
        self.sem         = asyncio.Semaphore(concurrency)
        self.grab_banner = grab_banner

    async def run(self) -> list[ScanResult]:
        """
        Drive all scan tasks through asyncio.as_completed so that results
        surface the moment each connection resolves.  tqdm is updated
        synchronously per result; tqdm.write() keeps open-port lines from
        tearing the progress bar.
        """
        results: list[ScanResult] = []
        tasks = [asyncio.create_task(self._scan_one(port)) for port in self.ports]

        bar_fmt = (
            "  {l_bar}{bar}| {n_fmt}/{total_fmt} ports"
            " [{elapsed}<{remaining}, {rate_fmt}]"
        )

        with tqdm(
            total=len(tasks),
            desc=f"  {'TCP Connect':12}",
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
                        f"  {_GREEN}{_BOLD}[OPEN]{_RESET}"
                        f"  {result.port:>5}/tcp"
                        f"  {_DIM}latency={result.latency_ms}ms{_RESET}"
                    )
                    if result.banner:
                        line += f"  {_YELLOW}banner={result.banner!r}{_RESET}"
                    tqdm.write(line)

                results.append(result)

        return results

    async def _scan_one(self, port: int) -> ScanResult:
        async with self.sem:
            loop  = asyncio.get_running_loop()
            start = loop.time()
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(self.host, port),
                    timeout=self.timeout,
                )
                latency = (loop.time() - start) * 1000
                banner  = None

                if self.grab_banner:
                    banner = await self._grab_banner_active(reader, writer, port)

                writer.close()
                await writer.wait_closed()
                return ScanResult(self.host, port, True, banner, round(latency, 2))

            except (TimeoutError, asyncio.TimeoutError, OSError, socket.gaierror):
                return ScanResult(self.host, port, False)

    async def _grab_banner_active(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        port:   int,
    ) -> str | None:
        """
        Stage 1 — Passive read: wait briefly for the server to push data
                  (SSH, FTP, SMTP, etc. announce themselves on connect).
        Stage 2 — Active HTTP probe: if the service stayed silent, inject a
                  generic GET request and attempt another read.  Useful for
                  HTTP/S services that only respond to client-initiated data.
        """
        banner = await self._passive_read(reader, timeout=0.40, max_bytes=512)
        if banner:
            return banner

        try:
            probe = _HTTP_PROBE_TEMPLATE.format(host=self.host).encode()
            writer.write(probe)
            await asyncio.wait_for(writer.drain(), timeout=0.30)
            banner = await self._passive_read(reader, timeout=0.60, max_bytes=1024)
            return banner
        except Exception:
            return None

    @staticmethod
    async def _passive_read(
        reader:    asyncio.StreamReader,
        timeout:   float,
        max_bytes: int,
    ) -> str | None:
        """Read up to *max_bytes* bytes within *timeout* seconds; return stripped
        UTF-8 text or None on failure / empty response."""
        try:
            data = await asyncio.wait_for(reader.read(max_bytes), timeout=timeout)
            text = data.decode(errors="ignore").strip()
            return text[:256] if text else None
        except Exception:
            return None

    @staticmethod
    def to_dict(results: list[ScanResult]) -> list[dict]:
        return [asdict(r) for r in results]
