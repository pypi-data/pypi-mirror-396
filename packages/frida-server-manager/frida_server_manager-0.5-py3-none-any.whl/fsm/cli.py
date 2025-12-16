import sys
import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich import print as rich_print
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text

from fsm.core import (
    check_adb_connection as core_check_adb,
    install_frida_server as core_install,
    run_frida_server as core_run,
    list_frida_server as core_list,
    get_running_processes as core_ps,
    kill_frida_server as core_kill
)

app = typer.Typer(
    name="fsm",
    help="frida-server manager for Android devices",
    add_completion=False,
    rich_markup_mode="rich",
    # Ensure help option has -h short form
    context_settings={"help_option_names": ["--help", "-h"]}
)

console = Console()


def print_success(message: str):
    """Print success message with green color"""
    rich_print(f"[bold green]✓ {message}[/bold green]")


def print_error(message: str):
    """Print error message with red color"""
    rich_print(f"[bold red]✗ {message}[/bold red]")


def print_warning(message: str):
    """Print warning message with yellow color"""
    rich_print(f"[bold yellow]⚠ {message}[/bold yellow]")


def print_info(message: str):
    """Print info message with blue color"""
    rich_print(f"[bold blue]ℹ {message}[/bold blue]")


@app.command()
def check(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """Check ADB connection to devices"""
    try:
        # Import core function
        from fsm.core import run_command
        
        devices = None
        output = None
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(description="Checking ADB connection...", total=None)

            output = run_command('adb devices', verbose)

            if output is None:
                progress.update(task, completed=True)
                print_error("ADB is not installed or not in PATH")
                raise typer.Exit(1)

            # Check if there are any devices connected
            devices = [line for line in output.splitlines() if 'device' in line and not line.startswith('List of')]

            progress.update(task, completed=True)

        # Process results after progress bar ends
        if not devices:
            print_error("No devices connected via ADB")
            raise typer.Exit(1)

        print_success(f"{len(devices)} device(s) connected")

        # Create a rich table to display device information
        table = Table(title="Connected Devices")
        table.add_column("Serial Number", style="cyan", no_wrap=True)
        table.add_column("Model", style="green")
        table.add_column("Status", style="yellow")

        # Get device model for each connected device
        for i, device_line in enumerate(devices, 1):
            # Parse device serial number from the line
            parts = device_line.strip().split()
            if len(parts) >= 2:
                serial = parts[0]
                status = parts[1]
                
                # Get device model
                model_cmd = f"adb -s {serial} shell getprop ro.product.model"
                model_output = run_command(model_cmd, verbose)
                model = model_output.strip() if model_output else "Unknown"
                
                # Add to table
                table.add_row(serial, model, status)

        # Print the table
        console.print(table)

        if verbose:
            print_info("Device details:")
            for device in devices:
                print_info(f"  {device}")

    except Exception as e:
        print_error(f"Error checking ADB connection: {e}")
        raise typer.Exit(1)


@app.command()
def install(
    version: Optional[str] = typer.Argument(None, help="Specific version of frida-server to install"),
    repo: str = typer.Option("frida/frida", "--repo", "-r", help="Custom GitHub repository (owner/repo format)"),
    keep_name: bool = typer.Option(False, "--keep-name", "-k", help="Keep the original name when installing"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Custom name for frida-server on the device"),
    url: Optional[str] = typer.Option(None, "--url", "-u", help="Custom URL to download frida-server from (supports xz, gz, tar.gz formats)"),
    proxy: Optional[str] = typer.Option(None, "--proxy", "-p", help="Proxy server to use for downloading frida-server"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """Install frida-server on the device"""
    try:
        result = None
        
        # Check ADB connection first, outside the progress bar
        from fsm.core import check_adb_connection
        check_adb_connection(verbose)
        
        # Show progress bar while running the installation
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(description="Installing frida-server...", total=None)
            
            # Run the actual installation
            try:
                result = core_install(version, verbose, repo, keep_name, name, url, proxy)
                progress.update(task, completed=True)
            except Exception as e:
                # Update progress bar before raising exception
                progress.update(task, completed=True)
                raise
        
        # Print success messages after progress bar has finished
        print_success(f"Successfully installed frida-server")
        print_info(f"Location: {result}")

        if version:
            print_info(f"To run this version: fsm run -V {version}")

    except SystemExit as e:
        raise typer.Exit(e.code)
    except Exception as e:
        print_error(f"Error installing frida-server: {e}")
        raise typer.Exit(1)


@app.command()
def run(
    dir: Optional[str] = typer.Option(None, "--dir", "-d", help="Custom directory to run frida-server from"),
    params: Optional[str] = typer.Option(None, "--params", "-p", help="Additional parameters for frida-server"),
    version: Optional[str] = typer.Option(None, "--version", "-V", help="Specific version of frida-server to run"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Custom name of frida-server to run"),
    force: bool = typer.Option(False, "--force", "-f", help="Force run the specified version, stop any existing frida-server processes first"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """Run frida-server on the device"""
    try:
        success = False
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(description="Starting frida-server...", total=None)

            # Run frida-server
            success = core_run(dir, params, verbose, version, name, force)

            progress.update(task, completed=True)
        
        # Print success message outside the Progress context manager
        if success:
            if version:
                print_success(f"frida-server version {version} is running")
            else:
                print_success("frida-server is running")

    except SystemExit as e:
        raise typer.Exit(e.code)
    except Exception as e:
        print_error(f"Error running frida-server: {e}")
        raise typer.Exit(1)


@app.command()
def list(
    dir: Optional[str] = typer.Option(None, "--dir", "-d", help="Custom directory to list frida-server files from"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Filter by specific frida-server name"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """List frida-server files on the device and show their versions"""
    try:
        # Get the list of files first with progress bar
        from fsm.core import run_command, get_frida_server_version, DEFAULT_INSTALL_DIR
        
        server_dir = dir if dir else DEFAULT_INSTALL_DIR
        files = []
            
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(description="Listing frida-server files...", total=None)

            # Build the command with optional name filter
            if name:
                # If name is provided, search for that specific file
                output = run_command(f"adb shell ls {server_dir}/{name} 2>/dev/null || echo 'Not found'", verbose)
                # Check if the file exists
                if output.strip() == 'Not found' or 'No such file or directory' in output:
                    progress.update(task, completed=True)
                    print_warning(f"No frida-server file found with name '{name}' in {server_dir}")
                    return
                # File exists, use its name
                files = [name]
                # Update progress bar to completed
                progress.update(task, completed=True)
            else:
                # Otherwise list all frida-server files
                output = run_command(f"adb shell ls {server_dir} | grep frida-server", verbose)
                
                progress.update(task, completed=True)
                
                if not output:
                    print_warning(f"No frida-server files found in {server_dir}")
                    return
                
                # Process the files and get their versions
                files = output.strip().split('\n')
                # Sort files alphabetically by filename
                files.sort()

        # Create a rich table after progress bar is done
        table = Table(title=f"Frida-Server Files in {server_dir}" + (f" (Filtered by: {name})" if name else ""))
        table.add_column("Filename", style="cyan", no_wrap=True)
        table.add_column("Version", style="green")

        # Process each file and get its version
        for file in files:
            filename = file.strip()
            remote_path = f"{server_dir}/{filename}"
            version = get_frida_server_version(remote_path, verbose)
            table.add_row(filename, version if version else "Unknown")

        console.print(table)
        # Print success message
        print_success(f"Found {len(files)} frida-server file(s) in {server_dir}")

    except Exception as e:
        print_error(f"Error listing frida-server files: {e}")
        raise typer.Exit(1)


@app.command()
def ps(
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Filter processes by name"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """List running processes on the device"""
    try:
        # Get running processes
        from fsm.core import run_command

        search_name = name if name else "frida-server"
        cmd = f"adb shell ps -A | grep {search_name}"
        
        # Use progress bar only for command execution
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(description="Checking running processes...", total=None)
            output = run_command(cmd, verbose)
            progress.update(task, completed=True)

        # Process output after progress bar ends
        if not output:
            print_warning(f"No running processes found matching '{search_name}'")
            return

        # Process the output - remove duplicates
        lines = output.strip().split('\n')
        # Deduplicate lines while preserving order
        seen = set()
        unique_lines = []
        for line in lines:
            stripped_line = line.strip()
            if stripped_line and stripped_line not in seen:
                seen.add(stripped_line)
                unique_lines.append(stripped_line)

        # Create a rich table
        table = Table(title=f"Running Processes matching '{search_name}'")
        table.add_column("PID", style="cyan", no_wrap=True)
        table.add_column("User", style="yellow")
        table.add_column("Memory", style="blue")
        table.add_column("Command", style="green")

        for line in unique_lines:
            parts = line.strip().split()
            if len(parts) >= 9:  # Need at least 9 parts to include command
                pid = parts[1]
                user = parts[0]
                memory = parts[4]
                command = ' '.join(parts[8:])  # Command starts from 9th field (index 8), not 8th field
                table.add_row(pid, user, memory, command)

        console.print(table)

    except Exception as e:
        print_error(f"Error checking processes: {e}")
        raise typer.Exit(1)


@app.command()
def kill(
    pid: Optional[str] = typer.Option(None, "--pid", "-p", help="Specific PID of process to kill"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Process name to kill"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """Kill frida-server process(es) on the device"""
    try:
        # Check ADB connection first, outside the progress bar
        from fsm.core import check_adb_connection
        check_adb_connection(verbose)
        
        result = None
        
        # Show progress bar while killing processes
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(description="Killing processes...", total=None)

            # Kill processes
            result = core_kill(pid, verbose, name)

            progress.update(task, completed=True)
        
        # Print result after progress bar ends
        if result:
            if "Success:" in result["message"]:
                print_success(result["message"])
            elif "Warning:" in result["message"]:
                print_warning(result["message"])
            elif "Error:" in result["message"]:
                print_error(result["message"])

    except SystemExit as e:
        raise typer.Exit(e.code)
    except Exception as e:
        print_error(f"Error killing processes: {e}")
        raise typer.Exit(1)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """
    frida-server manager for Android devices

    When called without a command, checks ADB connection.
    """
    if ctx.invoked_subcommand is None:
        # No command provided, check ADB connection
        check(verbose)


if __name__ == "__main__":
    app()