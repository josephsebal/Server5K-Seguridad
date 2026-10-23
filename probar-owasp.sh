#!/usr/bin/env bash
set -euo pipefail
repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
project_dir="${SERVER5K_DIR:-$(dirname "$repo_dir")/Server5K}"
if [[ ! -x "$project_dir/.venv/bin/python" ]]; then
  echo "No se encontró Python del proyecto en $project_dir/.venv/bin/python" >&2
  exit 1
fi
exec "$project_dir/.venv/bin/python" "$repo_dir/herramientas/probar_owasp_guiado.py" "$project_dir" "$@"
