#!/usr/bin/env bash
set -euo pipefail

OUT_MD="artifacts/phase3_evidence.md"
OUT_PYTEST="artifacts/pytest_phase3.log"
OUT_MAIN="artifacts/main_phase3.log"

mkdir -p artifacts

# Dynamically find ALL project source files to ensure nothing is missed.
# We include .py and .json files from src, tests, and data.
# We also include critical root files.

FILES=("main.py" "requirements.txt")

# Use process substitution to append found files to the array
while IFS= read -r file; do
    FILES+=("$file")
done < <(find src tests data -type f \( -name "*.py" -o -name "*.json" \) | sort)

# Helper: safe repo tree
print_tree() {
  if command -v tree >/dev/null 2>&1; then
    tree -a -I 'artifacts|__pycache__|.pytest_cache|.venv|.git'
  else
    find . -maxdepth 4 -not -path '*/.*' -not -path './artifacts*' | sort
  fi
}

# Generate markdown evidence
{
  echo "# Complete Project Evidence"
  echo "Generated timestamp: $(date)"
  echo
  echo "## Environment"
  echo '```'
  python --version
  echo '```'

  echo
  echo "## Repo tree"
  echo '```'
  print_tree
  echo '```'

  echo
  echo "## Source Code (FULL TEXT - Dynamic Scan)"
  for f in "${FILES[@]}"; do
    echo
    echo "### $f"
    if [[ -f "$f" ]]; then
      echo '```'
      sed -n '1,99999p' "$f"
      echo '```'
    else
      echo "_MISSING_"
    fi
  done

  echo
  echo "## Pytest output (literal)"
  echo '```'
  if [[ -f "$OUT_PYTEST" ]]; then
      cat "$OUT_PYTEST"
  else
      echo "Log file $OUT_PYTEST not found."
  fi
  echo '```'

  echo
  echo "## Pipeline run output (literal)"
  echo '```'
  if [[ -f "$OUT_MAIN" ]]; then
      cat "$OUT_MAIN"
  else
      echo "Log file $OUT_MAIN not found."
  fi
  echo '```'

} > "$OUT_MD"

echo "Wrote $OUT_MD with ${#FILES[@]} files."
