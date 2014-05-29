#!/bin/bash

REPO_DIR="/storage/repo/cc1/"
REPREPRO_DIR="/storage/repo/packages"

# Iterate over each new tag
cd $REPO_DIR
TAGS=`git fetch --tags 2>&1 > /dev/null | grep "tag" | cut -d '>' -f 2`

echo $TAGS
for TAG in $TAGS ; do
    echo "Checking git repository - $TAG..."
    cd $REPO_DIR
    git checkout $TAG

    if [ ! -d /tmp/build/$TAG ] ; then
        mkdir -p /tmp/build/$TAG
    fi

    echo "Building packages..."
    cd /tmp/build/$TAG
    bash $REPO_DIR/tools/build_all.sh $REPO_DIR &> /var/log/packages_build.log

    for PKG in `ls -1 /tmp/build/$TAG/*.deb` ; do
        echo "Signing $PKG..."
        dpkg-sig --sign builder $PKG

        echo "Adding to repository..."
        reprepro -b $REPREPRO_DIR --ask-passphrase --keepunreferencedfiles includedeb nightly $PKG
    done
done

rm -rf /tmp/pkg
rm -rf /tmp/build
