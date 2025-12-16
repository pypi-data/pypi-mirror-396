# Copyright 2025 BBDevs
# Licensed under the Apache License, Version 2.0

"""Docker output formatters for TUI-like terminal and Jenkins output.

This module provides formatted, streaming output for Docker operations (build,
pull, push, logs, exec) that works well in both terminal and Jenkins environments.

Author: A M (am@bbdevs.com)
Created At: 12 Dec 2025
"""

from __future__ import annotations

import json
import os
import re
import sys
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

# ANSI escape code patterns
ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")


def is_jenkins() -> bool:
    """Check if running in Jenkins environment.

    Returns:
        True if BUILD_NUMBER or JENKINS_URL is set.
    """
    return bool(os.getenv("BUILD_NUMBER") or os.getenv("JENKINS_URL"))


def is_ansi_supported() -> bool:
    """Check if ANSI colors are supported.

    Returns:
        True if terminal supports colors or Jenkins has AnsiColor plugin.
    """
    # Check if Jenkins has AnsiColor plugin (common pattern)
    if is_jenkins():
        # AnsiColor plugin sets this
        return os.getenv("ANSI_COLOR") == "true" or os.getenv("TERM") == "xterm"

    # Check if terminal supports colors
    return sys.stdout.isatty() and os.getenv("TERM") != "dumb"


def strip_ansi(text: str) -> str:
    """Strip ANSI escape codes from text.

    Args:
        text: Text with ANSI codes.

    Returns:
        Text without ANSI codes.
    """
    return ANSI_ESCAPE.sub("", text)


def clean_line(line: str) -> str:
    """Clean Docker build output line.

    Args:
        line: Raw line from Docker build.

    Returns:
        Cleaned line.
    """
    # Strip ANSI if not supported
    if not is_ansi_supported():
        line = strip_ansi(line)

    # Remove common Docker build noise
    line = line.strip()

    # Remove redundant whitespace
    line = re.sub(r"\s+", " ", line)

    return line


def extract_step_info(line: str) -> tuple[int | None, int | None, str, bool]:
    """Extract step number and message from Docker build line.

    Args:
        line: Docker build output line.

    Returns:
        Tuple of (step_number, total_steps, message, has_step_prefix).
        has_step_prefix indicates if line already contains step number format.
    """
    # Pattern: "Step X/Y : COMMAND" - Docker already includes step number
    step_match = re.search(r"Step\s+(\d+)/(\d+)\s*:\s*(.+)", line, re.IGNORECASE)
    if step_match:
        step_num = int(step_match.group(1))
        total_steps = int(step_match.group(2))
        command = step_match.group(3).strip()
        return step_num, total_steps, f"[{step_num}/{total_steps}] {command}", True

    # Pattern: "---> Running in <container_id>"
    running_match = re.search(r"--->\s+Running in\s+(\w+)", line)
    if running_match:
        return None, None, f"  → Running in container {running_match.group(1)[:12]}...", False

    # Pattern: "---> <step_id>"
    step_id_match = re.search(r"--->\s+([a-f0-9]{12})", line)
    if step_id_match:
        return None, None, "  ✓ Step completed", False

    # Pattern: "---> Using cache"
    if "Using cache" in line:
        return None, None, "  ⊘ Using cache", False

    # Pattern: "Removed intermediate container"
    if "Removed intermediate container" in line:
        return None, None, "  🗑️  Cleaned up intermediate container", False

    return None, None, line, False


def should_show_line(line: str, last_line: str | None = None) -> bool:
    """Determine if a line should be shown (filter repetitive/verbose output).

    Args:
        line: Current line to check.
        last_line: Previous line for comparison.

    Returns:
        True if line should be shown, False if it should be filtered.
    """
    cleaned = clean_line(line).lower()

    # Filter completely empty lines
    if not cleaned:
        return False

    # Filter repetitive SSH keyscan output (same line repeated)
    if cleaned.startswith("# ") and "ssh-2.0" in cleaned:
        if last_line and last_line.lower() == cleaned:
            return False

    # Show important lines
    if any(keyword in cleaned for keyword in ["error", "warning", "successfully", "step", "--->"]):
        return True

    # Show non-trivial content (more than just whitespace/punctuation)
    if len(cleaned.strip()) > 3:
        return True

    return False


