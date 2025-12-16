import sys
import os
import urllib.request
import json
import lzma
import tempfile
import shutil
from pathlib import Path
import subprocess
from rich import print as rich_print

# GitHub API URL for Frida releases
GITHUB_RELEASES_URL = "https://api.github.com/repos/frida/frida/releases"
DEFAULT_INSTALL_DIR = '/data/local/tmp'


def run_command(cmd, verbose=False, return_error=False):
    """Run a shell command and return the output"""
    if verbose:
        rich_print(f"Running command: {cmd}")

    try:
        result = subprocess.run(cmd, shell=True, check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True)

        if return_error:
            if verbose:
                rich_print(f"Command output: {result.stderr}")
            return result.stderr
        else:
            if verbose:
                rich_print(f"Command output: {result.stdout}")
            return result.stdout
    except subprocess.CalledProcessError as e:
        if verbose:
            rich_print(f"Command failed: {e.stderr}")
        return None


def check_adb_connection(verbose=False):
    """Check if ADB is connected to any device"""
    rich_print("Checking ADB connection...")
    output = run_command('adb devices', verbose)

    if output is None:
        rich_print("Error: ADB is not installed or not in PATH")
        sys.exit(1)

    # Check if there are any devices connected
    devices = [line for line in output.splitlines() if 'device' in line and not line.startswith('List of')]

    if not devices:
        rich_print("Error: No devices connected via ADB")
        sys.exit(1)

    rich_print(f"Success: {len(devices)} device(s) connected")
    if verbose:
        for device in devices:
            rich_print(f"  {device}")


def get_latest_frida_version(repo="frida/frida", verbose=False, proxy=None):
    """Get the latest version of frida from GitHub"""
    if verbose:
        rich_print(f"Fetching latest version from GitHub repository: {repo}")

    try:
        url = f"https://api.github.com/repos/{repo}/releases/latest"
        
        # Create opener with proxy if provided
        if proxy:
            if verbose:
                rich_print(f"Using proxy: {proxy}")
            proxy_handler = urllib.request.ProxyHandler({'https': proxy, 'http': proxy})
            opener = urllib.request.build_opener(proxy_handler)
            urllib.request.install_opener(opener)
        
        # Set a timeout for the request
        with urllib.request.urlopen(url, timeout=10) as response:
            # Check if the request was successful
            if response.status != 200:
                raise Exception(f"HTTP error {response.status}")
            # Read and parse the response
            data = json.loads(response.read().decode())
            latest_version = data["tag_name"].strip('v')  # Remove 'v' prefix if present
            if verbose:
                rich_print(f"Latest version: {latest_version}")
            return latest_version
    except Exception as e:
        if verbose:
            rich_print(f"Error fetching latest version: {e}")
        return None


def get_frida_server_arch(verbose=False):
    """Determine the architecture of the Android device for frida-server"""
    if verbose:
        rich_print("Determining Android device architecture...")

    # Get the architecture info from the device
    arch_info = run_command("adb shell getprop ro.product.cpu.abi", verbose)

    if not arch_info:
        rich_print("Error: Could not determine device architecture")
        sys.exit(1)

    arch_info = arch_info.strip()

    # Map Android architecture to frida-server architecture
    if 'arm64' in arch_info:
        frida_arch = "android-arm64"
    elif 'armeabi' in arch_info:
        frida_arch = "android-arm"
    elif 'x86_64' in arch_info:
        frida_arch = "android-x86_64"
    elif 'x86' in arch_info:
        frida_arch = "android-x86"
    else:
        rich_print(f"Error: Unsupported architecture: {arch_info}")
        sys.exit(1)

    if verbose:
        rich_print(f"Device architecture: {arch_info} -> Frida architecture: {frida_arch}")

    return frida_arch


