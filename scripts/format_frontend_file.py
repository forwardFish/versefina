from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: python scripts/format_frontend_file.py <literal-path> <prettier-path>", file=sys.stderr)
        return 2

    literal_path = Path(sys.argv[1])
    prettier_path = sys.argv[2]
    source = literal_path.read_text(encoding="utf-8-sig")

    result = subprocess.run(
        f'pnpm --dir apps/web dlx prettier --stdin-filepath "{prettier_path}"',
        input=source,
        text=True,
        capture_output=True,
        encoding="utf-8",
        shell=True,
    )
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    if result.returncode != 0:
        return result.returncode

    literal_path.write_text(result.stdout, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
