%define pkg_version 4.1
%define api_version 0.5.4

%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}
%{!?pyver: %define pyver %(%{__python} -c "import sys; v=sys.version_info[:2]; print '%d.%d'%v")}

%{!?tcl_version: %define tcl_version %(echo 'puts $tcl_version' | tclsh)}
%{!?tcl_sitearch: %define tcl_sitearch %{_prefix}/%{_lib}/tcl%{tcl_version}}

%define _exec_prefix %{nil}
%define _libdir /%{_lib}

# with speech dispatcher iff on Fedora:
%define with_speech_dispatcher 0%{?fedora}

Name: brltty
Version: %{pkg_version}
Release: 6%{?dist}
License: GPLv2+
Group: System Environment/Daemons
URL: http://mielke.cc/brltty/
Source: http://mielke.cc/brltty/releases/%{name}-%{version}.tar.gz
Patch4: brltty-cppflags.patch
Patch5: brltty-parallel.patch
Patch6: brltty-autoconf-quote.patch
BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
Summary: Braille display driver for Linux/Unix
BuildRequires: byacc glibc-kernheaders
BuildRequires: autoconf
# work around a bug in the install process:
Requires(post): coreutils

%description
BRLTTY is a background process (daemon) which provides
access to the Linux/Unix console (when in text mode)
for a blind person using a refreshable braille display.
It drives the braille display and provides complete
screen review functionality.
%if %{with_speech_dispatcher}
BRLTTY can also work with speech synthetizers; if you want to use it with
Speech Dispatcher, please install also package %{name}-speech-dispatcher.

%package speech-dispatcher
Summary: Speech Dispatcher driver for BRLTTY
Group: System Environment/Daemons
License: GPLv2+
BuildRequires: speech-dispatcher-devel
Requires: %{name} = %{pkg_version}-%{release}
%description speech-dispatcher
This package provides the Speech Dispatcher driver for BRLTTY.
%endif

%package xw
Summary: XWindow driver for BRLTTY
Group: System Environment/Daemons
License: GPLv2+
BuildRequires: libSM-devel libICE-devel libX11-devel libXaw-devel libXext-devel libXt-devel libXtst-devel
Requires: %{name} = %{pkg_version}-%{release}
%description xw
This package provides the XWindow driver for BRLTTY.

%package at-spi
Summary: AtSpi driver for BRLTTY
Group: System Environment/Daemons
# The data files are licensed under LGPLv2+, see the README file.
License: GPLv2+ and LGPLv2+
BuildRequires: at-spi-devel
Requires: %{name} = %{pkg_version}-%{release}
%description at-spi
This package provides the AtSpi driver for BRLTTY.

%package -n brlapi
Version: %{api_version}
Group: Applications/System
License: LGPLv2+
Summary: Appliation Programming Interface for BRLTTY
Requires: %{name} = %{pkg_version}-%{release}
%description -n brlapi
This package provides the run-time support for the Application
Programming Interface to BRLTTY.

Install this package if you have an application which directly accesses
a refreshable braille display.

%package -n brlapi-devel
Version: %{api_version}
Group: Development/System
License: LGPLv2+
Requires: brlapi = %{api_version}-%{release}
Summary: Headers, static archive, and documentation for BrlAPI

%description -n brlapi-devel
This package provides the header files, static archive, shared object
linker reference, and reference documentation for BrlAPI (the
Application Programming Interface to BRLTTY).  It enables the
implementation of applications which take direct advantage of a
refreshable braille display in order to present information in ways
which are more appropriate for blind users and/or to provide user
interfaces which are more specifically atuned to their needs.

Install this package if you are developing or maintaining an application
which directly accesses a refreshable braille display.

%package -n tcl-brlapi
Version: %{api_version}
Group: Development/System
License: LGPLv2+
Requires: brlapi = %{api_version}-%{release}
BuildRequires: tcl-devel
Summary: Tcl binding for BrlAPI
%description -n tcl-brlapi
This package provides the Tcl binding for BrlAPI.

%package -n python-brlapi
Version: %{api_version}
Group: Development/System
License: LGPLv2+
Requires: brlapi = %{api_version}-%{release}
BuildRequires: Pyrex
Summary: Python binding for BrlAPI
%description -n python-brlapi
This package provides the Python binding for BrlAPI.

