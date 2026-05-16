from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
import re
import ipaddress
import urllib.parse
from datetime import datetime

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.live import Live
from rich.prompt import Prompt

from .ports import TOP_COMMON, parse_ports
from .scanner import AsyncPortScanner

console = Console()

def sanitize_target(target: str) -> str | None:
    """Limpa a entrada e valida se é um IP ou Hostname válido."""
    if not target:
        return None
    target = target.strip()

    if target.startswith(("http://", "https://")):
        parsed = urllib.parse.urlparse(target)
        target = parsed.netloc

    target = target.split(':')[0]
    target = target.split('/')[0]

    try:
        ipaddress.ip_address(target)
        return target
    except ValueError:
        pass

    hostname_regex = re.compile(
        r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(?:\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*$"
    )
    if hostname_regex.match(target):
        return target

    return None

def get_interactive_target() -> str:
    """Tela minimalista para receber o alvo interativamente."""
    console.clear()
    
    header = Panel(
        Text("PORT SCANNER\n", style="bold white") + 
        Text("Interactive Targeting System", style="dim white"),
        border_style="blue",
        padding=(1, 2)
    )
    console.print(Align.center(header))
    console.print()

    while True:
        target_input = Prompt.ask("  [bold cyan]>[/] [white]Analisar (IP, Domínio ou URL)[/]")
        sanitized = sanitize_target(target_input)
        
        if sanitized:
            return sanitized
            
        console.print("    [bold red][!] Entrada inválida.[/] Digite um IP (ex: 192.168.1.1) ou Domínio (ex: scanme.nmap.org).\n")

class AnimatedEye:
    def __init__(self):
        self.frame_open = r"""
                    ▓▓████████████████                  
                ▒▒██▓▓              ▒▒██████░░          
            ▓▓██░░    ▓▓██████████████    ██████        
        ██▒▒  ░░██████████████████████████    ██████    
      ██  ▒▒██░░  ████████████████████░░▒▒██▒▒  ▓▓████  
    ██  ██        ████████    ██████████    ████  ▒▒████░░
  ▒▒            ████████        ████████      ████    ██████
░░░░            ██    ██        ████████        ████  ░░████
░░              ██    ██        ████████          ████    ██
                    ▒▒████████████████████          ██████  
                    ████████████████████          ░░██████  
░░                ████████████████          ░░██▒▒████  
    ░░              ▒▒████████▒▒          ████          
      ▒▒▒▒░░                            ▒▒██            
            ░░▒▒██                ▓▓██                  
"""

        self.frame_half = r"""
                                                        
                    ▓▓████████████████                  
                ▒▒██▓▓              ▒▒██████░░          
            ▓▓██░░  ████████████████  ██████        
        ██▒▒  ░░██████████████████████████    ██████    
      ██  ▒▒██░░  ████████████████████░░▒▒██▒▒  ▓▓████  
    ██  ██        ████████████████████        ████  ▒▒████░░
  ▒▒            ████████████████████████      ████    ██████
░░░░            ████████████████████████        ████  ░░████
░░              ████████████████████████          ██    ██
                    ▒▒██████████████████          ██████  
░░                ▒▒████████████████░░    ░░██▒▒████  
    ░░              ▒▒████████▒▒          ████          
                                                        
                                                        
"""

        self.frame_closed = r"""
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
        ██▒▒░░                              ░░▒▒██      
      ██  ▒▒████████████████████████████████▒▒██▒▒▓▓████
    ██  ██    ▓▓██████████████████████████▓▓  ████  ▒▒████░░
  ▒▒            ▒▒██████████████████████▒▒    ████    ██████
░░░░              ░░██████████████████░░        ████  ░░████
░░                                                ██    ██
                                                        
                                                        
                                                        
"""
        self.frames = {
            0: self.frame_open,
            1: self.frame_half,
            2: self.frame_closed
        }
        self.current_frame_id = 0
        self.ticks = 0

    def __rich__(self) -> Panel:
        self.ticks += 1
        cycle = self.ticks % 40
        
        if cycle == 0:
            self.current_frame_id = 1  
        elif cycle == 1:
            self.current_frame_id = 2  
        elif cycle == 2:
            self.current_frame_id = 1  
        else:
            self.current_frame_id = 0  
            
        text = Text(self.frames[self.current_frame_id], style="bold yellow", no_wrap=True)
        return Panel(Align.center(text, vertical="middle"), border_style="yellow")

def make_header(target: str) -> Panel:
    grid = Table.grid(expand=True)
    grid.add_column(justify="left", ratio=1)
    grid.add_column(justify="right")
    
    title = Text(" PORT SCANNER by Liragbr ", style="bold white")
    timestamp = Text(datetime.now().strftime("%a %b %d %H:%M:%S %Y"), style="white")
    
    grid.add_row(title, timestamp)
    return Panel(grid, style="on default", border_style="blue", padding=(0, 1))

def make_session_info(args: argparse.Namespace, ports_count: int, target: str) -> Panel:
    table = Table.grid(padding=(0, 2))
    table.add_column(style="dim", justify="left")
    table.add_column(style="bold white", justify="left")

    mode = "[bold red]SYN Stealth[/] (Scapy)" if args.stealth else "[bold green]TCP Connect[/]"
    banner_info = "n/a (stealth)" if args.stealth else ("[bold yellow]Active + HTTP[/]" if args.banner else "Off")

    table.add_row("Target", target)
    table.add_row("Ports", f"{ports_count} selected")
    table.add_row("Timeout", f"{args.timeout}s")
    table.add_row("Concurrency", str(args.concurrency))
    table.add_row("Mode", mode)
    table.add_row("Banner Grab", banner_info)

    return Panel(table, title="[cyan]Session Info", border_style="cyan")

def make_results_table(results: list, is_stealth: bool) -> Panel:
    table = Table(expand=True, border_style="dim", box=None)
    table.add_column("Port", style="cyan", justify="right", width=6)
    table.add_column("State", style="bold green", width=6)
    table.add_column("Banner / Service", style="dim white")

    open_results = sorted((r for r in results if r.open), key=lambda r: r.port)
    
    if not open_results:
        table.add_row("-", "[red]CLOSED[/]", "No open ports found on selected range.")
    else:
        for r in open_results:
            banner_text = r.banner.strip()[:60] + "..." if hasattr(r, 'banner') and r.banner else "Unknown"
            if is_stealth:
                banner_text = "N/A (Stealth Mode)"
            table.add_row(str(r.port), "OPEN", banner_text)

    return Panel(
        table, 
        title="[red]Scan Results", 
        border_style="red",
        subtitle=f"[dim]Total Open: {len(open_results)}[/dim]"
    )

def make_footer(open_count: int, total_count: int, json_out: str | None) -> Panel:
    status = f"Scan Completed. Found [bold green]{open_count}[/] open ports out of [bold]{total_count}[/] scanned."
    if json_out:
        status += f"\nJSON report saved to: [bold white]{json_out}[/]"
        
    return Panel(Align.center(Text.from_markup(status)), border_style="green")

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Professional async port scanner",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    p.add_argument("target", nargs="?", default=None, metavar="TARGET", help="Hostname or IP address (optional)")
    p.add_argument("-p", "--ports", default="top", metavar="SPEC", help="e.g. 1-1024, 3306 (default: top common)")
    p.add_argument("--no-banner", action="store_false", dest="banner", help="Disable banner grabbing")
    p.add_argument("--timeout", type=float, default=0.8, metavar="SEC", help="TCP timeout in seconds [default: 0.8]")
    p.add_argument("--concurrency", type=int, default=400, metavar="N", help="Max parallel sockets [default: 400]")
    p.add_argument("--stealth", action="store_true", help="SYN half-open scan via Scapy (requires root)")
    p.add_argument("--json", dest="json_out", default=None, metavar="FILE", help="Write JSON results to FILE")
    return p

def main() -> None:
    args = build_parser().parse_args()

    if args.target:
        final_target = sanitize_target(args.target)
        if not final_target:
            console.print(f"[bold red][!] Alvo inválido fornecido:[/] {args.target}")
            sys.exit(1)
    else:
        final_target = get_interactive_target()

    if args.ports == "top":
        ports = TOP_COMMON
    else:
        try:
            ports = parse_ports(args.ports)
        except ValueError as exc:
            console.print(f"\n[bold red][!] Invalid port spec:[/] {exc}")
            sys.exit(1)

    if args.stealth:
        try:
            from .stealth_engine import StealthPortScanner
            scanner = StealthPortScanner(final_target, ports, args.timeout, args.concurrency)
        except ImportError as exc:
            console.print(f"[bold red][!] Stealth engine unavailable:[/] {exc}\n    pip install scapy")
            sys.exit(1)
        except PermissionError as exc:
            console.print(f"[bold red][!] Permission Error:[/] {exc}")
            sys.exit(1)
    else:
        scanner = AsyncPortScanner(final_target, ports, args.timeout, args.concurrency, args.banner)

    console.clear()
    results = []
    try:
        with console.status(f"[bold cyan]Scanning {final_target}... (this might take a moment)", spinner="bouncingBar"):
            results = asyncio.run(scanner.run())
    except KeyboardInterrupt:
        console.print("[bold red]\n[!] Scan aborted by user.[/]")
        sys.exit(130)

    open_results = [r for r in results if r.open]

    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=5)
    )
    layout["body"].split_row(
        Layout(name="left", ratio=1),
        Layout(name="right", ratio=2)
    )
    layout["left"].split_column(
        Layout(name="info", size=10),
        Layout(name="results")
    )

    layout["header"].update(make_header(final_target))
    layout["info"].update(make_session_info(args, len(ports), final_target))
    layout["results"].update(make_results_table(results, args.stealth))  
    layout["right"].update(AnimatedEye())                                
    layout["footer"].update(make_footer(len(open_results), len(ports), args.json_out))

    if args.json_out:
        try:
            with open(args.json_out, "w", encoding="utf-8") as fh:
                json.dump(AsyncPortScanner.to_dict(results), fh, ensure_ascii=False, indent=2)
        except OSError as exc:
            console.print(f"[bold red][!] Could not write JSON:[/] {exc}", style="stderr")

    try:
        with Live(layout, console=console, refresh_per_second=10, screen=True):
            while True:
                time.sleep(0.1)
    except KeyboardInterrupt:
        console.clear()
        console.print("[dim]Scanner session closed.[/]")
        sys.exit(0)

if __name__ == "__main__":
    main()