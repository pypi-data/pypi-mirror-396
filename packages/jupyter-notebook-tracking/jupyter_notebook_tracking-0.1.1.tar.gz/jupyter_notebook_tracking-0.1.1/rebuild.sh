#!/bin/bash
pip install --editable "."
jupyter labextension develop . --overwrite
jlpm build