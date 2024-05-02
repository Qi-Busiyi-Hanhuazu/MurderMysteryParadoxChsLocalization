#!/bin/bash

pushd $(dirname $(dirname "$0"))

if [ ! -f original_files/scenario/LB_chapter1.ks ]; then
  7z x -ooriginal_files original_files/original_files.7z
fi

python scripts/convert_others_data.py
python scripts/convert_scenario.py

cp -rf others/* out/

pushd out
zip -q -r ../patch.zip ./*
popd

mv patch.zip patch.xzp

popd