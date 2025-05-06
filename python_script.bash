#!/usr/bin/env bash

output=all_python_files.txt
rm -f "$output"

# Récupère le répertoire d'exécution (working directory)
root="$(pwd)"

find . \
  -type f \
  -name '*.py' \
  ! -path '*/__pycache__/*' \
  ! -path '*/migrations/*' \
| while IFS= read -r file; do
    # supprime le "./" en début de chemin
    rel="${file#./}"
    # affiche le chemin complet depuis le répertoire d'exécution
    echo "===== $root/$rel =====" >> "$output"
    cat "$file"               >> "$output"
    echo                       >> "$output"
  done
