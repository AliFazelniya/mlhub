#!/usr/bin/env bash
set -euo pipefail

FILE="mnist_train.csv"
ARCHIVE="${FILE}.xz"

# Move to the script's directory so it works from anywhere
cd "$(dirname "$0")"

if [[ -f "$FILE" ]]; then
  echo "Already exists: $FILE"
  exit 0
fi

if [[ ! -f "$ARCHIVE" ]]; then
  echo "Missing archive: $ARCHIVE"
  echo "Make sure ${ARCHIVE} is in this directory."
  exit 1
fi

echo "Restoring $FILE from $ARCHIVE ..."
xz -dk "$ARCHIVE"   # -d decompress, -k keep .xz
echo "Done."
ls -lh "$FILE"