def format_warning(message: str) -> str:
    """Format a warning message.

    Args:
        message: Warning message.

    Returns:
        Formatted warning line.
    """
    marker = "⚠" if is_ansi_supported() else "[WARN]"
    return f"{marker} Warning: {message}"


def format_success(message: str) -> str:
    """Format a success message.

    Args:
        message: Success message.

    Returns:
        Formatted success line.
    """
    marker = "✓" if is_ansi_supported() else "[OK]"
    return f"{marker} {message}"


def format_progress_line(
    line: str,
    current_step: int | None = None,
    current_total: int | None = None,
    last_line: str | None = None,
) -> str | None:
    """Format a single Docker build output line.

    Args:
        line: Raw line from Docker build.
        current_step: Current step number if known.
        current_total: Total number of steps if known.
        last_line: Previous line for filtering repetitive output.

    Returns:
        Formatted line ready for output, or None if line should be filtered.
    """
    cleaned = clean_line(line)

    # Skip empty lines
    if not cleaned:
        return None

    # Filter repetitive/verbose output
    if not should_show_line(cleaned, last_line):
        return None

    # Extract step info if available
    step_num, total_steps, formatted, has_step_prefix = extract_step_info(cleaned)

    # Update current step if we detected one
    if step_num is not None:
        current_step = step_num
        current_total = total_steps

    # Determine prefix - don't duplicate if Docker already shows step number
    if has_step_prefix:
        # Docker already shows [N/M], just use that format
        prefix = "  "
    elif step_num is not None and current_total is not None:
        prefix = f"  [{step_num}/{current_total}]"
    elif current_step is not None and current_total is not None:
        prefix = f"  [{current_step}/{current_total}]"
    elif current_step is not None:
        prefix = f"  [{current_step:2d}]"
    else:
        prefix = "     "

    # Format based on content type
    if "error" in cleaned.lower() or "fatal" in cleaned.lower():
        marker = "✗" if is_ansi_supported() else "[ERROR]"
    elif "warning" in cleaned.lower() or "build-args" in cleaned.lower():
        marker = "⚠" if is_ansi_supported() else "[WARN]"
    elif cleaned.startswith("--->"):
        marker = "→" if is_ansi_supported() else "->"
    elif "complete" in cleaned.lower() or "success" in cleaned.lower() or "successfully" in cleaned.lower():
        marker = "✓" if is_ansi_supported() else "[OK]"
    else:
        marker = " "

    return f"{prefix} {marker} {formatted}"


