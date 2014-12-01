Simple example of SCL meta package that depends on SCL foo1
===========================================================

Software Collection `bar1` consists of two package, so there are two
RPM SPEC files in this directory:

  * bar-meta.spec is an RPM SPEC file for SCL meta package
  * bar.spec is an RPM SPEC file with a simple CLI utility that
    demonstrates usage of depended SCL

A depended collection suites for use cases, where some package or
software collection needs some functionality from a different collection
and you do not want to duplicate code in both collections.


Building SCL meta package for bar collection
--------------------------------------------

In order to build the `bar` meta package, you need to have already installed
foo1-scldevel from a directory `../foo`, because this software collection
depends on `foo1` software collection

Then, build this package as ordinary package:

    $ rpmbuild -ba bar-meta.spec

Building `bar1` meta package results in `bar1`, `bar1-scldevel`,
`bar1-runtime` and `bar1-build` packages.

Please, notice, that `scl-utils-build` needs to be installed before
building, otherwise the spec file is not parsed properly. Thus, it is
a good idea to have `scl-utils-build` in the basic buildroot.


Building a package into the `bar1` collection
---------------------------------------------

After building `bar` SCL meta package, you may now build the example package
for this SCL. You can either install `bar1-build` package, that defines `%scl`
macro for all builds or define this macro on the command-line.

    $ rpmbuild -ba --define 'scl bar1' bar.spec

This results into `bar1-bar` package.


Installing the `bar1` SCL
-------------------------

After you have built all necessary packages, install the main package from
the `bar1` meta package and all its dependencies.

    $ yum install bar1


How to run the `bar1` Software Collection
-----------------------------------------

Properly built depending software collection `bar1` then ensures that
the parent collection `foo1` is enabled as soon as collection `bar1` is
enabled.

    $ scl enable bar1 -- scl_enabled foo1 && echo YES
    YES

