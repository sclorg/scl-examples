%{?scl:%scl_package foo}
%{!?scl:%global pkg_name %{name}}

%if 0%{?scl:1}
%global scl_upper %{lua:print(string.upper(string.gsub(rpm.expand("%{scl}"), "-", "_")))}
%endif

%global daemonname %{?scl_prefix}%{pkg_name}-daemon.service

Name:		%{?scl_prefix}foo
Version:	4.2.1
Release:	2%{?dist}
Summary:	Example of CLI package

Group:		Applications/System
License:	BSD
URL:		http://example.com

Source0:	https://github.com/sclorg/scl-examples/archive/v%{version}/scl-examples-v%{version}.tar.gz
Source1:	scl-register-helper.sh

Patch0:		foo-sclenv.patch

%description
This is an example package to demonstrate a simple application and
daemon packaged as Software Collection.


%package	server
Summary:	Example of Server package with a daemon
Group:		Applications/System

%description server
This is an example package to demonstrate a simple application and
daemon packaged as Software Collection.


%prep
%setup -q  -n scl-examples-%{version}

%if 0%{?scl:1}
%patch0 -p1 -b .sclenv
%endif

cp %{SOURCE1} .

%build
pushd foo-src
%cmake \
%if 0%{?scl:1}
	-DSCL_NAME="%{?scl}" \
	-DSCL_NAME_UPPER="%{?scl_upper}" \
	-DROOT_BINDIR="%{_root_bindir}" \
	-DSCL_SCRIPTS="%{?_scl_scripts}" \
%endif
	.
make
popd

%install
pushd foo-src
make DESTDIR=%{buildroot} install
popd

%if 0%{?scl:1}
mv %{buildroot}%{_unitdir}/%{pkg_name}-daemon.service \
	%{buildroot}%{_unitdir}/%{daemonname}
%endif

mkdir -p %{buildroot}%{_sysconfdir}
touch %{buildroot}%{_sysconfdir}/%{pkg_name}-daemon.cnf

%if 0%{?scl:1}
#include helper script for creating register stuff
source %{_sourcedir}/scl-register-helper.sh

# configure variables for the helper function scl_reggen
export _SR_BUILDROOT=%{buildroot}
export _SR_SCL_SCRIPTS=%{?_scl_scripts}

# backup files and generate register scripts for -server package
scl_reggen %{pkg_name}-server --cpfile %{_unitdir}/%{daemonname}
scl_reggen %{pkg_name}-server --selinux %{_unitdir}/%{daemonname} \
	%{_unitdir}/%{pkg_name}-daemon.service
scl_reggen %{pkg_name}-server --cpfile %{_sysconfdir}/%{pkg_name}-daemon.cnf
scl_reggen %{pkg_name}-server --runafterregister 'systemctl daemon-reload'
scl_reggen %{pkg_name}-server --runafterderegister 'systemctl daemon-reload'

# generate a configuration file for daemon
cat << EOF | tee -a %{buildroot}%{?_scl_scripts}/service-environment
# Services are started in a fresh environment without any influence of user's
# environment (like environment variable values). As a consequence,
# information of all enabled collections will be lost during service start up.
# If user needs to run a service under any software collection enabled, this
# collection has to be written into %{scl_upper}_SCLS_ENABLED variable
# in %{?_scl_scripts}/service-environment.
%{scl_upper}_SCLS_ENABLED="%{scl}"
EOF
%endif #scl

%post server
%systemd_post %{daemonname}
%{?scl:%{?_scl_scripts}/register.d/*.%{pkg_name}-server.selinux-set}
%{?scl:%{?_scl_scripts}/register.d/*.%{pkg_name}-server.selinux-restore}

%files
%{_bindir}/%{pkg_name}-run

%files server
%{_bindir}/%{pkg_name}-daemon
%{_unitdir}/%{daemonname}
%config(noreplace) %{_sysconfdir}/%{pkg_name}-daemon.cnf
%if 0%{?scl:1}
%{?_scl_scripts}/register.d/*.%{pkg_name}-server.*
%{?_scl_scripts}/deregister.d/*.%{pkg_name}-server.*
%{?_scl_scripts}/register.content/%{_sysconfdir}/%{pkg_name}-daemon.cnf
%{?_scl_scripts}/register.content/%{_unitdir}/%{daemonname}
%config(noreplace) %{?_scl_scripts}/service-environment
%endif #scl


%changelog
* Tue Jan 20 2015 Honza Horak <hhorak@redhat.com>
- Initial register implementation

* Mon Dec 01 2014 Honza Horak <hhorak@redhat.com> - 1-1
- initial packaging

