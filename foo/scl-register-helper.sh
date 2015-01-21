#!/bin/sh
#
# License: BSD
# Author: Honza Horak <hhorak@redhat.com>
# URL: https://github.com/sclorg/scl-examples/blob/master/foo/scl-register-helper.sh
#
# This script defines a shell function that helps SCL packagers to generate
# scripts for `scl register` feature. This feature is used in caes where /opt
# is mounted using NFS and we want to use the collection from /opt still on NFS
# client.
#
# In this case `scl register` is called, which creates basic necessary
# configuration file to let scl tool to see the collection, but collections
# need to handle the rest themselves. So, in cases where collections need some
# special files outside of /opt they need to back-up such files during build
# and then provide a script that copies or creates those files during `scl register`
# call. This tool helps to generate scripts for both these cases.
#
# This helper script counts with the following structure:
#
# /opt/<vendor>/<sclname>/register.content
#   location for all backed-up files in the collection
#
# /opt/<vendor>/<sclname>/register.content/usr/systemd/system/<daemonname>
#   example of backed-up systemd service file
#
# /opt/<vendor>/<sclname>/register
#   the only script in whole collection run by `scl register`; NOOP if this
#   script does not exist
#   to allow different packages to add own stuff to be copied, this script
#   executes all scripts from ./register.d
#
# /opt/<vendor>/<sclname>/register.d
#   location for scripts relevant for particular packages, run by main register script
#   numbers in the beginning of the script name ensure correct order of the scripts
#
# /opt/<vendor>/<sclname>/register.d/10.<pkgname>.<scripttype>
#   example of a script releavant for package <pkgname>, the part <scripttype>
#   only makes the readability easier
#   those files need to be packaged into the particular package
#
# /opt/<vendor>/<sclname>/deregister
# /opt/<vendor>/<sclname>/deregister.d
#   main script and directory for particular scripts with the same purpose as register,
#   except it works for `scl deregister` command
#
# How to use it:
# --------------
#
# Define those environment variables in the script where this file is sourced, usually
# in %%install section
#   export _SR_BUILDROOT=%%{buildroot}
#   export _SR_SCL_SCRIPTS=%%{?_scl_scripts}
#
# Source the script:
#   source %{_sourcedir}/scl-register-helper.sh
#
# For back-up a file use it like this (without %%{buildroot}):
#   scl_reggen <pkgname> --cpfile <file-to-backup>
#     which not only creates a file under register.content, but also generates
#     scripts XX.<pkgname>.content-create into register.d
#     and XX.<pkgname>.content-remove into deregister.d.
#
# For setting up SELinux context for a file with SELinux equivalency
# (semanage fcontext -a -e <src> <dst>):
#   scl_reggen <pkgname> --selinux <pathdst> <pathsrc>
#     which generates scripts XX.<pkgname>.selinux-set
#     and XX.<pkgname>.selinux-restore into register.d.
#
# For creating dir, touching a file, running chmod, chown or arbitrary
# commands after register and deregister, there are the following commands
# options (in the same order):
#
#   scl_reggen <pkgname> --mkdir <path>
#   scl_reggen <pkgname> --touch <path>
#   scl_reggen <pkgname> --chmod <path> <chmod-args>
#   scl_reggen <pkgname> --chown <path> <chown-args>
#   scl_reggen <pkgname> --runafterregister <cmd>
#   scl_reggen <pkgname> --runafterderegister <cmd>
#
# The scripts and backed-up files then must be included into particular packages:
# %%files <pkgname>
# %%{?_scl_scripts}/register.d/*.<pkgname>.*
# %%{?_scl_scripts}/deregister.d/*.<pkgname>.*
# %%{?_scl_scripts}/register.content/%%{_unitdir}/<daemonname>
#
# Tip:
# Since we need to set the SELinux also when installing the collection normally, we can use the following files to be run as part of the %%post script, like this:
#   %%post server
#   %%{?scl:%%{?_scl_scripts}/register.d/*.<pkgname>.selinux-set}
#   %%{?scl:%%{?_scl_scripts}/register.d/*.<pkgname>-server.selinux-restore}
#
# Caution:
# Don't forget to set the following variables: _SR_BUILDROOT and
# _SR_SCL_SCRIPTS as described above.