async def format_build_stream(
    stream: AsyncIterator[str],
    tag: str | None = None,
    write_to_stdout: bool = True,
) -> AsyncIterator[dict[str, Any]]:
    """Format Docker build stream into TUI-like output.

    Args:
        stream: Async iterator of raw Docker build JSON lines.
        tag: Image tag being built (for header).
        write_to_stdout: If True, write formatted output to stdout. If False, yield formatted lines.

    Yields:
        If write_to_stdout=False: Formatted lines as strings.
        If write_to_stdout=True: Original JSON dicts from stream (for image_id extraction).
    """
    current_step: int | None = None
    step_count: int | None = None
    last_line: str | None = None
    warnings: list[str] = []
    success_messages: list[str] = []

    # Print header
    if tag:
        header = f"\n🔨 Building Docker image: {tag}\n"
    else:
        header = "\n🔨 Building Docker image...\n"

    if write_to_stdout:
        sys.stdout.write(header)
        sys.stdout.flush()
    else:
        yield header

    async for line in stream:
        if not line:
            continue

        try:
            data = json.loads(line)

            # Handle stream output
            if "stream" in data:
                stream_line = data["stream"].rstrip()
                if stream_line:
                    formatted = format_progress_line(stream_line, current_step, step_count, last_line)
                    if formatted:
                        if write_to_stdout:
                            sys.stdout.write(formatted + "\n")
                            sys.stdout.flush()
                        else:
                            yield formatted
                        last_line = stream_line

                    # Update current step if we detected one
                    step_match = re.search(r"Step\s+(\d+)/(\d+)", stream_line, re.IGNORECASE)
                    if step_match:
                        current_step = int(step_match.group(1))
                        step_count = int(step_match.group(2))

                    # Capture warnings and success messages
                    cleaned = clean_line(stream_line).lower()
                    if "warning" in cleaned or "build-args" in cleaned:
                        warnings.append(stream_line)
                    elif "successfully" in cleaned:
                        success_messages.append(stream_line)

                # Yield data dict for image_id extraction
                if write_to_stdout:
                    yield data

            # Handle progress output (pull progress, etc.)
            elif "progressDetail" in data or "status" in data:
                status = data.get("status", "")
                if status and status not in ("Downloading", "Extracting"):
                    # Only show non-progress status messages
                    formatted = format_progress_line(status, current_step, step_count, last_line)
                    if formatted:
                        if write_to_stdout:
                            sys.stdout.write(formatted + "\n")
                            sys.stdout.flush()
                        else:
                            yield formatted
                        last_line = status

                # Yield data dict for image_id extraction
                if write_to_stdout:
                    yield data

            # Handle errors
            elif "error" in data:
                error_msg = data.get("error", "Unknown build error")
                error_detail = data.get("errorDetail", {}).get("message", error_msg)
                error_line = f"\n✗ Build Error: {error_detail}\n"
                if write_to_stdout:
                    sys.stdout.write(error_line)
                    sys.stdout.flush()
                else:
                    yield error_line
                # Yield the error dict for handling
                if write_to_stdout:
                    yield data
                break

            # Handle aux output (image IDs, etc.)
            elif "aux" in data:
                aux_data = data.get("aux", {})
                if "ID" in aux_data:
                    image_id = aux_data["ID"]
                    footer = f"\n✓ Image ID: {image_id[:12]}...\n"
                    if write_to_stdout:
                        sys.stdout.write(footer)
                        sys.stdout.flush()
                    else:
                        yield footer

                # Yield data dict for image_id extraction
                if write_to_stdout:
                    yield data

            # Handle any other data types
            else:
                # Yield data dict for image_id extraction
                if write_to_stdout:
                    yield data

        except json.JSONDecodeError:
            # Non-JSON line, try to format as-is
            formatted = format_progress_line(line, current_step, step_count, last_line)
            if formatted:
                if write_to_stdout:
                    sys.stdout.write(formatted + "\n")
                    sys.stdout.flush()
                else:
                    yield formatted
                last_line = line

    # Print warnings and success messages
    if warnings:
        for warning in warnings:
            if "build-args" in warning.lower():
                # Extract build-args warning message
                args_match = re.search(r"\[(.*?)\]", warning)
                if args_match:
                    args_list = args_match.group(1)
                    warning_msg = format_warning(f"One or more build-args were not consumed: {args_list}")
                else:
                    warning_msg = format_warning(warning)
            else:
                warning_msg = format_warning(warning)
            if write_to_stdout:
                sys.stdout.write(warning_msg + "\n")
                sys.stdout.flush()
            else:
                yield warning_msg

    if success_messages:
        for msg in success_messages:
            # Extract success message (e.g., "Successfully built", "Successfully tagged")
            if "successfully built" in msg.lower():
                built_match = re.search(r"Successfully built\s+([a-f0-9]+)", msg, re.IGNORECASE)
                if built_match:
                    success_msg = format_success(f"Successfully built {built_match.group(1)}")
                else:
                    success_msg = format_success(msg)
            elif "successfully tagged" in msg.lower():
                tagged_match = re.search(r"Successfully tagged\s+(.+)", msg, re.IGNORECASE)
                if tagged_match:
                    success_msg = format_success(f"Successfully tagged {tagged_match.group(1)}")
                else:
                    success_msg = format_success(msg)
            else:
                success_msg = format_success(msg)
            if write_to_stdout:
                sys.stdout.write(success_msg + "\n")
                sys.stdout.flush()
            else:
                yield success_msg

    # Print footer
    if current_step and step_count:
        footer = f"\n✓ Build completed: {current_step}/{step_count} steps\n"
    else:
        footer = "\n✓ Build completed\n"

    if write_to_stdout:
        sys.stdout.write(footer)
        sys.stdout.flush()
    else:
        yield footer


