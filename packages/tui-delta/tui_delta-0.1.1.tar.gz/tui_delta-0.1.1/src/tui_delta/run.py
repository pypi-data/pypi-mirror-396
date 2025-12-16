#!/usr/bin/env python3
"""
Run a TUI application with real-time delta processing.

Wraps a TUI application using `script` to capture all terminal output
(including escape sequences), then processes through the pipeline:
  clear_lines → consolidate → uniqseq → cut → uniqseq

The TUI displays normally to the user while processed deltas stream to stdout.
"""

import platform
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Optional


def build_script_command(
    command: list[str],
    system: Optional[str] = None,
) -> list[str]:
    """
    Build platform-specific script command.

    Args:
        command: The TUI command to run (e.g., ['claude', 'code'])
        system: Platform identifier ('Darwin' or 'Linux'). Auto-detected if None.

    Returns:
        Complete script command as list
    """
    if system is None:
        system = platform.system()

    if system == "Darwin":  # macOS
        # macOS syntax: script -q -F /dev/stdout command args...
        # Note: -F forces output even if stdout is not a terminal
        return ["script", "-q", "-F", "/dev/stdout"] + command
    else:  # Linux and others
        # Linux syntax: script --flush --quiet --return --command "cmd" /dev/stdout
        # --return: return exit code of child process
        # --command: command to execute
        cmd_str = shlex.join(command)
        return [
            "script",
            "--flush",
            "--quiet",
            "--return",
            "--command",
            cmd_str,
            "/dev/stdout",
        ]


def build_pipeline_commands(
    profile: Optional[str] = None,
    rules_file: Optional[Path] = None,
) -> list[list[str]]:
    """
    Build the processing pipeline command list.

    Standard pipeline: clear_lines → consolidate → uniqseq → cut
    Optional: additional_pipeline command from profile

    Args:
        profile: Clear rules profile (claude_code, generic, etc.)
        rules_file: Custom rules YAML file

    Returns:
        List of command lists for the pipeline
    """
    from .clear_rules import ClearRules

    pipeline: list[list[str]] = []

    # Step 1: clear_lines --prefixes
    clear_cmd = [sys.executable, "-m", "tui_delta.clear_lines", "--prefixes"]
    if profile:
        clear_cmd.extend(["--profile", profile])
    if rules_file:
        clear_cmd.extend(["--rules-file", str(rules_file)])
    pipeline.append(clear_cmd)

    # Step 2: consolidate_clears
    consolidate_cmd = [sys.executable, "-m", "tui_delta.consolidate_clears"]
    pipeline.append(consolidate_cmd)

    # Step 3: uniqseq --track '^\+: ' --quiet
    uniqseq1_cmd = [
        sys.executable,
        "-m",
        "uniqseq",
        "--track",
        r"^\+: ",
        "--quiet",
    ]
    pipeline.append(uniqseq1_cmd)

    # Step 4: cut -b 4- (strip prefix)
    # Using Python one-liner to strip first 4 characters
    # Use end='' to avoid adding extra newlines (stdin lines already have them)
    cut_cmd = [sys.executable, "-c", "import sys; [print(line[3:], end='') for line in sys.stdin]"]
    pipeline.append(cut_cmd)

    # Step 5 (optional): additional_pipeline from profile
    try:
        profile_config = ClearRules.get_profile_config(profile, rules_file)
        additional_pipeline = profile_config.get("additional_pipeline")
        if additional_pipeline:
            # Parse shell command into list for subprocess
            # Shell will handle the command string, so pass it as-is
            pipeline.append(["sh", "-c", additional_pipeline])
    except (FileNotFoundError, ValueError):
        # If profile not found or file missing, continue without additional pipeline
        pass

    return pipeline


def run_tui_with_pipeline(
    command: list[str],
    profile: Optional[str] = None,
    rules_file: Optional[Path] = None,
) -> int:
    """
    Run a TUI application with real-time delta processing.

    Args:
        command: The TUI command to run
        profile: Clear rules profile
        rules_file: Custom rules YAML file

    Returns:
        Exit code from the TUI application
    """
    # Build script command
    script_cmd = build_script_command(command)

    # Build pipeline commands
    pipeline_cmds = build_pipeline_commands(profile, rules_file)

    # Create pipeline: script | cmd1 | cmd2 | ... | stdout
    processes: list[subprocess.Popen[bytes]] = []

    try:
        # Start script process
        script_proc = subprocess.Popen(
            script_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        processes.append(script_proc)
        current_stdin = script_proc.stdout

        # Chain pipeline commands
        for cmd in pipeline_cmds:
            proc = subprocess.Popen(
                cmd,
                stdin=current_stdin,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            processes.append(proc)
            # Close the previous stdout in this process to allow SIGPIPE
            if current_stdin:
                current_stdin.close()
            current_stdin = proc.stdout

        # Final process writes to stdout
        if current_stdin:
            # Read from final process and write to stdout
            try:
                for line in current_stdin:
                    sys.stdout.buffer.write(line)
                    sys.stdout.buffer.flush()
            except KeyboardInterrupt:
                # User interrupted - clean up
                pass
            finally:
                current_stdin.close()

        # Wait for all processes and collect errors
        exit_code = 0
        errors: list[str] = []

        for i, proc in enumerate(processes):
            proc.wait()

            # Collect stderr if process failed
            if proc.returncode != 0 and proc.stderr:
                stderr_output = proc.stderr.read().decode("utf-8", errors="replace")
                # Identify which stage failed
                if proc == script_proc:
                    stage_name = "script"
                else:
                    stage_name = f"pipeline stage {i}"

                errors.append(f"{stage_name} (exit {proc.returncode}):\n{stderr_output}")

                # Capture first non-zero exit code
                if exit_code == 0:
                    exit_code = proc.returncode

            # Also capture script's exit code even if it succeeds
            if proc == script_proc and exit_code == 0:
                exit_code = proc.returncode

        # Report all errors to stderr
        if errors:
            print("Pipeline errors:", file=sys.stderr)
            for error in errors:
                print(error, file=sys.stderr)

        return exit_code

    except Exception as e:
        print(f"Error running pipeline: {e}", file=sys.stderr)
        # Clean up processes
        for proc in processes:
            try:
                proc.terminate()
            except Exception:
                pass
        return 1
