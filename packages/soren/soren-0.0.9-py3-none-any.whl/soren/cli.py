"""
Soren CLI - Command-line interface for Soren AI evaluation framework
"""
import boto3
from botocore.exceptions import ClientError
import yaml
import argparse
import dotenv
import sys
import os
import subprocess
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from . import __version__
from .client import SorenClient
from .config import SorenConfig
from .validation import build_manifest_entry

dotenv.load_dotenv()

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)



BUCKET = os.environ.get('S3_BUCKET')

def validate_yaml_config(yaml_data: dict) -> tuple:
    """
    Validate YAML configuration has required fields and proper values.

    This performs client-side validation before sending to the backend,
    providing faster feedback to users about configuration errors.

    Required fields:
        - cmd: The command to execute (must be non-empty)
        - run_name: Display name for the evaluation run (must be non-empty)

    Args:
        yaml_data: Parsed YAML configuration dictionary

    Returns:
        tuple: (is_valid: bool, error_message: str)
            - If valid: (True, "")
            - If invalid: (False, "descriptive error message")
    """
    # Backward compatibility: allow legacy 'name' by mapping to 'run_name'
    if "run_name" not in yaml_data and "name" in yaml_data:
        yaml_data["run_name"] = yaml_data.get("name")

    # Check required field: cmd
    if "cmd" not in yaml_data:
        return False, "YAML configuration must contain 'cmd' field"

    # Check required field: run_name
    if "run_name" not in yaml_data:
        return False, "YAML configuration must contain 'run_name' field (or legacy 'name')"

    # New: Check required field: project_name
    if "project_name" not in yaml_data:
        return False, "YAML configuration must contain 'project_name' field"

    # Validate cmd is not empty
    cmd_value = yaml_data["cmd"]
    if not cmd_value or (isinstance(cmd_value, str) and not cmd_value.strip()):
        return False, "Field 'cmd' cannot be empty"

    # Validate run_name is not empty
    run_name_value = yaml_data["run_name"]
    if not run_name_value or (isinstance(run_name_value, str) and not run_name_value.strip()):
        return False, "Field 'run_name' cannot be empty"

    # Validate project_name is not empty
    project_name_value = yaml_data["project_name"]
    if not project_name_value or (isinstance(project_name_value, str) and not project_name_value.strip()):
        return False, "Field 'project_name' cannot be empty"

    # All validations passed
    return True, ""


def handle_login(args):
    """Handle the login command"""
    config = SorenConfig()

    api_key = args.SOREN_API_KEY or input("Enter your Soren API key: ")
    try:
        # Authenticate with backend
        print("Authenticating with backend...")
        client = SorenClient(base_url=config.get_api_url())
        print("API key: ", api_key)
        response = client.login(api_key)

        # Store API key locally
        api_key = response.get('access_token')
        if api_key:
            config.set_api_key(api_key)
            print("✓ Successfully logged in!")
            print(f"API key stored in {config.config_file}")
        else:
            print("✗ Login failed: No API key received")
            sys.exit(1)

    except Exception as e:
        print(f"✗ Login failed: {e}")
        sys.exit(1)


