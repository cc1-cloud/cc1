#!/bin/bash

if [ "$1" == "" ] ; then
    echo "Usage: $0 [repository]"
    exit 1
fi

packages=`ls -1 $1/pkg/`

for pkg in $packages ; do
    echo "################################################"
    echo "Building $pkg"
    bash $1/tools/build_ubu.sh $1 $pkg $2
done
