#!/bin/bash
sphinx-build -M markdown ./source build
cp build/markdown/index.md ./README.md