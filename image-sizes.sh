#!/usr/bin/env bash

set -e

HD=$1

rm -rf images
[[ $HD = true ]] && mkdir -p images/160
mkdir -p images/96 images/64 images/40
