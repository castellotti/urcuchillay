#!/bin/bash

OUTDATED_PACKAGES=$(pip list --outdated | awk '{print $1"=="$2}')

# shellcheck disable=SC2068
for package in ${OUTDATED_PACKAGES[@]}; do
    pip install --upgrade "${package}"
done