def handle_run(args):
    """Handle the run command"""

    """
    config-path: The path to the config file
    - This config file is a YAML file that contains the necessary configs for run
 
    Pseudocode:
    1. API is parsed to validate each run.
    2. Reads the YAML configuration file for each of the necessary toggles + other for UI.
    3. Spawns their CLI and commands with these toggles.
    4. This creates a new run in my frontend (running)
    5. After it is done, it pulls from the output directory and outputs to backend and my UI.
    6. View on UI
    """
    config = SorenConfig()
    api_key = config.get_api_key()
    
    if not api_key:
        print("✗ Not logged in. Run 'soren login' first.")
        sys.exit(1)

    print("API key: ", api_key)
    print("Config path: ", args.config_path)
    
    # Read the YAML configuration file (user device)
    try:
        with open(args.config_path, "r") as f:
            yaml_data = yaml.safe_load(f)

        print("YAML data: ", yaml_data)

        # Print for debugging purposes
        print("\n=== YAML Configuration ===")
        print(yaml.dump(yaml_data, default_flow_style=False))
        print("=" * 26 + "\n")

    except FileNotFoundError:
        print(f"✗ Error: Config file not found at: {args.config_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"✗ Error: Invalid YAML format: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error reading config file: {e}")
        sys.exit(1)

    # Validate YAML configuration
    print("=== Validating Configuration ===")
    is_valid, error_msg = validate_yaml_config(yaml_data)
    if not is_valid:
        print(f"✗ Invalid YAML configuration: {error_msg}")
        print("\nRequired fields:")
        print("  - cmd: The command to execute")
        print("  - name: Display name for the run")
        sys.exit(1)
    print("✓ Configuration validated successfully\n")

    # Build command from config
    print("\n=== Building Command ===")
    try:
        command = yaml_data.get("cmd")
        print(f"Command: {command}\n")
    except Exception as e:
        print(f"✗ Error building command: {e}")
        sys.exit(1)
    
    # Create run in backend
    try:
        client = SorenClient(api_key=api_key, base_url=config.get_api_url())
        
        print("Creating a new evaluation run...")
        run = client.create_run(yaml_config=yaml_data)
        run_id = run.get('run_id')
        experiment_id = run.get('experiment_id') or yaml_data.get("experiment_id") or yaml_data.get("experiment-id")
        
        print(f"✓ Run created: {run_id}")
        if experiment_id:
            print(f"Experiment ID: {experiment_id}")
        else:
            print("⚠ No experiment_id returned; experiment manifest updates will be skipped.")
        
    except Exception as e:
        print(f"✗ Failed to create run: {e}")
        sys.exit(1)
    
    # Determine working directory
    working_dir = yaml_data.get("working-directory")
    if not working_dir:
        # Default to directory containing the YAML config file
        working_dir = os.path.dirname(os.path.abspath(args.config_path))
    
    print(f"Working directory: {working_dir}")
    
    # Validate working directory exists
    if not os.path.isdir(working_dir):
        print(f"✗ Error: Working directory does not exist: {working_dir}")
        sys.exit(1)
    
    # Execute command locally
    print("\n=== Executing Command ===")
    print(f"Starting execution at {datetime.now()}")
    print("-" * 50)
    print()
    
    # Execute the command locally (run scripts on user device)
    result = execute_command(command=command, working_dir=working_dir)
    
    print()
    print("-" * 50)
    
    if result["success"]:
        print(f"✓ Command completed successfully!")
        print(f"Exit code: {result['exit_code']}")

        # UPDATE FRONTEND WITH THE RESULT (from In Progress to --> Done)
        client.update_run(
            run_id=run_id,
            status="completed"
            )

        # Support both "output-dir" (hyphenated) and "output_dir" (underscored)
        output_directory = yaml_data.get("output-dir") or yaml_data.get("output_dir")
        if output_directory:
            print(f"\n=== Retrieving Output ===")

            # Resolve to absolute path using working_dir as base when needed
            if not os.path.isabs(output_directory):
                output_directory = os.path.abspath(os.path.join(working_dir, output_directory))
            else:
                output_directory = os.path.abspath(output_directory)

            if not os.path.isdir(output_directory):
                print(f"✗ Error: Output directory does not exist: {output_directory}")
                sys.exit(1)

            timestamp_prefix = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            base_prefix = f"runs/{run_id}/{timestamp_prefix}/"

            print(f"Output directory (resolved): {output_directory}")
            print(f"S3 destination prefix: s3://{BUCKET}/{base_prefix}")

            uploaded_count = 0
            failed_uploads = []
            manifest_entries: List[Dict[str, Any]] = []

            for root, _, files in os.walk(output_directory):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(file_path, output_directory)
                    normalized_relative_path = "/".join(relative_path.split(os.sep))
                    s3_key = f"{base_prefix}{normalized_relative_path}"

                    # Build manifest entry (includes validation info)
                    manifest_entry = build_manifest_entry(file_path, normalized_relative_path)
                    manifest_entry["s3_key"] = s3_key
                    manifest_entries.append(manifest_entry)

                    # Upload raw file regardless of validation outcome, but log status
                    try:
                        s3.upload_file(Filename=file_path, Bucket=BUCKET, Key=s3_key)
                        uploaded_count += 1
                        valid_flag = "valid" if manifest_entry["validation"]["valid"] else "invalid"
                        schema_id = manifest_entry["validation"]["schema_id"]
                        schema_info = f"schema={schema_id}" if schema_id else "schema=none"
                        print(f"✓ Uploaded ({valid_flag}, {schema_info}) {file_path} -> s3://{BUCKET}/{s3_key}")
                    except Exception as e:
                        failed_uploads.append((file_path, str(e)))
                        print(f"⚠ Failed to upload {file_path}: {e}")

            # Write manifest to S3 (even if some uploads failed)
            manifest_key = f"{base_prefix}manifest.json"
            manifest_body = json.dumps(
                {
                    "run_id": run_id,
                    "timestamp": timestamp_prefix,
                    "output_dir": output_directory,
                    "files": manifest_entries,
                },
                indent=2,
            )
            try:
                s3.put_object(Body=manifest_body.encode("utf-8"), Bucket=BUCKET, Key=manifest_key)
                print(f"✓ Uploaded manifest -> s3://{BUCKET}/{manifest_key}")
            except Exception as e:
                print(f"⚠ Failed to upload manifest: {e}")

            if uploaded_count == 0:
                print("✗ No files uploaded; no files found in output directory or all uploads failed.")
                sys.exit(1)

            print(f"✓ Uploaded {uploaded_count} file(s) to S3")
            if failed_uploads:
                print("⚠ Some files failed to upload:")
                for path, error in failed_uploads:
                    print(f"  - {path}: {error}")

        else:
            print("⚠ No output-dir specified in config, skipping output retrieval")
    else:
        print(f"✗ Command failed with exit code: {result['exit_code']}")
        if result["stderr"]:
            print(f"Error: {result['stderr']}")
        sys.exit(1)
    
    return


def get_output(output_dir: str, working_dir: str) -> str:
    """
    Legacy helper for single-file output retrieval (not used by handle_run).
    Prefer the directory-based S3 uploads implemented in handle_run.

    Args:
        output_dir: Directory containing run outputs (relative or absolute)
        working_dir: Working directory to resolve relative paths

    Returns:
        File contents as string, or None if file doesn't exist
    """
    # Handle None or empty output_dir
    if not output_dir:
        print("[CLI] No output directory specified, skipping output retrieval")
        return None

    # Resolve to absolute path on user's machine
    if not os.path.isabs(output_dir):
        full_path = os.path.join(working_dir, output_dir)
    else:
        full_path = output_dir

    # Check if file exists on user's machine
    if not os.path.exists(full_path):
        print(f"[CLI] Warning: Output file not found at {full_path}")
        return None

    # Read entire file from user's machine
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"[CLI] Successfully read {len(content)} bytes from {full_path}")
        return content
    except Exception as e:
        print(f"[CLI] Error reading output file: {e}")
        return None

