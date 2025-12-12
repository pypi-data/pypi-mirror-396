"""
MTF (Modular Test Framework) package initializer.

When this module is imported, the contents of the top‑level README.md are printed
to the console. This provides a quick overview of the framework without needing
to manually open the file.

The implementation safely reads the README relative to the package location.
If the file cannot be read, the import will continue silently.
"""

import pathlib
import sys

def _display_readme():
    """Read the top‑level README.md and display it.
    If the Rich library is available, render the markdown using Rich for rich‑text output.
    Otherwise, fall back to plain stdout printing."""
    package_dir = pathlib.Path(__file__).resolve().parent
    readme_path = package_dir.parent.parent / "README.md"
    try:
        with readme_path.open(encoding="utf-8") as f:
            content = f.read()
        try:
            from rich.console import Console
            from rich.markdown import Markdown
            Console().print(Markdown(content))
        except Exception:
            # Rich not available; fallback to plain text
            print(content, file=sys.stdout)
    except Exception as ex:
        print(f"Warning: Could not read README.md: {ex}", file=sys.stderr)

# Execute the display when the package is imported
_display_readme()
