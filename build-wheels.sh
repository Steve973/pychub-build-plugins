#!/bin/bash

set -e

for sp in hatch pdm poetry; do
  pushd "$sp"
  poetry build -o ./dist/
  popd
done