def execute_command(command: str, working_dir: str = None) -> dict:
    """
    Execute a shell command on the local machine with real-time output.
    
    Args:
        command: The full command string to execute
        working_dir: Optional working directory (defaults to current dir)
        
    Returns:
        Dict with execution results: {
            "success": bool,
            "exit_code": int,
            "stdout": str,
            "stderr": str
        }
    """
    print(f"Executing: {command}")
    print(f"Working directory: {working_dir or os.getcwd()}")
    print()
    print(command)
    
    try:
        # Start the process
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
            cwd=working_dir
        )
        
        # Collect output while streaming to console
        stdout_lines = []
        stderr_lines = []
        
        # Read stdout in real-time
        while True:
            stdout_line = process.stdout.readline()
            if stdout_line:
                print(stdout_line, end='')
                stdout_lines.append(stdout_line)
            
            # Check if process has finished
            if process.poll() is not None:
                # Read any remaining output
                remaining = process.stdout.read()
                if remaining:
                    print(remaining, end='')
                    stdout_lines.append(remaining)
                break
        
        # Read stderr after process completes
        stderr_output = process.stderr.read()
        if stderr_output:
            print(stderr_output, file=sys.stderr)
            stderr_lines.append(stderr_output)
        
        # Get exit code
        exit_code = process.returncode
        
        return {
            "success": exit_code == 0,
            "exit_code": exit_code,
            "stdout": "".join(stdout_lines),
            "stderr": "".join(stderr_lines)
        }
        
    except FileNotFoundError:
        return {
            "success": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": f"Command not found: {command.split()[0]}"
        }
    except Exception as e:
        return {
            "success": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": f"Error executing command: {str(e)}"
        }


