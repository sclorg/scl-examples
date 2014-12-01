Example of Software Collection meta package
===========================================

Software Collection `foo1` consists of two package, so there are two
RPM SPEC files in this directory:

  * foo-meta.spec is an RPM SPEC file for SCL meta package
  * foo.spec is an RPM SPEC file for a simple CLI utility and a simple
    daemon


Building SCL meta package for `foo1` collection
-----------------------------------------------

The file `foo-meta.spec` is an RPM SRPM meta package, which is a base
for the `foo1` Software Collection. In order to build this package,
use `rpmbuild` or `mock` as for ordinary package:

    $ rpmbuild -ba foo-meta.spec

Building `foo1` meta package results in `foo1`, `foo1-scldevel`,
`foo1-runtime` and `foo1-build` packages.

Please, notice, that `scl-utils-build` needs to be installed before
building, otherwise the spec file is not parsed properly. Thus, it is
a good idea to have `scl-utils-build` in the basic buildroot.


Building a package into the `foo1` collection
-------------------------------------------

After building `foo` SCL meta package, you may now build the example package
for this SCL. You can either install `foo1-build` package, that defines `%scl`
macro for all builds or define this macro on the command-line.

    $ rpmbuild -ba --define 'scl foo1' foo.spec

This results into `foo1-foo` package.

When building in some infrastructure (e.g. in koji, copr), this macro
is usually defined by installing `foo1-build` package in the buildroot.
Doing so the `scl` macro is defined for all packages.


Installing the `foo1` SCL
-------------------------

After you have built all necessary packages, install the main package from
the `foo1` meta package and all its dependencies.

    $ yum install foo1


How to use the `foo1` SCL
-------------------------

In order to run the CLI application from `foo1` collection, use `scl` utility
and specify the collection for enabling:

    $ scl enable foo1 'foo-run'

The package `foo1-server` includes a deamon started using the init system and
thus started in clean environment. Thus, setting a proper environment needs
to happen when starting the daemon and the service then may be run without
`scl` utility:

    # systemctl start foo1-foo-daemon


More information about software collections:
https://www.softwarecollections.org/en/docs/guide/
