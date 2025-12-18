from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Union

try:
    from importlib.resources import files as ir_files
except ImportError:
    from importlib_resources import files as ir_files  # Python < 3.9


def _walk_traversable(root):
    stack = [(root, Path())]
    while stack:
        node, rel = stack.pop()
        if node.is_dir():
            for child in node.iterdir():
                stack.append((child, rel / child.name))
        else:
            yield node, rel


def copy_packaged_tree_flat(
    package_module,
    resource_dir: str,
    dst_dir: Union[str, os.PathLike],
    overwrite: bool = False,
) -> None:
    dst_root = Path(dst_dir)
    dst_root.mkdir(parents=True, exist_ok=True)

    pkg_root = ir_files(package_module)
    root = pkg_root.joinpath(resource_dir)

    try:
        entries = list(root.iterdir())
    except Exception as e:
        raise FileNotFoundError(
            f"Resource directory '{resource_dir}' not found in package '{package_module.__name__}'"
        ) from e

    if not entries:
        raise FileNotFoundError(
            f"Resource directory '{resource_dir}' is empty in package '{package_module.__name__}'"
        )

    for node, rel_path in _walk_traversable(root):
        out = dst_root / rel_path
        out.parent.mkdir(parents=True, exist_ok=True)

        if out.exists() and not overwrite:
            continue

        with node.open("rb") as src, out.open("wb") as dst_f:
            shutil.copyfileobj(src, dst_f)

if __name__ == "__main__":
    import squidient  # IMPORTANT: import the module, don't pass a string
    copy_packaged_tree_flat(squidient, "data", ".", overwrite=True)
    copy_packaged_tree_flat(squidient, "utils", "src-remote/utils/", overwrite=True)
    print("OK: copied squidient/data/* into current directory")