def build_command_from_config(yaml_config: dict) -> str:
    """
    Build a shell command from YAML configuration.

    Args:
        yaml_config: Parsed YAML configuration

    Returns:
        Complete command string
    """
    # Reserved keys that are not CLI flags
    # These are metadata fields stored in the database but not passed to the command
    #
    # Categories:
    # - System fields: cmd, name, description
    # - Path fields: config-path, output-dir/output_dir, working-directory
    # - Metadata fields: Custom fields that may be used for tracking/filtering in UI
    #
    # Note: Any field not in this list will be passed as a CLI flag (--field-name value)
    RESERVED_KEYS = {
        # Core system fields (required)
        "cmd",                    # The command to execute
        "name",                   # Display name in UI (legacy)
        "run_name",               # Display name in UI (canonical)
        "project_name",           # Project name (metadata that is required)

        # Optional metadata fields (stored in DB, not passed to CLI)
        "description",            # Run description
        "config-path",            # Path to the YAML config file
        "output-dir",             # Directory where evaluation output is written
        "output_dir",             # Directory where evaluation output is written
        "working-directory",      # Working directory for command execution

        # Common metadata fields (customize based on your needs)
        # These are stored in yaml_metadata JSONB column for filtering/analysis
        "model",                  # Model name (e.g., "gpt-4")
        "prompt-variant",         # Prompt variant identifier
        "prompt_variant",         # Alternative underscore format
        "experiment-name",        # Experiment name
        "experiment_name",        # Alternative underscore format
        "tags",                   # Custom tags for categorization
        "version",                # Version identifier
    }
    
    # Get base command
    base_cmd = yaml_config.get("cmd")
    if not base_cmd:
        raise ValueError("YAML config must contain 'cmd' field")
    
    # Build argument list
    args = []
    
    for key, value in yaml_config.items():
        # Skip reserved keys
        if key in RESERVED_KEYS:
            continue
            
        # Skip None or empty values
        if value is None or value == "":
            continue
        
        # Convert key to CLI flag format (e.g., "feature-flag" -> "--feature-flag")
        flag = f"--{key}"
        
        # Handle different value types
        if isinstance(value, bool):
            # Boolean flags: only include if True
            if value:
                args.append(flag)
        else:
            # String/number flags: include with value
            args.append(f"{flag} {value}")
    
    return base_cmd

def handle_logout(args):
    """Handle the logout command"""
    config = SorenConfig()
    config.clear()
    print("✓ Logged out successfully")


def main():
    """Main entry point for the Soren CLI"""

    # Main parser
    parser = argparse.ArgumentParser(
        prog="soren",
        description="Soren AI - Evaluation framework CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    # Global version flag
    parser.add_argument(
        "--version",
        action="version",
        version=f"soren {__version__}",
    )
    
    # Subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # API login command
    login_parser = subparsers.add_parser("login", help="Authenticate with Soren")
    login_parser.add_argument("--SOREN_API_KEY", help="Your Soren API key")
    
    # Run command (will be edited later to support their CLI)

    # THEIR EVALS CLI
    # 3. **Local**: Run `poetry run evaluate-agents-performance`
    # - **Base mode**: `poetry run evaluate-agents-performance`
    # - **With feature flags**: `poetry run evaluate-agents-performance --feature-flag is_opted_in_to_gold_examples`
    # - **With baseline agents**: `poetry run evaluate-agents-performance --include-baseline`
    # - **On backtesting data**: `poetry run evaluate-agents-performance --end-to-end`
    run_parser = subparsers.add_parser("run", help="Create and run an evaluation")
    run_parser.add_argument("config_path", help="The path to the config file")
    
    # Logout command
    logout_parser = subparsers.add_parser("logout", help="Clear stored credentials")
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    
    # Route to command handlers
    if args.command == "login":
        handle_login(args)
    elif args.command == "run":
        handle_run(args)
    elif args.command == "logout":
        handle_logout(args)
    else:
        print(f"Command '{args.command}' not yet implemented")


if __name__ == "__main__":
    main()
