%{?scl:%scl_package foo}
%{!?scl:%global pkg_name %{name}}

Name:		%{?scl_pkg_name}%{?!scl_pkg_name:foo}
Version:	1
Release:	1%{?dist}
Summary:	Example of CLI package

Group:		Applications/System
License:	BSD
URL:		http://example.com

%description
This is an example package to demonstrate a simple application and
daemon packaged as Software Collection.


%package	server
Summary:	Example of Server package with a daemon
Group:          Applications/System

%description server
This is an example package to demonstrate a simple application and
daemon packaged as Software Collection.


%build
cat > %{pkg_name}-run <<EOF
#!/bin/sh
echo "Hello, my name is %{name}."
EOF

cat > %{pkg_name}-daemon <<EOF
#!/bin/sh
echo "Deamon %{name} is running..."
while true ; do
  echo "Still running."
  sleep 10s
done
EOF


%install
mkdir -p %{buildroot}%{_bindir}
install -m 0755 %{pkg_name}-run %{buildroot}%{_bindir}/%{pkg_name}-run
install -m 0755 %{pkg_name}-daemon %{buildroot}%{_bindir}/%{pkg_name}-daemon


%files
%{_bindir}/%{pkg_name}-run

%files server
%{_bindir}/%{pkg_name}-daemon


%changelog
* Mon Dec 01 2014 Honza Horak <hhorak@redhat.com> - 1-1
- initial packaging

