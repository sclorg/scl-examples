#!/bin/sh

NAME=foo

# get version
VERSION_MAJOR=$(grep -e 'FOO_VERSION_MAJOR' CMakeLists.txt | sed -e 's/^.*FOO_VERSION_MAJOR[[:space:]]*\([[:digit:]]*\).*/\1/')
VERSION_MINOR=$(grep -e 'FOO_VERSION_MINOR' CMakeLists.txt | sed -e 's/^.*FOO_VERSION_MINOR[[:space:]]*\([[:digit:]]*\).*/\1/')
VERSION_PATCH=$(grep -e 'FOO_VERSION_PATCH' CMakeLists.txt | sed -e 's/^.*FOO_VERSION_PATCH[[:space:]]*\([[:digit:]]*\).*/\1/')
VERSION="${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_PATCH}"

# create dir for archive
archive_dir="${NAME}-${VERSION}"
mkdir -p "$archive_dir/foo-src"
cp CMakeLists.txt foo-daemon.service.in foo-daemon.sh foo-run.sh "$archive_dir/foo-src"

# create archive
tar czf "${NAME}-${VERSION}.tar.gz" "$archive_dir"

# clean up
rm -rf "$archive_dir"

# report output
echo ${NAME}-${VERSION}.tar.gz