%package -n brlapi-java
Version: %{api_version}
Group: Development/System
License: LGPLv2+
Requires: brlapi = %{api_version}-%{release}
## temporary work around, java-devel is not resolved consistently acrss archs
BuildRequires: java-devel
#BuildRequires: java-1.5.0-gcj-devel
Summary: Java binding for BrlAPI
%description -n brlapi-java
This package provides the Java binding for BrlAPI.

%define version %{pkg_version}

%prep
%setup -q
%patch4 -p1 -b .cppflags
%patch5 -p1 -b .parallel
%patch6 -p1 -b .quote

%build
# Patch6 changes aclocal.m4:
autoconf
for i in -I/usr/lib/jvm/java/include{,/linux}; do
      java_inc="$java_inc $i"
done
# there is no curses packages in BuildRequires, so the package builds
# without them in mock; let's express this decision explicitly
%configure CPPFLAGS="$java_inc" --without-curses \
%if %{with_speech_dispatcher}
  --with-speechd=%{_prefix} \
%endif
  --disable-stripping
make %{?_smp_mflags}

find . \( -path ./doc -o -path ./Documents \) -prune -o \
  \( -name 'README*' -o -name '*.txt' -o -name '*.html' -o \
     -name '*.sgml' -o -name '*.patch' -o \
     \( -path './Bootdisks/*' -type f -perm +ugo=x \) \) -print |
