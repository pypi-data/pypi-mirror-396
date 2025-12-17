#!/usr/bin/env python3
"""Reset the edit time metadata in a Jupyter notebook."""

import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser(description="Reset edit time in a Jupyter notebook to zero")
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

    if "metadata" not in notebook:
        notebook["metadata"] = {}

    tracking = notebook["metadata"].get("tracking", {})
    old_time = tracking.get("total_edit_time_seconds", 0)
    old_user = tracking.get("last_edit_by", "")
    old_editors = tracking.get("editors", {})
    old_history = tracking.get("history", [])

    if "tracking" in notebook["metadata"]:
        del notebook["metadata"]["tracking"]

    with open(args.path, "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=1)

    print(f"Cleared tracking metadata:")
    print(f"  total_edit_time_seconds: {old_time}s")
    if old_user:
        print(f"  last_edit_by: {old_user}")
    if old_editors:
        print(f"  editors: {old_editors}")
    if old_history:
        print(f"  history: {len(old_history)} records")


if __name__ == "__main__":
    main()
