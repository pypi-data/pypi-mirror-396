#!/usr/bin/env python3
"""
Dars Package Manager (DPM) - CLI for downloading Dars UI components
"""

import os
import sys
import platform
import urllib.request
import argparse
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich import box

console = Console()


def getAppdataDir(app_name="dars"):
    system = platform.system()
    if system == "Windows":
        basedir = os.getenv("APPDATA") or os.path.expanduser("~\\AppData\\Roaming")
    elif system == "Darwin":
        basedir = os.path.expanduser("~/Library/Application Support")
    else:
        basedir = os.path.expanduser("~/.local/share")

    dars_dir = os.path.join(basedir, app_name, "dpm_components")
    os.makedirs(dars_dir, exist_ok=True)
    return dars_dir


class DarsPackageManager:
    def __init__(self, version: str = "1.0.0"):
        self.version = version

        self.repo_base = "https://raw.githubusercontent.com/ZtaMDev/dars-package-registry/CrystalMain/components"

        self.manifest_url = f"{self.repo_base}/manifest.json"

        self.local_dir = getAppdataDir("dars")

    def fetch_manifest(self):
        """Descarga y lee el archivo manifest.json desde GitHub"""
        try:
            with urllib.request.urlopen(self.manifest_url) as response:
                return json.load(response)
        except Exception as e:
            console.print(f"[red]Failed to fetch component list: {e}[/red]")
            return {}

    def list_components(self, search_query: str = None):
        manifest = self.fetch_manifest()
        if not manifest:
            return

        components = manifest.get("components", [])
        if search_query:
            components = [c for c in components if search_query.lower() in c["name"].lower()]

        if not components:
            console.print(f"[yellow]No components found matching '{search_query or ''}'.[/yellow]")
            return

        table = Table(
            title=f"[bold cyan]Available Dars Components[/bold cyan]",
            show_header=True,
            header_style="bold magenta",
            box=box.MINIMAL_DOUBLE_HEAD
        )
        table.add_column("Name", style="bold white")
        table.add_column("Description", style="dim")
        table.add_column("Size", justify="right")

        for comp in components:
            table.add_row(comp["name"], comp.get("description", "No description"), comp.get("size", "?"))

        console.print(table)

    def download_component(self, name: str):
        manifest = self.fetch_manifest()
        if not manifest:
            return

        components = manifest.get("components", [])
        target = next((c for c in components if c["name"].lower() == name.lower()), None)

        if not target:
            console.print(f"[red]Component '{name}' not found in repository.[/red]")
            return

        url = f"{self.repo_base}/{target['name']}"
        dest = os.path.join(self.local_dir, target["name"])

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(f"Downloading {target['name']}...", total=None)
            try:
                urllib.request.urlretrieve(url, dest)
                progress.update(task, completed=100)
                console.print(Panel.fit(
                    f"[green]✔ Component '{target['name']}' downloaded successfully![/green]\nSaved to: {dest}",
                    border_style="green"
                ))
            except Exception as e:
                console.print(f"[red]❌ Failed to download component: {e}[/red]")

    def interactive_mode(self):
        manifest = self.fetch_manifest()
        if not manifest:
            return

        components = manifest.get("components", [])
        if not components:
            console.print("[red]No components available.[/red]")
            return

        console.print(Panel(
            "[bold cyan]Dars Package Manager[/bold cyan]\nSelect a component to download or type to search:",
            border_style="cyan"
        ))

        while True:
            query = Prompt.ask("[bold green]Search (empty to list all, or type 'exit' to quit)[/bold green]")
            if query.lower() == "exit":
                break

            filtered = [c for c in components if query.lower() in c["name"].lower()] if query else components
            if not filtered:
                console.print("[yellow]No matching components.[/yellow]")
                continue

            table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE_HEAVY)
            table.add_column("Index", justify="center", style="cyan")
            table.add_column("Name", style="bold white")
            table.add_column("Description", style="dim")

            for i, comp in enumerate(filtered):
                table.add_row(str(i + 1), comp["name"], comp.get("description", "No description"))

            console.print(table)
            choice = Prompt.ask("Enter component index to download (or Enter to skip)", default="")
            if not choice.isdigit():
                continue

            idx = int(choice) - 1
            if 0 <= idx < len(filtered):
                self.download_component(filtered[idx]["name"])
            else:
                console.print("[red]Invalid index.[/red]")

def main():
    parser = argparse.ArgumentParser(description="Dars Package Manager CLI (DPM)")
    parser.add_argument("command", nargs="?", help="Command to execute (add/list)")
    parser.add_argument("argument", nargs="?", help="Component name or search term")
    args = parser.parse_args()

    dpm = DarsPackageManager()

    if args.command == "add" and args.argument:
        dpm.download_component(args.argument)
    elif args.command == "list":
        dpm.list_components(args.argument)
    else:
        dpm.interactive_mode()

if __name__ == "__main__":
    main()
