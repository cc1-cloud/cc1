#!/bin/bash

REPO_DIR="/storage/repo/cc1/"
REPREPRO_DIR="/storage/repo/packages"

# Copy information about package from wheezy to another distributions
for PKG in `reprepro -b $REPREPRO_DIR list nightly | cut -d ' ' -f 2` ; do
    echo "Propagating $PKG to..."
    for DIST in `cat $REPREPRO_DIR/conf/distributions | grep Codename | cut -d ' ' -f 2` ; do
        # Get name of package (cc1- and name of pakcage, e.g. node-2.0); version is skipped here
        if [ "$DIST" != "nightly" ] ; then
            echo -e "\t...to $DIST"
            reprepro -b $REPREPRO_DIR copy $DIST nightly $PKG
        fi
    done
    echo ""
done

