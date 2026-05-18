#!/usr/bin/env bash
set -euo pipefail

dry=false
if [[ "${1:-}" == -n || "${1:-}" == --dry-run ]]; then
  dry=true
  shift
fi
exts=(out err loc bibtex densities densitiesinfo gbw inp txt)
expr=()
for e in "${exts[@]}"; do expr+=( -name "*.$e" -o ); done
unset 'expr[-1]'
mapfile -t files < <(find functionals -type f -path 'functionals/*/*/out/*' \( "${expr[@]}" \) -print)
if [[ "$dry" == true ]]; then
  printf 'Dry run: will remove %s files from functionals/*/*/out/\n' "${exts[*]}"
  if [[ ${#files[@]} -eq 0 ]]; then
    echo 'No matching files'
  else
    printf '%s\n' "${files[@]}"
  fi
  exit 0
fi
if [[ ${#files[@]} -eq 0 ]]; then
  echo 'No matching files to delete.'
  exit 0
fi
printf 'Deleting %s files from functionals/*/*/out/:%s' "${exts[*]}" $'\n'
for f in "${files[@]}"; do rm -v "$f"; done
