#!/usr/bin/env bash

pip install --no-deps --force-reinstall -e . \
    && cd docs \
    && rm -f api/_styles-quartodoc.css api/_sidebar.yml *.qmd \
    && quartodoc build && quartodoc interlinks && quarto render \
    && cd .. \
    && pip uninstall -y munch-group-library
