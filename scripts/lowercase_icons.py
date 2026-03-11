#!/usr/bin/env python3
"""
lowercase_icons.py

Safe utility to lowercase all filenames under a directory (default: ./static/icons).
- Dry-run by default: prints planned operations.
- Use `--apply` to perform renames.

It handles case-only renames on case-insensitive filesystems by using a temporary intermediate name.
If multiple files map to the same lowercase name, it keeps the first and renames others with a `-dupN` suffix.
"""

from pathlib import Path
import argparse
import uuid
import sys


def find_files(base: Path):
    return [p for p in base.rglob("*") if p.is_file()]


def plan_renames(files, base: Path):
    mapping = {}
    for p in files:
        rel = p.relative_to(base)
        lower = Path(str(rel).lower())
        mapping.setdefault(str(lower), []).append(p)

    ops = []  # list of (src_path, dst_path)
    existing_targets = set()

    for lower_name, srcs in mapping.items():
        target = base / lower_name
        if len(srcs) == 1:
            src = srcs[0]
            # If src already equals target (path strings), skip
            if src.resolve() == target.resolve() and src.name == target.name:
                continue
            # Ensure we don't have another op to same target
            if str(target) in existing_targets:
                # conflict: create unique suffix
                i = 1
                new_target = target.with_name(target.stem + f"-dup{i}" + target.suffix)
                while str(new_target) in existing_targets:
                    i += 1
                    new_target = target.with_name(target.stem + f"-dup{i}" + target.suffix)
                ops.append((src, new_target))
                existing_targets.add(str(new_target))
            else:
                ops.append((src, target))
                existing_targets.add(str(target))
        else:
            # Multiple sources map to same lowercase name
            # Keep the first as the main target, others get -dupN
            first = srcs[0]
            if str(target) in existing_targets:
                # find next available target name
                i = 1
                new_target = target.with_name(target.stem + f"-dup{i}" + target.suffix)
                while str(new_target) in existing_targets:
                    i += 1
                    new_target = target.with_name(target.stem + f"-dup{i}" + target.suffix)
                ops.append((first, new_target))
                existing_targets.add(str(new_target))
                base_target = new_target
            else:
                ops.append((first, target))
                existing_targets.add(str(target))
                base_target = target

            for idx, other in enumerate(srcs[1:], start=1):
                i = idx
                new_target = base_target.with_name(base_target.stem + f"-dup{i}" + base_target.suffix)
                while str(new_target) in existing_targets:
                    i += 1
                    new_target = base_target.with_name(base_target.stem + f"-dup{i}" + base_target.suffix)
                ops.append((other, new_target))
                existing_targets.add(str(new_target))

    return ops


def do_rename(ops, apply_changes: bool):
    if not ops:
        print("No files to rename.")
        return

    print("Planned operations:")
    for src, dst in ops:
        print(f"{src} -> {dst}")

    if not apply_changes:
        print("\nDry run: no files were renamed. Re-run with --apply to perform changes.")
        return

    print("\nApplying changes...")
    for src, dst in ops:
        dst_parent = dst.parent
        dst_parent.mkdir(parents=True, exist_ok=True)

        # If target already exists and is the same inode/file, skip
        try:
            if dst.exists() and src.resolve() == dst.resolve():
                print(f"Skipping (same file): {src} -> {dst}")
                continue
        except Exception:
            pass

        # Handle case-only rename on case-insensitive FS: use temp name
        try:
            if src.parent == dst.parent and src.name.lower() == dst.name.lower() and src.name != dst.name:
                temp = src.with_name(src.name + f".tmp.{uuid.uuid4().hex}")
                src.rename(temp)
                temp.rename(dst)
                print(f"Renamed (case-only) {src} -> {dst}")
            else:
                src.rename(dst)
                print(f"Renamed {src} -> {dst}")
        except Exception as e:
            print(f"Failed to rename {src} -> {dst}: {e}")

    print("Done.")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Lowercase filenames under a directory (safe dry-run by default).")
    parser.add_argument("--path", "-p", default="static/icons", help="Base directory to process (default: static/icons)")
    parser.add_argument("--apply", action="store_true", help="Apply the renames. Without this flag the script does a dry-run.")
    args = parser.parse_args(argv)

    base = Path(args.path).resolve()
    if not base.exists() or not base.is_dir():
        print(f"Error: base path does not exist or is not a directory: {base}")
        sys.exit(2)

    files = find_files(base)
    ops = plan_renames(files, base)
    do_rename(ops, args.apply)


if __name__ == "__main__":
    main()