while read file; do
   mkdir -p doc/${file%/*} && cp -rp $file doc/$file || exit 1
done

%install
rm -rf $RPM_BUILD_ROOT
# does not seem to be parallel safe
make install INSTALL_ROOT="${RPM_BUILD_ROOT}"
mv "$RPM_BUILD_ROOT%{_libdir}/libbrlapi.a" "$RPM_BUILD_ROOT%{_prefix}/%{_lib}/"
rm "$RPM_BUILD_ROOT%{_libdir}/libbrlapi.so"
ln -s ../../%{_lib}/libbrlapi.so "$RPM_BUILD_ROOT%{_prefix}/%{_lib}/"
mv "$RPM_BUILD_ROOT%{_sysconfdir}/brltty/brltty-pm.conf" \
  doc/Drivers/Braille/Papenmeier/
install -d -m 755 "${RPM_BUILD_ROOT}%{_sysconfdir}" "$RPM_BUILD_ROOT%{_mandir}/man5"
install -m 644 Documents/brltty.conf "${RPM_BUILD_ROOT}%{_sysconfdir}"
echo ".so man1/brltty.1" > $RPM_BUILD_ROOT%{_mandir}/man5/brltty.conf.5

# clean up the manuals:
rm Documents/Manual-*/*/{*.mk,*.made,Makefile*}
mv Documents/BrlAPIref/{html,BrlAPIref}

%clean
rm -rf $RPM_BUILD_ROOT

%post
devices="/dev/vcsa /dev/vcsa0 /dev/vcc/a"
install=true
for device in ${devices}
do
   if [ -c "${device}" ]
   then
      install=false
      break
   fi
done
if $install
then
   device="$(set -- ${devices} && echo "${1}")"
   mkdir -p "${device%/*}"
   mknod -m o= "${device}" c 7 128
   chmod 660 "${device}"
   chown root.tty "${device}"
fi
exit 0

%post   -n brlapi -p /sbin/ldconfig
%postun -n brlapi -p /sbin/ldconfig

%files
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/brltty.conf
%{_sysconfdir}/brltty/
%{_bindir}/brltty
%{_bindir}/brltty-*
%{_libdir}/brltty/
%exclude %{_libdir}/brltty/libbrlttybba.so
%exclude %{_libdir}/brltty/libbrlttybxw.so
%if %{with_speech_dispatcher}
%exclude %{_libdir}/brltty/libbrlttyssd.so
%endif
%exclude %{_libdir}/brltty/libbrlttyxas.so
%doc LICENSE-GPL LICENSE-LGPL
%doc Documents/ChangeLog Documents/TODO
%doc Documents/Manual-BRLTTY/
%doc doc/*
%doc %{_mandir}/man[15]/brltty.*

%if %{with_speech_dispatcher}
%files speech-dispatcher
%defattr(-,root,root,-)
%doc Drivers/Speech/SpeechDispatcher/README
%{_libdir}/brltty/libbrlttyssd.so
%endif

%files xw
%defattr(-,root,root,-)
%doc Drivers/Braille/XWindow/README
%{_libdir}/brltty/libbrlttybxw.so

%files at-spi
%defattr(-,root,root,-)
%{_libdir}/brltty/libbrlttyxas.so

%files -n brlapi
%defattr(-,root,root)
%{_bindir}/vstp
%{_bindir}/xbrlapi
%{_libdir}/brltty/libbrlttybba.so
%{_libdir}/libbrlapi.so.*
%doc Drivers/Braille/XWindow/README
%doc Documents/Manual-BrlAPI/
%doc %{_mandir}/man1/xbrlapi.*
%doc %{_mandir}/man1/vstp.*

%files -n brlapi-devel
%defattr(-,root,root)
%{_prefix}/%{_lib}/libbrlapi.a
%{_prefix}/%{_lib}/libbrlapi.so
%{_includedir}/brltty
%{_includedir}/brlapi*.h
%doc %{_mandir}/man3/brlapi_*.3*
%doc Documents/BrlAPIref/BrlAPIref/

%files -n tcl-brlapi
%defattr(-,root,root)
%{tcl_sitearch}/brlapi-%{api_version}

%files -n python-brlapi
%defattr(-,root,root)
%{python_sitearch}/brlapi.so
%{python_sitearch}/Brlapi-%{api_version}-py%{pyver}.egg-info

%files -n brlapi-java
%defattr(-,root,root)
%{_jnidir}/libbrlapi_java.so
%{_javadir}/brlapi.jar


%changelog
* Thu Feb 18 2010 Jaroslav Škarvada <jskarvad@redhat.com> - 4.1-6
- fix rpmlint errors and warnings

* Wed Jan 20 2010 Stepan Kasal <skasal@redhat.com> - 4.1-5
- requires(post): coreutils to work around an installator bug
- Resolves: #540437

* Wed Jan 13 2010 Stepan Kasal <skasal@redhat.com> - 4.1-4
- limit building against speech-dispatcher to Fedora
- Resolves: rhbz#553795

* Sun Nov  1 2009 Stepan Kasal <skasal@redhat.com> - 4.1-3
- build the TTY driver (it was disabled since it first appered in 3.7.2-1)
- build with speech-dispatcher, packed into a separate sub-package

* Fri Oct 30 2009 Stepan Kasal <skasal@redhat.com> - 4.1-2
- move data-directory back to default: /etc/brltty
- move brltty to /bin and /lib, so that it can be used to repair the system
  without /usr mounted (#276181)
- move vstp and libbrlttybba.so to brlapi
- brltty no longer requires brlapi
- brlapi now requires brltty from the same build

* Wed Oct 28 2009 Stepan Kasal <skasal@redhat.com> - 4.1-1
- new upstream version
- use --disable-stripping instead of make variable override
- install the default brltty-pm.conf to docdir only (#526168)
- remove the duplicate copies of rhmkboot and rhmkroot from docdir
- patch configure so that the dirs in summary are not garbled:
  brltty-autoconf-quote.patch
- move data-directory to ${datadir}/brltty

* Tue Oct 20 2009 Stepan Kasal <skasal@redhat.com> - 4.0-2
- escape rpm macros in the rpm change log
- add requires to bind subpackages from one build together

* Wed Oct  7 2009 Stepan Kasal <skasal@redhat.com> - 4.0-1
- new upstream version
- drop upstreamed patches; ./autogen not needed anymore
- pack the xbrlapi server; move its man page to brlapi package
- add man-page for brltty.conf (#526168)

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.10-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue May 12 2009 Stepan Kasal <skasal@redhat.com> - 3.10-5
- rebuild after java-1.5.0-gcj rebuild

* Thu Apr 30 2009 Stepan Kasal <skasal@redhat.com> - 3.10-4
- own the tcl subdirectory (#474032)
- set CPPFLAGS to java include dirs, so that the java bindings build with
  any java implementation (#498964)
- add --without-curses; there is no curses package BuildRequired anyway

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.10-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 3.10-2
- Rebuild for Python 2.6

* Sat Sep 13 2008 Stepan Kasal <skasal@redhat.com> - 3.10-1
- new upstream release
- drop brltty-3.9-java-svn.patch, brltty-3.9-tcl85path.patch,
  and brltty-3.9-pyxfix.patch, they are upstream
- fix BuildRoot
- fix many sub-packages' Requires on brlapi

* Wed Sep 10 2008 Stepan Kasal <skasal@redhat.com> - 3.9-3
- add brltty-3.9-autoconf.patch to fix to build with Autoconf 2.62
- add brltty-3.9-parallel.patch to fix race condition with parallel make
- add brltty-3.9-pyxfix.patch to fix build with current pyrex
- Summary lines shall not end with a dot

* Thu Feb 28 2008 Tomas Janousek <tjanouse@redhat.com> - 3.9-2.2
- glibc build fixes
- applied java reorganisations from svn

* Wed Feb 20 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 3.9-2.1
- Autorebuild for GCC 4.3

* Wed Jan 09 2008 Tomas Janousek <tjanouse@redhat.com> - 3.9-1.1
- specfile update to comply with tcl packaging guidelines

* Mon Jan 07 2008 Tomas Janousek <tjanouse@redhat.com> - 3.9-1
- update to latest upstream (3.9)

* Tue Sep 18 2007 Tomas Janousek <tjanouse@redhat.com> - 3.8-2.svn3231
- update to r3231 from svn
- added java binding subpackage

* Wed Aug 29 2007 Tomas Janousek <tjanouse@redhat.com> - 3.8-2.svn3231
- update to r3231 from svn

* Tue Aug 21 2007 Tomas Janousek <tjanouse@redhat.com> - 3.8-1
- update to latest upstream
- added the at-spi driver, tcl and python bindings
- fixed the license tags

* Mon Mar 05 2007 Tomas Janousek <tjanouse@redhat.com> - 3.7.2-3
- added the XWindow driver
- build fix for newer byacc

* Tue Jan 30 2007 Tomas Janousek <tjanouse@redhat.com> - 3.7.2-2.1
- quiet postinstall scriptlet, really fixes #224570

* Tue Jan 30 2007 Tomas Janousek <tjanouse@redhat.com> - 3.7.2-2
- failsafe postinstall script, fixes #224570
- makefile fix - debuginfo extraction now works

* Thu Jan 25 2007 Tomas Janousek <tjanouse@redhat.com> - 3.7.2-1.1
- fix building with newer kernel-headers (#224149)

* Wed Jul 12 2006 Petr Rockai <prockai@redhat.com> - 3.7.2-1
- upgrade to latest upstream version
- split off brlapi and brlapi-devel packages

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 3.2-12.1
- rebuild

* Sun Jul 02 2006 Florian La Roche <laroche@redhat.com>
- for the post script require coreutils

* Mon Jun 05 2006 Jesse Keating <jkeating@redhat.com> - 3.2-11
- Added byacc BuildRequires, removed prereq, coreutils is always there

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 3.2-10.2.1
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 3.2-10.2
- rebuilt for new gcc4.1 snapshot and glibc changes

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Wed Mar 16 2005 Bill Nottingham <notting@redhat.com> 3.2-10
- rebuild

* Fri Nov 26 2004 Florian La Roche <laroche@redhat.com>
- add a %%clean into .spec

* Thu Oct 14 2004 Adrian Havill <havill@redhat.com> 3.2-5
- chmod a-x for conf file (#116244)

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Sep 30 2003 Florian La Roche <Florian.LaRoche@redhat.de>
- prereq coreutils for mknod/chown/chmod

* Mon Jul 07 2003 Adrian Havill <havill@redhat.com> 3.2-2
- changed spec "Copyright" to "License"
- use %%configure macro, %%{_libdir} for non-ia32 archs
- removed unnecessary set and unset, assumed/default spec headers
- fixed unpackaged man page, duplicate /bin and /lib entries
- use plain install vs scripts for non-i386 buildsys
