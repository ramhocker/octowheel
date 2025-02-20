#!/bin/sh

if [ $# -ne 2 ]; then
  echo "Usage: ${0} <input-nes-file> <output-nes-file>"
  exit 1
fi


source_file="${1}"
target_file="${2}"

./src/hack-game.py \
  --no-harm \
  --timers       99 \
  --logo         images/patches/logo.png \
  --players      okto_patches-de/players \
  --puzzles      okto_patches-de/puzzlelist-octonauts \
  --title-text   okto_patches-de/title_text \
  --marquee      okto_patches-de/marquee_text \
  --custom-hacks okto_patches-de/custom_hacks.py \
  --loglevel     VERBOSE \
"${source_file}" "${target_file}"
