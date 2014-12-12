%{?scl:%scl_package fooplugin}
%{!?scl:%global pkg_name %{name}}

Name:		%{?scl_pkg_name}%{?!scl_pkg_name:fooplugin}
Version:	2.3
Release:	1%{?dist}
Summary:	Example of CLI package

Group:		Applications/System
License:	BSD
URL:		http://example.com

%description
This is an example of an extension for package foo.
It adds some functionality to that package nad similates how
dynamic languages work with excensions.


%prep
%setup -c -T


%build

cat > %{pkg_name}.sh <<EOF
#!/bin/sh
echo "This is extension called %{name}."
EOF

%install
mkdir -p %{buildroot}%{_datadir}/%{pkg_name}

install -m 0755 %{pkg_name}.sh %{buildroot}%{_datadir}/%{pkg_name}


%files
%{_datadir}/%{pkg_name}


%changelog
* Mon Dec 01 2014 Honza Horak <hhorak@redhat.com> - 1-1
- initial packaging

