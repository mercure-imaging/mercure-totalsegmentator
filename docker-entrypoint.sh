#!/usr/bin/env bash
set -Eeo pipefail
echo "-- Starting TotalSegmentator..."
conda run --no-capture-output -n mercure-totalsegmentator python mercure-totalsegmentator -i $MERCURE_IN_DIR -o $MERCURE_OUT_DIR
echo "-- Done."