scl_reggen(){

  # helper function to save some chars
  add2file(){
    if ! [ -f "${2}" ] ; then
      mkdir -p $(dirname "${2}")
      echo "#!/bin/sh" >"${2}"
      chmod a+x "${2}"
    fi
    echo "${1}" >>"${2}"
  }

  package=$1
  [ -z "$package" ] && echo "No package specified." && return 1
  shift

  while [ -n "$1" ] ; do
    action="$1"
    shift

    case "$action" in

      --cpfile )
        file=$1
        shift
        [ -z "$file" ] && echo "No file specified for cpfile." && return 1
        # make dir and cp file
        mkdir -p $(dirname ${_SR_BUILDROOT}${_SR_SCL_SCRIPTS}/register.content${file})
        cp ${_SR_BUILDROOT}${file} ${_SR_BUILDROOT}${_SR_SCL_SCRIPTS}/register.content${file}
        # add command to script that handles copying file on register
        add2file "cp -n ${_SR_SCL_SCRIPTS}/register.content${file} ${file}" \
                 ${_SR_BUILDROOT}${_SR_SCL_SCRIPTS}/register.d/50.${package}.content-create
        # add command to script that handles removing file on deregister
        add2file "rm -f ${file}" ${_SR_BUILDROOT}${_SR_SCL_SCRIPTS}/deregister.d/50.${package}.content-remove
        ;;

      --selinux )
        dst=$1
        src=$2
        shift 2
        [ -z "$dst" ] && echo "No src or dst specified for selinux." && return 1
        # store rule for setting selinux
        add2file "semanage fcontext -a -e \"$src\" \"$dst\" >/dev/null 2>&1 || :" \
                 ${_SR_BUILDROOT}${_SR_SCL_SCRIPTS}/register.d/20.${package}.selinux-set
        # store rule for restoring selinux
        add2file "restorecon -R \"$dst\" >/dev/null 2>&1 || :" \
                 ${_SR_BUILDROOT}${_SR_SCL_SCRIPTS}/register.d/80.${package}.selinux-restore
        ;;

      --mkdir )
        dst=$1
        shift
        [ -z "$dst" ] && echo "No dst specified for mkdir." && return 1
        # store command for creating directory
        add2file "mkdir -p ${dst}" ${_SR_BUILDROOT}${_SR_SCL_SCRIPTS}/register.d/40.${package}.content-create
        # store command for removing directory if empty, ignore errors
        add2file "rmdir --ignore-fail-on-non-empty -p ${dst}" \
                 ${_SR_BUILDROOT}${_SR_SCL_SCRIPTS}/deregister.d/60.${package}.content-remove
        ;;

      --touch )
        file=$1
        shift
        [ -z "$file" ] && echo "No file specified for touch." && return 1
        # store command for creating file
        add2file "touch ${file}" ${_SR_BUILDROOT}${_SR_SCL_SCRIPTS}/register.d/50.${package}.content-create
        # add command to script that handles removing file on deregister
        add2file "rm -f ${file}" ${_SR_BUILDROOT}${_SR_SCL_SCRIPTS}/deregister.d/50.${package}.content-remove
        ;;

      --chmod )
        dst=$1
        args=$2
        shift 2
        [ -z "$args" ] && echo "No dst or args specified for chmod." && return 1
        # store command for chmod
        add2file "chmod $args ${dst}" ${_SR_BUILDROOT}${_SR_SCL_SCRIPTS}/register.d/60.${package}.attrs
        ;;

      --chown )
        dst=$1
        args=$2
        shift 2
        [ -z "$args" ] && echo "No dst or args specified for chown." && return 1
        # store command for chown
        add2file "chown $args ${dst}" ${_SR_BUILDROOT}${_SR_SCL_SCRIPTS}/register.d/60.${package}.attrs
        ;;

      --runafterregister )
        cmd=$1
        shift
        [ -z "$cmd" ] && echo "No cmd specified for run." && return 1
        # store command for running after
        add2file "$cmd" ${_SR_BUILDROOT}${_SR_SCL_SCRIPTS}/register.d/90.${package}.run
        ;;

      --runafterderegister )
        cmd=$1
        shift
        [ -z "$cmd" ] && echo "No cmd specified for run." && return 1
        # store command for running after
        add2file "$cmd" ${_SR_BUILDROOT}${_SR_SCL_SCRIPTS}/deregister.d/90.${package}.run
        ;;

      *)
        echo "Wrong action $*"
        return 1
        ;;
    esac
  done
}
