#!/bin/bash

echo $1
echo $2

if [ "$1" == "" ] ; then
    echo "Usage: $0 [repository directory] [package name]"
    exit 1
fi
if [ "$2" == "" ] ; then
    echo "Usage: $0 [repository directory] [package name]"
    exit 1
fi


PKG=$2
REPO=$1
TAG=$3

echo "Preparing package structure..."
mkdir -p /tmp/pkg/$PKG/usr/lib/cc1/$PKG
cp -r $REPO/pkg/$PKG/* /tmp/pkg/$PKG/
cp -r $REPO/src/$PKG/* /tmp/pkg/$PKG/usr/lib/cc1/$PKG
rm /tmp/pkg/$PKG/usr/lib/cc1/$PKG/config.py

# copy Ubuntu specific files
cp -r $REPO/pkg_ubuntu/$PKG/* /tmp/pkg/$PKG/

echo "Changing permissions..."
chown -R root:root /tmp/pkg/$PKG/
chown -R 331:331 /tmp/pkg/$PKG/etc/cc1/$PKG
chown -R 331:331 /tmp/pkg/$PKG/usr/lib/cc1/$PKG
chown -R 331:331 /tmp/pkg/$PKG/var/lib/cc1/ || true 2> /dev/null
chmod a+rx /tmp/pkg/$PKG/usr/sbin/* || true 2> /dev/null

chmod a+x /tmp/pkg/$PKG/DEBIAN/preinst || true
chmod a+x /tmp/pkg/$PKG/DEBIAN/postinst || true
chmod a+x /tmp/pkg/$PKG/DEBIAN/prerm || true
chmod a+x /tmp/pkg/$PKG/DEBIAN/postrm || true

BUILD_NUMBER=$TAG

sed -i "s/BUILD_NUMBER/$BUILD_NUMBER/" /tmp/pkg/$PKG/DEBIAN/control

echo "Calculating md5sums of files..."
md5sum `find /tmp/pkg/$PKG -type f ! -path "/tmp/pkg/$PKG/DEBIAN/*"` | sed -r "s/\/tmp\/pkg\/$PKG//" > /tmp/pkg/$PKG/DEBIAN/md5sums

dpkg-deb --build /tmp/pkg/$PKG/

VERSION=`cat /tmp/pkg/$PKG/DEBIAN/control | grep Version | cut -d ' ' -f 2`
mv /tmp/pkg/$PKG.deb $PKG-$VERSION.deb
lintian $PKG.deb >> $PKG-$VERSION.log