def download_frida_server(version=None, repo="frida/frida", verbose=False, url=None, proxy=None):
    """Download frida-server for Android using temporary files"""
    # Get the latest version if not specified and no URL provided
    if not url and not version:
        version = get_latest_frida_version(repo, verbose, proxy)
        if not version:
            rich_print("Error: Could not determine the latest version")
            sys.exit(1)

    # Determine the architecture if not using URL
    if not url:
        frida_arch = get_frida_server_arch(verbose)
        download_url = f"https://github.com/{repo}/releases/download/{version}/frida-server-{version}-{frida_arch}.xz"
    else:
        download_url = url

    if verbose:
        rich_print(f"Downloading from {download_url}")

    try:
        # Download the compressed file
        # Set headers to mimic a browser to avoid GitHub API rate limiting
        req = urllib.request.Request(download_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # Use tempfile to handle temporary files
        # Create a temporary directory for our files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Determine filename based on URL
            if url:
                filename = download_url.split('/')[-1]
            else:
                filename = f"frida-server-{version}-{frida_arch}.xz"
            
            # Path for compressed file
            compressed_file = temp_path / filename
            
            # Save the downloaded content
            # For large files, we'll read in chunks to avoid memory issues
            
            # Create opener with proxy if provided
            if proxy:
                if verbose:
                    rich_print(f"Using proxy: {proxy}")
                proxy_handler = urllib.request.ProxyHandler({'https': proxy, 'http': proxy})
                opener = urllib.request.build_opener(proxy_handler)
                urllib.request.install_opener(opener)
            
            with urllib.request.urlopen(req, timeout=30) as response:
                # Check if the request was successful
                if response.status != 200:
                    raise Exception(f"HTTP error {response.status}")
                
                with open(compressed_file, 'wb') as f:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)

            if verbose:
                rich_print(f"Download completed: {compressed_file}")

            # Determine file extension and use appropriate extraction method
            file_extension = compressed_file.suffix.lower()
            
            # Create a temporary file for the extracted content
            # We need to close it here and reopen because we need to change its permissions
            extracted_temp = tempfile.NamedTemporaryFile(delete=False, dir=temp_dir)
            extracted_temp.close()
            extracted_file = Path(extracted_temp.name)
            
            if verbose:
                rich_print(f"Extracting to {extracted_file}")

            if file_extension == '.xz':
                # Extract .xz file
                with lzma.open(compressed_file, 'rb') as f_in:
                    with open(extracted_file, 'wb') as f_out:
                        f_out.write(f_in.read())
            elif file_extension == '.gz':
                # Extract .gz file
                import gzip
                with gzip.open(compressed_file, 'rb') as f_in:
                    with open(extracted_file, 'wb') as f_out:
                        f_out.write(f_in.read())
            elif file_extension == '.tar' and str(compressed_file).endswith('.tar.gz'):
                # Extract .tar.gz file
                import tarfile
                with tarfile.open(compressed_file, 'r:gz') as tar:
                    # Find the first executable file in the tar archive
                    for member in tar.getmembers():
                        if member.isfile():
                            # Extract to our temporary file
                            tar.extract(member, temp_dir)
                            # Move the extracted file to our named temporary file
                            os.rename(temp_path / member.name, extracted_file)
                            break
            else:
                # If it's not a recognized compressed format, assume it's already extracted
                # Just copy the file
                import shutil
                shutil.copy2(compressed_file, extracted_file)

            if verbose:
                rich_print(f"Extraction completed: {extracted_file}")

            # Make the extracted file executable
            os.chmod(extracted_file, 0o755)
            if verbose:
                rich_print(f"Made the file executable")

            # The temporary directory will be automatically deleted when exiting the context manager
            # But we need to return the path to the extracted file which will be deleted
            # So we need to create a final temporary file outside the context manager
            # to return to the caller
            final_temp = tempfile.NamedTemporaryFile(delete=False)
            final_temp.close()
            
            # Copy the extracted file to the final temporary file
            import shutil
            shutil.copy2(extracted_file, final_temp.name)
            os.chmod(final_temp.name, 0o755)
            
            if verbose:
                rich_print(f"Created final temporary file: {final_temp.name}")
            
            # Return the path to the final temporary file
            # The caller is responsible for deleting this file when done
            return final_temp.name
            
    except Exception as e:
        if verbose:
            rich_print(f"Error downloading frida-server: {e}")
        error_msg = f"Error: Could not download frida-server from {download_url}"
        rich_print(error_msg)
        raise Exception(error_msg)


