#!/bin/bash

# SPDX-FileCopyrightText: 2024 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

PROJECT="interregnum"
INIT_FILES="src/${PROJECT}/__init__.py"
DOC_FILES="doc/source/conf.py"

echoerr(){
    >&2 echo $1
}

usage(){
    echoerr "$0 <version>"
}

check_clean_wd(){
    git diff --quiet
    if [[ "$?" != "0" ]]
    then
        echoerr "The working directory is dirty. Aborting."
        exit 1
    fi
}

major_version(){
    echo $1 | sed -r 's/^([^\.]+(\.[^\.]+)?).*/\1/'
}

change_init(){
    for f in ${INIT_FILES}
    do
        sed -i -r -e "s/^(__version__ *= *)(.*)/\1'$1'/" $f
    done
}

change_docconf(){

    release=$1
    version=$(major_version ${release})

    for f in ${DOC_FILES}
    do
        sed -i -r -e "s/^(version *= *)(.*)/\1'${version}'/" \
                  -e "s/^(release *= *)(.*)/\1'${release}'/" \
                  $f
    done
}

change_version(){
    echo "$1" > VERSION
}

if [ -z "$1" ]
  then
    usage
    exit 1
fi

check_clean_wd &&
make local-test &&
#change_version $1 &&
# change_init $1 &&
# change_docconf $1 &&
make doc &&
git co -b release/$1 &&
git ci --all -m "version set to $1 [skip ci]" &&
echoerr "PROCESO EXITOSO. Nueva versión: $1"
