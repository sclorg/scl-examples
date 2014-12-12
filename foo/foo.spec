%{?scl:%scl_package foo}
%{!?scl:%global pkg_name %{name}}

Name:		%{?scl_pkg_name}%{?!scl_pkg_name:foo}
Version:	4.2.1
Release:	1%{?dist}
Summary:	Example of CLI package

Group:		Applications/System
License:	BSD
URL:		http://example.com

Source0:	%{pkg_name}-%{version}.tar.gz

%description
This is an example package to demonstrate a simple application and
daemon packaged as Software Collection.


%package	server
Summary:	Example of Server package with a daemon
Group:          Applications/System

%description server
This is an example package to demonstrate a simple application and
daemon packaged as Software Collection.


%prep
%setup -q 

%build
pushd foo-src
%cmake .
make
popd

%install
pushd foo-src
make DESTDIR=%{buildroot} install
popd

#mkdir -p %{buildroot}%{_unitdir}

#install -m 0644 %{pkg_name}-daemon.service %{buildroot}%{_unitdir}/%{pkg_name}-daemon.service


%files
%{_bindir}/%{pkg_name}-run

%files server
%{_bindir}/%{pkg_name}-daemon
%{_unitdir}/%{pkg_name}-daemon.service


%changelog
* Mon Dec 01 2014 Honza Horak <hhorak@redhat.com> - 1-1
- initial packaging