def install_frida_server(version=None, verbose=False, repo="frida/frida", keep_name=False, custom_name=None, url=None, proxy=None):
    """Install frida-server on the Android device"""
    # Download frida-server
    local_path = None
    try:
        local_path = download_frida_server(version, repo, verbose, url, proxy)

        # Determine the remote path
        if version and not keep_name and not custom_name:
            remote_path = f"{DEFAULT_INSTALL_DIR}/frida-server-{version}"
        elif custom_name:
            remote_path = f"{DEFAULT_INSTALL_DIR}/{custom_name}"
        else:
            remote_path = f"{DEFAULT_INSTALL_DIR}/frida-server"

        if verbose:
            rich_print(f"Installing frida-server to {remote_path}")

        # Push the file to the device
        output = run_command(f"adb push {local_path} {remote_path}", verbose, return_error=False)
        if not output or "1 file pushed" not in output:
            rich_print("Error: Failed to push frida-server to the device")
            sys.exit(1)

        # Make the file executable on the device
        output = run_command(f"adb shell chmod 755 {remote_path}", verbose)

        if verbose:
            rich_print("Successfully installed frida-server")

        return remote_path
    except Exception as e:
        # Re-raise the exception after cleanup
        raise
    finally:
        # Always clean up the temporary file
        if local_path and os.path.exists(local_path):
            try:
                os.unlink(local_path)
                if verbose:
                    rich_print(f"Cleaned up temporary file: {local_path}")
            except Exception as cleanup_error:
                # Just log the cleanup error but don't fail the installation
                if verbose:
                    rich_print(f"Warning: Could not clean up temporary file: {cleanup_error}")


def get_frida_server_version(remote_path, verbose=False):
    """Get the version of frida-server from the device"""
    if verbose:
        rich_print(f"Checking version of frida-server at {remote_path}")

    # First try: Run the file with --version
    version_output = run_command(f"adb shell {remote_path} --version", verbose)
    if version_output:
        return version_output.strip()
    
    # Second try: Check if file exists and is executable
    check_output = run_command(f"adb shell ls -la {remote_path}", verbose)
    if check_output and '-rwx' in check_output:
        # File exists and is executable, try alternative version check
        try:
            # Try to get version by parsing file properties or name pattern
            # Check if filename contains version pattern
            filename = os.path.basename(remote_path)
            import re
            # Look for version patterns like "16.1.4" in filename
            version_match = re.search(r'\d+\.\d+\.\d+', filename)
            if version_match:
                return version_match.group()
        except Exception as e:
            if verbose:
                rich_print(f"Error in fallback version detection: {e}")
    
    if verbose:
        rich_print("Could not determine frida-server version")
    return None