async def format_pull_stream(
    stream: AsyncIterator[str],
    image_ref: str,
    write_to_stdout: bool = True,
) -> AsyncIterator[dict[str, Any]]:
    """Format Docker image pull stream into TUI-like output.

    Args:
        stream: Async iterator of raw Docker pull JSON lines.
        image_ref: Image reference (repository:tag).
        write_to_stdout: If True, write formatted output to stdout.

    Yields:
        Original JSON dicts from stream.
    """
    header = f"\n📥 Pulling image: {image_ref}\n"
    if write_to_stdout:
        sys.stdout.write(header)
        sys.stdout.flush()

    last_status: str | None = None
    layers: dict[str, dict[str, Any]] = {}

    async for line in stream:
        if not line:
            continue

        try:
            data = json.loads(line)

            if "status" in data:
                status = data["status"]
                status_detail = data.get("statusDetail", {})

                # Skip repetitive downloading/extracting progress
                if status in ("Downloading", "Extracting") and status == last_status:
                    continue

                last_status = status

                # Format status message
                if "id" in data:
                    layer_id = data["id"][:12]
                    progress = status_detail.get("current", 0)
                    total = status_detail.get("total", 0)

                    if progress and total:
                        percent = int((progress / total) * 100)
                        progress_bar = "█" * (percent // 10) + "░" * (10 - percent // 10)
                        size_mb = total / (1024 * 1024)
                        current_mb = progress / (1024 * 1024)
                        status_line = f"  → {layer_id}: {status} [{progress_bar}] {current_mb:.1f}MB/{size_mb:.1f}MB"
                    else:
                        status_line = f"  → {layer_id}: {status}"
                else:
                    status_line = f"  → {status}"

                if write_to_stdout:
                    sys.stdout.write(status_line + "\n")
                    sys.stdout.flush()

            elif "error" in data:
                error_msg = data.get("error", "Unknown pull error")
                error_line = f"\n✗ Pull Error: {error_msg}\n"
                if write_to_stdout:
                    sys.stdout.write(error_line)
                    sys.stdout.flush()
                yield data
                break

            elif "aux" in data:
                # Digest information
                aux_data = data.get("aux", {})
                if "Digest" in aux_data:
                    digest = aux_data["Digest"]
                    digest_line = f"  → Digest: {digest}\n"
                    if write_to_stdout:
                        sys.stdout.write(digest_line)
                        sys.stdout.flush()

            yield data

        except json.JSONDecodeError:
            continue

    footer = "\n✓ Pull completed\n"
    if write_to_stdout:
        sys.stdout.write(footer)
        sys.stdout.flush()


async def format_push_stream(
    stream: AsyncIterator[str],
    image_ref: str,
    write_to_stdout: bool = True,
) -> AsyncIterator[dict[str, Any]]:
    """Format Docker image push stream into TUI-like output.

    Args:
        stream: Async iterator of raw Docker push JSON lines.
        image_ref: Image reference (repository:tag).
        write_to_stdout: If True, write formatted output to stdout.

    Yields:
        Original JSON dicts from stream.
    """
    header = f"\n📤 Pushing image: {image_ref}\n"
    if write_to_stdout:
        sys.stdout.write(header)
        sys.stdout.flush()

    last_status: str | None = None

    async for line in stream:
        if not line:
            continue

        try:
            data = json.loads(line)

            if "status" in data:
                status = data["status"]
                status_detail = data.get("statusDetail", {})

                # Skip repetitive uploading progress
                if status == "Pushing" and status == last_status:
                    continue

                last_status = status

                # Format status message
                if "id" in data:
                    layer_id = data["id"][:12]
                    progress = status_detail.get("current", 0)
                    total = status_detail.get("total", 0)

                    if progress and total:
                        percent = int((progress / total) * 100)
                        progress_bar = "█" * (percent // 10) + "░" * (10 - percent // 10)
                        size_mb = total / (1024 * 1024)
                        current_mb = progress / (1024 * 1024)
                        status_line = f"  → {layer_id}: {status} [{progress_bar}] {current_mb:.1f}MB/{size_mb:.1f}MB"
                    else:
                        status_line = f"  → {layer_id}: {status}"
                else:
                    status_line = f"  → {status}"

                if write_to_stdout:
                    sys.stdout.write(status_line + "\n")
                    sys.stdout.flush()

            elif "error" in data:
                error_msg = data.get("error", "Unknown push error")
                error_line = f"\n✗ Push Error: {error_msg}\n"
                if write_to_stdout:
                    sys.stdout.write(error_line)
                    sys.stdout.flush()
                yield data
                break

            elif "aux" in data:
                # Digest information
                aux_data = data.get("aux", {})
                if "Digest" in aux_data:
                    digest = aux_data["Digest"]
                    digest_line = f"  → Digest: {digest}\n"
                    if write_to_stdout:
                        sys.stdout.write(digest_line)
                        sys.stdout.flush()

            yield data

        except json.JSONDecodeError:
            continue

    footer = "\n✓ Push completed\n"
    if write_to_stdout:
        sys.stdout.write(footer)
        sys.stdout.flush()


async def format_logs_stream(
    stream: AsyncIterator[str],
    container_id: str,
    timestamps: bool = False,
    write_to_stdout: bool = True,
) -> AsyncIterator[str]:
    """Format container logs stream into TUI-like output.

    Args:
        stream: Async iterator of raw log lines (already decoded from bytes).
        container_id: Container ID or name.
        timestamps: Whether to include timestamps.
        write_to_stdout: If True, write formatted output to stdout.

    Yields:
        Formatted log lines (if write_to_stdout=False) or original lines.
    """
    header = f"\n📋 Logs for container: {container_id}\n"
    if write_to_stdout:
        sys.stdout.write(header)
        sys.stdout.flush()
    else:
        yield header

    async for line in stream:
        if not line:
            continue

        # Line is already decoded string from containers.py
        message = str(line).rstrip("\n")

        # Try to detect stream type from message format if available
        # Otherwise default to stdout
        stream_type = "stdout"
        if "[stderr]" in message.lower():
            stream_type = "stderr"
            # Remove the marker if present
            message = message.replace("[stderr]", "").replace("[STDERR]", "").strip()
        elif "[stdout]" in message.lower():
            stream_type = "stdout"
            # Remove the marker if present
            message = message.replace("[stdout]", "").replace("[STDOUT]", "").strip()

        # Format log line
        if timestamps:
            from datetime import datetime, timezone

            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            formatted = f"[{timestamp}] [{stream_type}] {message}"
        else:
            formatted = f"[{stream_type}] {message}"

        if write_to_stdout:
            sys.stdout.write(formatted + "\n")
            sys.stdout.flush()
        else:
            yield formatted


def format_exec_output(
    cmd: list[str] | str,
    output: str,
    exit_code: int,
    container_id: str,
    write_to_stdout: bool = True,
) -> str:
    """Format command execution output.

    Args:
        cmd: Command that was executed.
        output: Command output.
        exit_code: Exit code from command.
        container_id: Container ID or name.
        write_to_stdout: If True, write formatted output to stdout.

    Returns:
        Formatted output string.
    """
    cmd_str = " ".join(cmd) if isinstance(cmd, list) else str(cmd)
    header = f"\n🔧 Executing command in container: {container_id}\n\n$ {cmd_str}\n"
    footer = f"\n{format_success(f'Command completed (exit code: {exit_code})')}\n"

    formatted = header + output + footer

    if write_to_stdout:
        sys.stdout.write(formatted)
        sys.stdout.flush()

    return formatted

