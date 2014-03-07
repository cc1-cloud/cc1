#!/bin/bash

if [ "$1" == "" ] ; then
    echo "Usage: $0 [repository]"
    exit 1
fi

packages=`ls -1 $1/pkg/`

for pkg in $packages ; do
    echo "################################################"
    echo "Building $pkg"
    bash $1/tools/build_deb.sh $1 $pkg
done


# Build packages index
# Example /etc/apt/sources.list entry:
dpkg-scanpackages . | gzip > Packages.gz

echo Add following line to /etc/apt/sources.list:
echo deb file://`pwd`/ ./
