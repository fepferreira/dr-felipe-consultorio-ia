#!/bin/bash
set -e

# Usar wheels pré-compilados para evitar compilação
pip install --upgrade pip setuptools wheel
pip install --prefer-binary -r requirements.txt
