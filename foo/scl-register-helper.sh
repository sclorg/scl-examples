#!/bin/sh

#export _SR_BUILDROOT=%{buildroot}
#export _SR_SCL_SCRIPTS=%{?_scl_scripts}

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
