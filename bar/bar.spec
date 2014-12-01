%{?scl:%scl_package bar}

Name:		%{?scl_pkg_name}%{?!scl_pkg_name:bar}
Version:	1
Release:	1%{?dist}
Summary:	Example of depended package

Group:		Applications/Databases
License:	BSD
URL:		http://example.com


%description
Some nice information about package %{name}


%build
cat > bar-run <<EOF
#!/bin/sh
echo "Hello, my name is %{name}, calling bar:"
bar-run
EOF


%install
mkdir -p %{buildroot}%{_bindir}
install -m 0755 bar-run %{buildroot}%{_bindir}/bar-run


%files
%{_bindir}/bar-run


%changelog
* Fri Jan 25 2013 Honza Horak <hhorak@redhat.com> - 1-1
- initial packaging

