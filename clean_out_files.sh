#!/usr/bin/env bash
set -euo pipefail

dry=false
[[ "${1:-}" == -n ]] && { dry=true; shift; }
exts=( "${@:-out err loc}" )
expr=()
for e in "${exts[@]}"; do expr+=( -name "*.$e" -o ); done
unset 'expr[-1]'
find functionals -type f -path 'functionals/*/*/out/*' \( "${expr[@]}" \) -print | { if [[ "$dry" == true ]]; then cat; else xargs -r rm -v; fi; }
