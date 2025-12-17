#!/usr/bin/env python3
"""Read the total edit time from a Jupyter notebook."""

import argparse
import json
import sys


def format_time(seconds: int) -> str:
    """Format seconds as a friendly time string (e.g., '12h 34m 17s')."""
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)

    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if secs or not parts:
        parts.append(f"{secs}s")

    return " ".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Read edit time from a Jupyter notebook")
    parser.add_argument("path", help="Path to the notebook file")
    args = parser.parse_args()

    try:
        with open(args.path, "r", encoding="utf-8") as f:
            notebook = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in notebook: {e}", file=sys.stderr)
        sys.exit(1)




    metadata = notebook.get("metadata", {})
    tracking = metadata.get("tracking", {})
    total_edit_time = tracking.get("total_edit_time_seconds", 0)
    last_edit_by = tracking.get("last_edit_by", "")
    editors = tracking.get("editors", {})
    history = tracking.get("history", [])
    formatted_time = format_time(total_edit_time)

    print(f"total_edit_time_seconds: {total_edit_time}s / {formatted_time}")
    print(f"last_edit_by: {last_edit_by}")
    print("editors:")
    if editors:
        for user, seconds in editors.items():
            print(f"  {user}: {seconds}s / {format_time(seconds)}")
    else:
        print("  (none)")
    print(f"history: {len(history)} records")
    if history:
        for record in history:
            print(f"  {record['timestamp']} - {record['user']}: {record['bytes']} bytes, {record['edit_time_seconds']}s")


if __name__ == "__main__":
    main()
