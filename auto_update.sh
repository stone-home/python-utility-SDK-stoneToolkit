#!/usr/bin/env bash

poetry lock --no-update && \\
git add . && \\
git commit -m "build(poetry): update poetry.lock" && \\
cz dump && \\
git push origin trunk --tags