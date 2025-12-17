#!/bin/bash

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

sphinx-apidoc --force --module-first -o source/modules ../src ../src/interregnum/tests/* ../src/z*