def run_frida_server(custom_dir=None, custom_params=None, verbose=False, version=None, name=None, force=False):
    """Run frida-server on the Android device"""
    if verbose:
        rich_print(f"DEBUG: run_frida_server called with version={version}, name={name}")
    
    check_adb_connection(verbose)

    # Determine the directory to use
    server_dir = custom_dir if custom_dir else DEFAULT_INSTALL_DIR

    # Determine the server path
    server_path = None
    target_version = None
    target_name = None
    
    if verbose:
        rich_print(f"DEBUG: Server directory: {server_dir}")
        rich_print(f"DEBUG: Initial server_path: {server_path}")

    # If name is specified, use that specific name
    if name:
        server_path = f"{server_dir}/{name}"
        target_name = name
        # Extract version from name if possible
        import re
        version_match = re.search(r'\d+\.\d+\.\d+', name)
        if version_match:
            target_version = version_match.group()
    # If version is specified, find the matching file - ALWAYS execute this when version is provided
    elif version:
        if verbose:
            rich_print(f"DEBUG: Version specified: {version}")
            rich_print(f"DEBUG: Server directory: {server_dir}")
        
        # List all frida-server files in the directory
        output = run_command(f"adb shell ls {server_dir} | grep frida-server", verbose)
        if not output:
            rich_print(f"Error: No frida-server found in {server_dir}")
            rich_print("Please install it first")
            sys.exit(1)
        
        if verbose:
            rich_print(f"DEBUG: Found files: {output}")
        
        # Find the file that contains the version number
        import re
        files = output.strip().split('\n')
        matching_file = None
        
        # First try: Find file with version in filename
        for file in files:
            filename = file.strip()
            if re.search(rf'{re.escape(version)}', filename):
                matching_file = filename
                break
        
        # Second try: If no file has version in filename, check each file's actual version
        if not matching_file:
            for file in files:
                filename = file.strip()
                remote_path = f"{server_dir}/{filename}"
                file_version = get_frida_server_version(remote_path, verbose)
                # Extract just the version number from the output (e.g., "17.4.0" from "Frida 17.4.0")
                if file_version:
                    import re
                    version_match = re.search(r'\d+\.\d+\.\d+', file_version)
                    if version_match and version_match.group() == version:
                        matching_file = filename
                        break
        
        if not matching_file:
            rich_print(f"Error: No frida-server found with version {version} in {server_dir}")
            rich_print("Please check the installed versions with: fsm list")
            sys.exit(1)
        
        server_path = f"{server_dir}/{matching_file}"
        target_version = version
        target_name = matching_file
        
        if verbose:
            rich_print(f"DEBUG: Found matching file: {matching_file}")
            rich_print(f"DEBUG: Server path set to: {server_path}")
    elif custom_params and custom_params.startswith('/'):
        # If custom_params starts with '/', treat it as a full path
        server_path = custom_params
        target_name = os.path.basename(server_path)
        # Extract version from name if possible
        import re
        version_match = re.search(r'\d+\.\d+\.\d+', target_name)
        if version_match:
            target_version = version_match.group()
    else:
        # First check if any frida-server is already running
        verify_cmd = "adb shell ps | grep frida-server"
        verify_output = run_command(verify_cmd, verbose)
        if verify_output:
            # If any frida-server is running, use it
            if verbose:
                rich_print("frida-server is already running")
            return True
        
        # No frida-server is running, check if any exists in the directory
        output = run_command(f"adb shell ls {server_dir} | grep frida-server", verbose)
        if not output:
            rich_print(f"Error: No frida-server found in {server_dir}")
            rich_print("Please install it first")
            sys.exit(1)

        # Use the first frida-server file found
        files = output.strip().split('\n')
        server_path = f"{server_dir}/{files[0].split()[-1]}"
        target_name = os.path.basename(server_path)
        # Extract version from name if possible
        import re
        version_match = re.search(r'\d+\.\d+\.\d+', target_name)
        if version_match:
            target_version = version_match.group()

    # Check if any frida-server is running
    verify_cmd = "adb shell ps | grep frida-server"
    verify_output = run_command(verify_cmd, verbose)
    
    if verify_output and not force:
        # Clean up duplicate lines in output
        lines = [line.strip() for line in verify_output.strip().split('\n') if line.strip()]
        unique_lines = list(dict.fromkeys(lines))
        
        # Check if the exact version we want is already running, and no other versions
        same_version_running = False
        multiple_versions = False
        
        for process in unique_lines:
            if target_version and target_version in process:
                same_version_running = True
            else:
                multiple_versions = True
        
        # If only our target version is running, return success
        if same_version_running and not multiple_versions:
            if verbose:
                rich_print(f"frida-server version {target_version} is already running")
            return True
        
        # Otherwise, we need to stop all processes and start fresh
        if verbose:
            rich_print(f"Found {len(unique_lines)} frida-server processes, will restart with version {target_version}")
    elif force:
        if verbose:
            rich_print("Force option specified, will stop all existing processes and start the requested version")
    
    # Now check if the file exists
    output = run_command(f'adb shell ls {server_path}', verbose)
    if not output or 'No such file or directory' in output:
        if version:
            rich_print(f"Error: frida-server version {version} not found at {server_path}")
        elif name:
            rich_print(f"Error: frida-server with name {name} not found at {server_path}")
        else:
            rich_print(f"Error: frida-server not found at {server_path}")
        rich_print("Please install it first")
        sys.exit(1)

    # Construct the command to run frida-server
    cmd = f"adb shell su -c 'nohup {server_path}"
    if custom_params and not custom_params.startswith('/'):
        cmd += f" {custom_params}"
    cmd += " < /dev/null > /dev/null 2>&1 &'"

    if verbose:
        rich_print(f"Running frida-server with command: {cmd}")

    # Stop any existing frida-server processes first
    if verbose:
        rich_print("Stopping existing frida-server processes...")
    
    # Use multiple methods to ensure all frida-server processes are stopped
    stop_commands = [
        "adb shell su -c 'pkill -f frida-server'",
        "adb shell su -c 'killall -9 frida-server'",
        "adb shell su -c 'pkill -9 -f frida-server'"  # Force kill with -9
    ]
    
    for stop_cmd in stop_commands:
        # Run each stop command but don't check for errors
        subprocess.run(stop_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True)
    
    # Longer delay to ensure all processes are completely stopped
    import time
    time.sleep(1.5)

    # Run frida-server - don't wait for output since it's backgrounded
    try:
        # The start command should use check=True to catch errors
        subprocess.run(cmd, shell=True, check=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        rich_print(f"Error starting frida-server: {e}")
        sys.exit(1)

    # Small delay to allow process to start
    time.sleep(2)  # Increased delay for more reliable startup

    # Verify it's running
    verify_cmd = "adb shell ps | grep frida-server"
    verify_output = run_command(verify_cmd, verbose)

    # Clean up duplicate lines in output
    if verify_output:
        # Split by lines, remove empty lines, then deduplicate
        lines = [line.strip() for line in verify_output.strip().split('\n') if line.strip()]
        unique_lines = list(dict.fromkeys(lines))
        verify_output = '\n'.join(unique_lines)

    if not verify_output:
        rich_print("Warning: Could not verify that frida-server is running")
        rich_print("You may need to start it manually with:\n  adb shell su -c './frida-server'")
        return False
    
    if verbose:
        rich_print(verify_output)
    
    return True


def list_frida_server(custom_dir=None, verbose=False):
    """List frida-server files in the specified directory and show their versions"""
    check_adb_connection(verbose)

    # Determine the directory to use
    server_dir = custom_dir if custom_dir else DEFAULT_INSTALL_DIR

    if verbose:
        rich_print(f"Listing frida-server files in {server_dir}")

    # List all files in the directory containing 'frida-server'
    output = run_command(f"adb shell ls {server_dir} | grep frida-server", verbose)

    if not output:
        rich_print(f"No frida-server files found in {server_dir}")
        sys.exit(0)

    # Process the files and get their versions
    files = output.strip().split('\n')
    rich_print(f"Found {len(files)} frida-server file(s) in {server_dir}:")
    rich_print("=" * 80)
    rich_print(f"{'Filename':<40} {'Version':<40}")
    rich_print("=" * 80)

    # Process each file and get its version
    for file in files:
        filename = file.strip()
        remote_path = f"{server_dir}/{filename}"
        version = get_frida_server_version(remote_path, verbose)
        rich_print(f"{filename:<40} {version if version else 'Unknown':<40}")


def get_running_processes(verbose=False, process_name=None):
    """Check and list running processes on the Android device"""
    check_adb_connection(verbose)
    
    # Use custom process name if provided, default to frida-server
    search_name = process_name if process_name else "frida-server"
    
    # Command to list all running processes with more details
    cmd = f"adb shell ps -A | grep {search_name}"
    
    if verbose:
        rich_print(f"Checking for running processes with command: {cmd}")
    
    output = run_command(cmd, verbose)
    
    if not output:
        rich_print(f"No running processes found matching '{search_name}'")
        return []
    
    # Process the output and extract process information
    processes = []
    lines = output.strip().split('\n')
    
    rich_print(f"Running processes matching '{search_name}':")
    rich_print("=" * 80)
    rich_print(f"{'PID':<10} {'User':<15} {'Memory':<10} {'Command':<40}")
    rich_print("=" * 80)
    
    for line in lines:
            parts = line.strip().split()
            if len(parts) < 9:
                continue
            
            # Extract process information
            pid = parts[1]
            user = parts[0]
            memory = parts[4]
            command = ' '.join(parts[8:])  # Command starts from 9th field (index 8)
            
            # Store process info for potential use
            processes.append({
                'pid': pid,
                'user': user,
                'memory': memory,
                'command': command
            })
            
            # Print formatted process info
            rich_print(f"{pid:<10} {user:<15} {memory:<10} {command:<40}")
    
    rich_print("=" * 80)
    return processes


def get_running_frida_servers(verbose=False):
    """Check and list running frida-server processes on the Android device (backward compatibility)"""
    return get_running_processes(verbose, "frida-server")


def kill_frida_server(pid=None, verbose=False, name=None):
    """Kill frida-server process on the Android device"""
    result = {
        "success": True,
        "message": "",
        "warning": False
    }
    
    if name:
        # Kill processes by name
        cmd = f"adb shell su -c 'pkill -f {name} || killall -9 {name}'"
        if verbose:
            rich_print(f"Killing processes with name '{name}'")
        
        output = run_command(cmd, verbose)
        
        # Verify no processes with the name are running
        verify_cmd = f"adb shell ps -A | grep {name}"
        verify_output = run_command(verify_cmd, verbose)
        
        if not verify_output:
            result["message"] = f"Success: All processes with name '{name}' have been killed"
        else:
            result["message"] = f"Warning: Some processes with name '{name}' might still be running"
            result["warning"] = True
            if verbose:
                result["message"] += f"\n{verify_output}"
    elif pid:
        # Kill specific process by PID
        cmd = f"adb shell su -c 'kill -9 {pid}'"
        if verbose:
            rich_print(f"Killing frida-server process with PID {pid}")
        
        output = run_command(cmd, verbose)
        
        # Verify the process is killed
        verify_cmd = f"adb shell ps -p {pid}"
        verify_output = run_command(verify_cmd, verbose)
        
        if not verify_output or "No such process" in verify_output:
            result["message"] = f"Success: frida-server process with PID {pid} has been killed"
        else:
            result["message"] = f"Error: Failed to kill frida-server process with PID {pid}"
            result["success"] = False
    else:
        # Kill all frida-server processes
        cmd = "adb shell su -c 'pkill -f frida-server || killall -9 frida-server'"
        if verbose:
            rich_print("Killing all running frida-server processes")
        
        output = run_command(cmd, verbose)
        
        # Verify no frida-server processes are running
        verify_cmd = "adb shell ps -A | grep frida-server"
        verify_output = run_command(verify_cmd, verbose)
        
        if not verify_output:
            result["message"] = "Success: All frida-server processes have been killed"
        else:
            result["message"] = "Warning: Some frida-server processes might still be running"
            result["warning"] = True
            if verbose:
                result["message"] += f"\n{verify_output}"
    
    return result
