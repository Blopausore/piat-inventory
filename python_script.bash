output=all_python_files.txt
rm -f "$output"
find . \
  -type f \
  -name '*.py' \
  ! -path '*/__pycache__/*' \
  ! -path '*/migrations/*' \
| while IFS= read -r file; do
    echo "===== $file =====" >> "$output"
    cat "$file"           >> "$output"
    echo -e "\n"         >> "$output"
  done


