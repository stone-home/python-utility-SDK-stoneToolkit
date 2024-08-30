#!/usr/bin/env bash

poetry lock&& \\
git add . && \\
git commit -m "build(poetry): update poetry.lock" && \\
cz bump && \\
git push origin trunk --tags
