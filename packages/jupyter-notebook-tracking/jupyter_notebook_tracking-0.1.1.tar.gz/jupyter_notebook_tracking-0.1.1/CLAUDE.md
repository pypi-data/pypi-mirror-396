# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

JupyterLab extension that tracks total editing time for notebooks, including per-editor tracking. The time is stored in the notebook's metadata as `total_edit_time_seconds` (integer representing cumulative seconds). Each save operation adds the elapsed time since the last save (or notebook open) to the total, and also tracks individual editor contributions.

## Technical Documentation

Use the context7 tool to ensure you are up to date with the latest documentation and examples.

## Build Commands

```bash
jlpm install          # Install npm dependencies
jlpm build            # Build extension (dev mode)
jlpm build:prod       # Build for production
jlpm watch            # Watch mode for development
jlpm lint             # Run all linters
jlpm lint:check       # Check without fixing
```

## Development Setup

```bash
pip install -e .                        # Install Python package in editable mode
jupyter labextension develop . --overwrite  # Link extension for development
```

## Architecture

- **src/index.ts**: Main plugin entry point. Registers with `INotebookTracker` to track notebook panels.
- **NotebookEditTimeTracker class**: Per-notebook tracker that:
  - Starts timing when notebook becomes ready
  - Listens to `saveState` signal to detect saves
  - Updates `total_edit_time_seconds` in notebook metadata on each save
  - Updates per-editor time in the `editors` dictionary
  - Resets timer after each save to track time between saves

## Utilities

In the `utils` folder
- `read_metadata.py` reads the metadata from the notebook 
- `clear_metadata.py` clears the metadata from the notebook


## Metadata Storage

All tracking data is stored under `notebook.metadata.tracking`:

- `tracking.total_edit_time_seconds` The cumulative edit time in seconds. Accumulates across sessions - opening a notebook that already has edit time will add to the existing value.
- `tracking.last_edit_by` The username of the last person who saved the notebook.
- `tracking.editors` A dictionary where keys are usernames and values are their total edit time in seconds.
- `tracking.history` An array of records appended on each save. Each record contains:
  - `timestamp`: ISO 8601 timestamp of when the save occurred
  - `user`: Username of who saved the file
  - `bytes`: Size of the notebook file in bytes at the time of save
  - `edit_time_seconds`: Time in seconds since the last save (or notebook open)
