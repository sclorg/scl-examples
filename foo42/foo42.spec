# Define SCL name
%{!?scl_name_base: %global scl_name_base foo}
%{!?version_major: %global version_major 4}
%{!?version_minor: %global version_minor 2}
%{!?scl_name_version: %global scl_name_version %{version_major}%{version_minor}}
%{!?scl: %global scl %{scl_name_base}%{scl_name_version}}

# Turn on new layout -- prefix for packages and location
# for config and variable files
# This must be before calling %%scl_package
%{!?nfsmountable: %global nfsmountable 1}
%{!?scl_vendor_in_name: %global scl_vendor_in_name 1}

# Define SCL macros
%{?scl_package:%scl_package %scl}

# do not produce empty debuginfo package
%global debug_package %{nil}

Summary: Package that installs %{scl}
Name: %{?scl_meta_name}%{!?scl_meta_name:%scl}
Version: 1.0
Release: 1%{?dist}
License: GPLv2+
Group: Applications/File
Source0: README
Source1: LICENSE
Requires: scl-utils
Requires: %{?scl_pkg_prefix}foo
BuildRequires: scl-utils-build help2man

%description
This is the main package for %{scl} Software Collection, which installs
necessary packages to use foo package.

%package runtime
Summary: Package that handles %{scl} Software Collection.
Group: Applications/File
Requires: scl-utils

%description runtime
Package shipping essential scripts to work with %{scl} Software Collection.

%package build
Summary: Package shipping basic build configuration
Group: Applications/File
Requires: scl-utils-build

%description build
Package shipping essential configuration macros to build %{scl} Software
Collection or packages depending on %{scl} Software Collection.

%package scldevel
Summary: Package shipping development files for %{scl}

%description scldevel
Package shipping development files, especially usefull for development of
packages depending on %{scl} Software Collection.

%prep
%setup -c -T

# This section generates README file from a template and creates man page
# from that file, expanding RPM macros in the template file.
cat >README <<'EOF'
%{expand:%(cat %{SOURCE0})}
EOF

# copy the license file so %%files section sees it
cp %{SOURCE1} .

%build
# generate a helper script that will be used by help2man
cat >h2m_helper <<'EOF'
#!/bin/bash
[ "$1" == "--version" ] && echo "%{?scl_name} %{version} Software Collection" || cat README
EOF
chmod a+x h2m_helper
# generate the man page
help2man -N --section 7 ./h2m_helper -o %{?scl_name}.7

%install
%{?scl_install}

# create and own dirs not covered by %%scl_install and %%scl_files
%if 0%{?rhel} <= 6
mkdir -p %{buildroot}%{_datadir}/aclocal
%else
mkdir -p %{buildroot}%{_mandir}/man{1,7,8}
%endif

cat >> %{buildroot}%{?_scl_scripts}/enable << EOF
export PATH=%{_bindir}\${PATH:+:\${PATH}}
export LIBRARY_PATH=%{_libdir}\${LIBRARY_PATH:+:\${LIBRARY_PATH}}
export LD_LIBRARY_PATH=%{_libdir}\${LD_LIBRARY_PATH:+:\${LD_LIBRARY_PATH}}
export MANPATH=%{_mandir}:\${MANPATH}
export CPATH=%{_includedir}\${CPATH:+:\${CPATH}}
EOF

# generate rpm macros file for depended collections
cat >> %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel << EOF
%%scl_%{scl_name_base} %{scl}
%%scl_prefix_%{scl_name_base} %{?scl_prefix}
%%scl_pkg_prefix_%{scl_name_base} %{?scl_pkg_prefix}
EOF

# generate a configuration file for daemon
cat >> %{buildroot}%{?_scl_scripts}/service-environment << EOF
# Services are started in a fresh environment without any influence of user's
# environment (like environment variable values). As a consequence,
# information of all enabled collections will be lost during service start up.
# If user needs to run a service under any software collection enabled, this
# collection has to be written into SCLNAME_SCLS_ENABLED variable in
# /opt/rh/sclname/service-environment.
$(printf '%%s' '%{scl}' | tr '[:lower:][:space:]' '[:upper:]_')_SCLS_ENABLED='%{scl}'
EOF

# install generated man page
mkdir -p %{buildroot}%{_mandir}/man7/
install -m 644 %{?scl_name}.7 %{buildroot}%{_mandir}/man7/%{?scl_name}.7

%post runtime
# Simple copy of context from system root to DSC root.
# In case new version needs some additional rules or context definition,
# it needs to be solved.
# Unfortunately, semanage does not have -e option in RHEL-5, so we would
# have to have its own policy for collection (inspire in mysql%{scl_name_version} package)
semanage fcontext -a -e / %{?_scl_root} >/dev/null 2>&1 || :
semanage fcontext -a -e %{_initddir}/food %{_initddir}/%{?scl_prefix}food >/dev/null 2>&1 || :
semanage fcontext -a -e %{_root_localstatedir}/log/food.log %{_localstatedir}/log/%{?scl_prefix}food.log >/dev/null 2>&1 || :
restorecon -R %{?_scl_root} >/dev/null 2>&1 || :
restorecon %{_initddir}/%{?scl_prefix}food >/dev/null 2>&1 || :
restorecon %{?_localstatedir}/log/food.log >/dev/null 2>&1 || :
selinuxenabled && load_policy || :

%files

%files runtime
%doc README LICENSE
%{?scl_files}
%if 0%{?rhel} <= 6
%{_datadir}/aclocal
%else
%{_mandir}/man*
%endif
%config(noreplace) %{?_scl_scripts}/service-environment
%{_mandir}/man7/%{?scl_name}.*

%files build
%doc LICENSE
%{_root_sysconfdir}/rpm/macros.%{scl}-config

%files scldevel
%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel

%changelog
* Mon Dec 01 2014 Honza Horak <hhorak@redhat.com> 1-1
- initial packaging

