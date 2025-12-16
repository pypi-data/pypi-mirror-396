#!/usr/bin/env python3
import argparse
from itertools import cycle
from pathlib import Path

import yaml

COLORS = [
    "\x1b[91m",  # red
    "\x1b[92m",  # green
    "\x1b[93m",  # yellow
    "\x1b[94m",  # blue
    "\x1b[95m",  # magenta
    "\x1b[96m",  # cyan
]
RESET = "\x1b[0m"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Visualize the provenance of values in a YAML overlay file"
    )
    parser.add_argument("files", nargs="+", type=Path)
    return parser.parse_args()


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def overlay(a, b):
    """Deep overlay: last writer wins."""
    if not isinstance(a, dict) or not isinstance(b, dict):
        return b

    result = dict(a)
    for key, value in b.items():
        if key in result:
            result[key] = overlay(result[key], value)
        else:
            result[key] = value
    return result


def track_provenance(data, path, provenance, file_id):
    """Track provenance for each YAML path."""
    provenance.setdefault(tuple(path), set()).add(file_id)

    if isinstance(data, dict):
        for k, v in data.items():
            track_provenance(v, path + [k], provenance, file_id)

    elif isinstance(data, list):
        for i, v in enumerate(data):
            track_provenance(v, path + [i], provenance, file_id)


def _colorize(data, color):
    out = []
    if not isinstance(data, str):
        return f"{color}{data}{RESET}"
    lines = data.split("\n")
    for line in lines:
        out.append(f"{color}{line}{RESET}")
    return "\n".join(out)


def colorize(data, path, provenance, colors):
    """Apply ANSI coloring to scalar values based on last writer."""
    file_ids = provenance.get(tuple(path))
    last_file = sorted(file_ids)[-1]
    color = colors[last_file]

    if isinstance(data, dict):
        return {k: colorize(v, path + [k], provenance, colors) for k, v in data.items()}

    if isinstance(data, list):
        return [colorize(v, path + [i], provenance, colors) for i, v in enumerate(data)]

    # Scalar
    return _colorize(data, color)


def print_yaml_like(data, indent=0):
    """Print YAML shape manually with indentation and raw ANSI colors."""
    ind = "  " * indent

    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                print(f"{ind}{k}:")
                print_yaml_like(v, indent + 1)
            else:
                print(f"{ind}{k}: {v}")
        return

    if isinstance(data, list):
        for v in data:
            if isinstance(v, (dict, list)):
                print(f"{ind}-")
                print_yaml_like(v, indent + 1)
            else:
                print(f"{ind}- {v}")
        return

    print(f"{ind}{data}")


def main():
    args = parse_args()
    file_ids = {p: i for i, p in enumerate(args.files)}
    color_map = {file_ids[p]: c for p, c in zip(args.files, cycle(COLORS))}

    provenance = {}
    structures = []

    # Load YAMLs + provenance tracking
    for f in args.files:
        if not f.exists():
            continue
        data = load_yaml(f)
        structures.append(data)
        track_provenance(data, [], provenance, file_ids[f])

    # Overlay all files
    merged = {}
    for s in structures:
        merged = overlay(merged, s)

    print("---")
    for file_id, color in color_map.items():
        filename = args.files[file_id]
        print(_colorize(str(filename), color))
    print("---")

    # Apply color to values
    colored = colorize(merged, [], provenance, color_map)

    # Print YAML-like output with real ANSI escapes
    try:
        print_yaml_like(colored)
    except BrokenPipeError:
        ...


if __name__ == "__main__":
    main()
