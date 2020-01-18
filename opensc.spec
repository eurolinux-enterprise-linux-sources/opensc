Name:           opensc
Version:        0.19.0
Release:        3%{?dist}
Summary:        Smart card library and applications

Group:          System Environment/Libraries
License:        LGPLv2+
URL:            https://github.com/OpenSC/OpenSC/wiki
Source0:        https://github.com/OpenSC/OpenSC/releases/download/%{version}/%{name}-%{version}.tar.gz
Source1:        opensc.module
Source2:        pkcs11-switch.sh
# Disable pinpad by default and use backward compatible configuration (#1547117, #1547744)
Patch1:         opensc-0.19.0-config.patch
# https://github.com/OpenSC/OpenSC/pull/1489
Patch2:         opensc-0.19.0-coverity.patch
# https://github.com/OpenSC/OpenSC/pull/1500
Patch3:         opensc-0.19.0-coolkey-matching.patch
# https://github.com/OpenSC/OpenSC/pull/1502
Patch4:         opensc-0.19.0-cac1.patch
# https://github.com/OpenSC/OpenSC/pull/1549
Patch5:         opensc-0.19.0-dual.patch

BuildRequires:  pcsc-lite-devel
BuildRequires:  readline-devel
BuildRequires:  openssl-devel
BuildRequires:  /usr/bin/xsltproc
BuildRequires:  docbook-style-xsl
BuildRequires:  autoconf automake libtool
Requires:       pcsc-lite-libs%{?_isa}
Requires:	pcsc-lite
Obsoletes:      mozilla-opensc-signer < 0.12.0
Obsoletes:      opensc-devel < 0.12.0

%description
OpenSC provides a set of libraries and utilities to work with smart cards. Its
main focus is on cards that support cryptographic operations, and facilitate
their use in security applications such as authentication, mail encryption and
digital signatures. OpenSC implements the PKCS#11 API so applications
supporting this API (such as Mozilla Firefox and Thunderbird) can use it. On
the card OpenSC implements the PKCS#15 standard and aims to be compatible with
every software/card that does so, too.


%prep
%setup -q
%patch1 -p1 -b .config
%patch2 -p1 -b .coverity
%patch3 -p1 -b .coolkey-match
%patch4 -p1 -b .cac1
%patch5 -p1 -b .dual

cp -p src/pkcs15init/README ./README.pkcs15init
cp -p src/scconf/README.scconf .
# No {_libdir} here to avoid multilib conflicts; it's just an example
sed -i -e 's|/usr/local/towitoko/lib/|/usr/lib/ctapi/|' etc/opensc.conf.example.in


%build
autoreconf -fvi
%ifarch %{ix86} ppc s390
sed -i -e 's/opensc.conf/opensc-%{_arch}.conf/g' src/libopensc/Makefile.in
%endif
sed -i -e 's|"/lib /usr/lib\b|"/%{_lib} %{_libdir}|' configure # lib64 rpaths
%configure  --disable-static \
  --disable-assert \
  --enable-pcsc \
  --disable-tests `# Broken release tarball fails to build them` \
  --disable-notify `# This was not present in previous release` \
  --with-completiondir=no `#Bash completion is disabled` \
  --enable-sm \
  --with-pcsc-provider=libpcsclite.so.1
make %{?_smp_mflags} V=1


%install
make install DESTDIR=$RPM_BUILD_ROOT
rm -f $RPM_BUILD_ROOT%{_bindir}/opensc-notify
install -Dpm 644 %{SOURCE1} $RPM_BUILD_ROOT%{_datadir}/p11-kit/modules/opensc.module
install -Dpm 755 %{SOURCE2} $RPM_BUILD_ROOT%{_bindir}/pkcs11-switch

%ifarch %{ix86} ppc s390
# To avoid multilib issues, move these files on 32b intel architectures
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/opensc.conf
install -Dpm 644 etc/opensc.conf $RPM_BUILD_ROOT%{_sysconfdir}/opensc-%{_arch}.conf
rm -f $RPM_BUILD_ROOT%{_mandir}/man5/opensc.conf.5
install -Dpm 644 doc/files/opensc.conf.5 $RPM_BUILD_ROOT%{_mandir}/man5/opensc-%{_arch}.conf.5
# use NEWS file timestamp as reference for configuration file
touch -r NEWS $RPM_BUILD_ROOT%{_sysconfdir}/opensc-%{_arch}.conf
touch -r NEWS $RPM_BUILD_ROOT%{_mandir}/man5/opensc-%{_arch}.conf.5
%else
# For backward compatibility, symlink the old location to the new files
ln -s %{_sysconfdir}/opensc.conf $RPM_BUILD_ROOT%{_sysconfdir}/opensc-%{_arch}.conf
%endif

find $RPM_BUILD_ROOT%{_libdir} -type f -name "*.la" | xargs rm

rm -rf $RPM_BUILD_ROOT%{_datadir}/doc/opensc

# Upstream considers libopensc API internal and no longer ships
# public headers and pkgconfig files.
# Remove the symlink as nothing is supposed to link against libopensc.
rm -f $RPM_BUILD_ROOT%{_libdir}/libopensc.so
rm -f $RPM_BUILD_ROOT%{_libdir}/libsmm-local.so
rm -f $RPM_BUILD_ROOT%{_mandir}/man1/opensc-notify.1*
rm -f $RPM_BUILD_ROOT%{_datadir}/applications/org.opensc.notify.desktop
%if 0%{?rhel}
rm -rf %{buildroot}%{_sysconfdir}/bash_completion.d/
%endif

# the npa-tool builds to nothing since we do not have OpenPACE library
rm -rf %{buildroot}%{_bindir}/npa-tool
rm -rf %{buildroot}%{_mandir}/man1/npa-tool.1*

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files
%defattr(-,root,root,-)
%doc COPYING NEWS README*

%if ! 0%{?rhel}
%{_sysconfdir}/bash_completion.d/*
%endif

%ifarch %{ix86} ppc s390
%{_mandir}/man5/opensc-%{_arch}.conf.5*
%else
%config(noreplace) %{_sysconfdir}/opensc.conf
%{_mandir}/man5/opensc.conf.5*
%endif

%config(noreplace) %{_sysconfdir}/opensc-%{_arch}.conf
%{_datadir}/p11-kit/modules/opensc.module
%{_bindir}/cardos-tool
%{_bindir}/cryptoflex-tool
%{_bindir}/eidenv
%{_bindir}/iasecc-tool
%{_bindir}/gids-tool
%{_bindir}/netkey-tool
%{_bindir}/openpgp-tool
%{_bindir}/opensc-explorer
%{_bindir}/opensc-tool
%{_bindir}/opensc-asn1
%{_bindir}/piv-tool
%{_bindir}/pkcs11-tool
%{_bindir}/pkcs11-switch
%{_bindir}/pkcs15-crypt
%{_bindir}/pkcs15-init
%{_bindir}/pkcs15-tool
%{_bindir}/sc-hsm-tool
%{_bindir}/dnie-tool
%{_bindir}/westcos-tool
%{_bindir}/egk-tool
%{_libdir}/lib*.so.*
%{_libdir}/opensc-pkcs11.so
%{_libdir}/pkcs11-spy.so
%{_libdir}/onepin-opensc-pkcs11.so
%{_libdir}/pkgconfig/*.pc
%%dir %{_libdir}/pkcs11
%{_libdir}/pkcs11/opensc-pkcs11.so
%{_libdir}/pkcs11/onepin-opensc-pkcs11.so
%{_libdir}/pkcs11/pkcs11-spy.so
%{_datadir}/opensc/
%{_mandir}/man1/cardos-tool.1*
%{_mandir}/man1/cryptoflex-tool.1*
%{_mandir}/man1/eidenv.1*
%{_mandir}/man1/gids-tool.1*
%{_mandir}/man1/iasecc-tool.1*
%{_mandir}/man1/netkey-tool.1*
%{_mandir}/man1/openpgp-tool.1*
%{_mandir}/man1/opensc-explorer.*
%{_mandir}/man1/opensc-tool.1*
%{_mandir}/man1/opensc-asn1.1*
%{_mandir}/man1/piv-tool.1*
%{_mandir}/man1/pkcs11-tool.1*
%{_mandir}/man1/pkcs15-crypt.1*
%{_mandir}/man1/pkcs15-init.1*
%{_mandir}/man1/pkcs15-tool.1*
%{_mandir}/man1/sc-hsm-tool.1*
%{_mandir}/man1/westcos-tool.1*
%{_mandir}/man1/dnie-tool.1*
%{_mandir}/man1/egk-tool.1*
%{_mandir}/man5/pkcs15-profile.5*


%changelog
* Wed Mar 27 2019 Jakub Jelen <jjelen@redhat.com> - 0.19.0-3
- Make OpenSC multilib also on s390 and ppc arches

* Wed Mar 27 2019 Jakub Jelen <jjelen@redhat.com> - 0.19.0-2
- Make OpenSC multilib again by moving the conflicting files on ix86 arch

* Thu Feb 07 2019 Jakub Jelen <jjelen@redhat.com> - 0.19.0-1
- Rebase to new upstream release (#1656791)
  - Add Support for HID Crescendo 144K (#1612372)
  - Add Support for CAC Alt tokens (#1645581)
  - Fix usage detection from certificates (#1672898)
  - Fix security issues:
    - CVE-2018-16391
    - CVE-2018-16392
    - CVE-2018-16393
    - CVE-2018-16418
    - CVE-2018-16419
    - CVE-2018-16420
    - CVE-2018-16421
    - CVE-2018-16422
    - CVE-2018-16423
    - CVE-2018-16426
    - CVE-2018-16427

* Tue Jul 03 2018 Jakub Jelen <jjelen@redhat.com> - 0.16.0-10.20170227git
- Improve support for ECC-enabled CardOS 5.3 card (#1562277)

* Tue Jun 19 2018 Jakub Jelen <jjelen@redhat.com> - 0.16.0-9.20170227git
- make ECPoint behavior standards compliant by default (#1562572)
- allow mechanism to be specified in hexadecimal (#1562572)
- Disable pinpad by default (#1547117, #1547744)

* Wed Jan 03 2018 Jakub Jelen <jjelen@redhat.com> - 0.16.0-8.20170227git
- Copy labels from certificate (#1448555)
- Avoid infinite loop in CAC driver when reading non-CAC cards (#1473335)
- Properly parse Simple TLV structures in CAC driver (#1473418)

* Tue Nov 07 2017 Jakub Jelen <jjelen@redhat.com> - 0.16.0-7.20170227git
- Fix issues reported by Coverity
- Use upstream accepted fix for CAC Alt tokens (#1473418)

* Fri Nov 03 2017 Jakub Jelen <jjelen@redhat.com> - 0.16.0-6.20170227git
- Use label from certificate DN if there is none (#1448555)
- Use Cardholder name in the token label (#1449740)
- Avoid infinite loop when reading CAC cards (#1473335)
- Workaround for CAC Alt tokens (#1473418)

* Thu May 18 2017 Jakub Jelen <jjelen@redhat.com> - 0.16.0-5.20170227git
- Add missing pkcs11-switch script

* Thu Apr 13 2017 Jakub Jelen <jjelen@redhat.com> - 0.16.0-4.20170227git
- Release aquired lock for uninitialized ASEPCOS cards (#1376090)

* Thu Mar 23 2017 Jakub Jelen <jjelen@redhat.com> - 0.16.0-3.20170227git
- Fix more issues identified by Coverity scan

* Thu Mar 23 2017 Jakub Jelen <jjelen@redhat.com> - 0.16.0-2.20170227git
- Add support for CardOS 5.3
- Fix coverity issues
- Provide simple tool to swith PKCS#11 library in NSS DB

* Tue Jan 10 2017 Jakub Jelen <jjelen@redhat.com> - 0.16.0-1.20170110git
- Rebase to OpenSC master with support for CAC cards (#1373164)

* Thu Feb 25 2016 Nikos Mavrogiannopoulos <nmav@redhat.com> 0.14.0-2
- Export PKCS#11 symbols from spy library (#1283305)

* Thu Apr 23 2015 Nikos Mavrogiannopoulos <nmav@redhat.com> 0.14.0-1
- Updated to opensc 0.14.0

* Fri Mar 14 2014 Nikos Mavrogiannopoulos <nmav@redhat.com> 0.13.0-9
- Configuration file includes arch to allow it operate under multilib

* Mon Mar 10 2014 Nikos Mavrogiannopoulos <nmav@redhat.com> 0.13.0-8
- Ensure that variables are in scope when used (#1062307)

* Tue Feb 25 2014 Nikos Mavrogiannopoulos <nmav@redhat.com> 0.13.0-7
- Corrected path of opensc.module (#1060034)

* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 0.13.0-6
- Mass rebuild 2014-01-24

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 0.13.0-5
- Mass rebuild 2013-12-27

* Fri Mar 08 2013 Stef Walter <stefw@redhat.com> - 0.13.0-4
- Use the standard name format for p11-kit module configs
- Put the p11-kit module config is the system location

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.13.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sun Jan 13 2013 Kalev Lember <kalevlember@gmail.com> - 0.13.0-2
- Backport an upstream patch for fixing pkcs15 cert length calculation

* Thu Jan 03 2013 Milan Broz <mbroz@redhat.com> - 0.13.0-1
- Update to 0.13.0 (#890770)
- Remove no longer provided onepin-opensc-pkcs11.so.
- Add iasecc-tool, openpgp-tool and sc-hsm-tool.

* Fri Jul 27 2012 Tomas Mraz <tmraz@redhat.com> - 0.12.2-6
- Add a configuration file for p11-kit (#840504)

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.12.2-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sun Mar  4 2012 Peter Robinson <pbrobinson@fedoraproject.org> - 0.12.2-4
- Add patch for dso

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.12.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Aug 17 2011 Tomas Mraz <tmraz@redhat.com> - 0.12.2-2
- Rebuilt to fix trailing slashes in filelist from rpmbuild bug

* Tue Jul 19 2011 Kalev Lember <kalevlember@gmail.com> - 0.12.2-1
- Update to 0.12.2 (#722659)

* Wed May 18 2011 Kalev Lember <kalev@smartlink.ee> - 0.12.1-1
- Update to 0.12.1 (#705743)
- Removed BR libtool-ltdl-devel to build with glibc's libdl instead

* Tue Apr 12 2011 Tomas Mraz <tmraz@redhat.com> - 0.12.0-4
- drop multilib conflicting and duplicated doc file (#695368)

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.12.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Jan 03 2011 Kalev Lember <kalev@smartlink.ee> - 0.12.0-2
- Disabled asserts

* Mon Jan 03 2011 Kalev Lember <kalev@smartlink.ee> - 0.12.0-1
- Update to 0.12.0
- Removed and obsoleted mozilla-opensc-signer and opensc-devel subpackages
- Dropped patches which are now upstreamed
- It is no longer possible to build in both pcsc-lite and openct support,
  so opensc now gets built exclusively with pcsc-lite.

* Tue Dec 21 2010 Tomas Mraz <tmraz@redhat.com> - 0.11.13-6
- fix buffer overflow on rogue card serial numbers

* Tue Oct 19 2010 Tomas Mraz <tmraz@redhat.com> - 0.11.13-5
- own the _libdir/pkcs11 subdirectory (#644527)

* Tue Sep  7 2010 Tomas Mraz <tmraz@redhat.com> - 0.11.13-4
- fix build with new pcsc-lite

* Wed Aug 11 2010 Rex Dieter <rdieter@fedoraproject.org> - 0.11.13-3
- build against libassuan1 (f14+)

* Wed Jun  9 2010 Tomas Mraz <tmraz@redhat.com> - 0.11.13-2
- replace file dependency (#601943)

* Tue Feb 16 2010 Kalev Lember <kalev@smartlink.ee> - 0.11.13-1
- new upstream version

* Sun Feb 14 2010 Kalev Lember <kalev@smartlink.ee> - 0.11.12-2
- Added patch to fix linking with the new --no-add-needed default (#564758)

* Mon Dec 21 2009 Kalev Lember <kalev@smartlink.ee> - 0.11.12-1
- new upstream version
- replaced %%define with %%global
- BR clean up from items not applicable to current Fedora releases

* Tue Dec  8 2009 Michael Schwendt <mschwendt@fedoraproject.org> - 0.11.11-2
- Explicitly BR libassuan-static in accordance with the Packaging
  Guidelines (libassuan-devel is still static-only).

* Thu Nov 19 2009 Tomas Mraz <tmraz@redhat.com> - 0.11.11-1
- new upstream version

* Tue Sep 29 2009 Tomas Mraz <tmraz@redhat.com> - 0.11.9-2
- fix multilib conflict in the configuration file (#526269)

* Wed Sep 09 2009 Tomas Mraz <tmraz@redhat.com> - 0.11.9-1
- new upstream version

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 0.11.8-5
- rebuilt with new openssl

* Mon Jul 27 2009 Tomas Mraz <tmraz@redhat.com> - 0.11.8-4
- Depend on specific arch of pcsc-lite-libs (reported by Kalev Lember)

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.11.8-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Jun 15 2009 Tomas Mraz <tmraz@redhat.com> - 0.11.8-2
- Rebuilt with new openct

* Mon May 11 2009 Tomas Mraz <tmraz@redhat.com> - 0.11.8-1
- new upstream version - fixes security issue

* Fri Feb 27 2009 Tomas Mraz <tmraz@redhat.com> - 0.11.7-1
- new upstream version - fixes CVE-2009-0368

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.11.6-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Jan 15 2009 Tomas Mraz <tmraz@redhat.com> - 0.11.6-2
- Add explicit requires for pcsc-lite-libs. Dlopen libpcsclite with the full
  soname.

* Tue Sep  2 2008 Tomas Mraz <tmraz@redhat.com> - 0.11.6-1
- Update to latest upstream, fixes CVE-2008-2235

* Thu Apr 10 2008 Hans de Goede <j.w.r.degoede@hhs.nl> - 0.11.4-5
- BuildRequire libassuan-devel instead of libassuan-static (bz 441812)

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0.11.4-4
- Autorebuild for GCC 4.3

* Wed Dec 05 2007 Release Engineering <rel-eng at fedoraproject dot org> - 0.11.4-3
 - Rebuild for deps

* Wed Dec  5 2007 Ville Skyttä <ville.skytta at iki.fi> - 0.11.4-2
- Rebuild.

* Mon Sep 10 2007 Ville Skyttä <ville.skytta at iki.fi> - 0.11.4-1
- 0.11.4.

* Mon Aug 20 2007 Ville Skyttä <ville.skytta at iki.fi> - 0.11.4-0.1.rc1
- 0.11.4-rc1, pkcs11-tool usage message fix applied upstream.
- License: LGPLv2+

* Thu Jul 26 2007 Ville Skyttä <ville.skytta at iki.fi> - 0.11.3-2
- Fix pkcs11-tool usage message crash (#249702).

* Tue Jul 17 2007 Ville Skyttä <ville.skytta at iki.fi> - 0.11.3-1
- 0.11.3.

* Sat Jun 30 2007 Ville Skyttä <ville.skytta at iki.fi> - 0.11.3-0.1.pre2
- 0.11.3-pre2.

* Thu Jun 21 2007 Ville Skyttä <ville.skytta at iki.fi> - 0.11.3-0.1.pre1
- 0.11.3-pre1.

* Sun May  6 2007 Ville Skyttä <ville.skytta at iki.fi> - 0.11.2-2
- Add explicit build dependency on ncurses-devel.

* Sat May  5 2007 Ville Skyttä <ville.skytta at iki.fi> - 0.11.2-1
- 0.11.2.

* Tue Apr 24 2007 Ville Skyttä <ville.skytta at iki.fi> - 0.11.2-0.3.rc2
- 0.11.2-rc2.

* Fri Mar 23 2007 Ville Skyttä <ville.skytta at iki.fi> - 0.11.2-0.3.rc1
- 0.11.2-rc1.

* Thu Mar 15 2007 Ville Skyttä <ville.skytta at iki.fi> - 0.11.2-0.2.pre6
- 0.11.2-pre6.

* Tue Mar  6 2007 Ville Skyttä <ville.skytta at iki.fi> - 0.11.2-0.2.pre4
- 0.11.2-pre4.
- Require pinentry-gui instead of the pinentry executable in signer.

* Sun Dec  3 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.11.2-0.1.pre3
- 0.11.2-pre3.
- Build with new libassuan.
- Don't run autotools during build.
- Adjust to readline/termcap/ncurses changes.

* Sat Oct 14 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.11.1-6
- Rebuild with new libassuan.

* Sun Oct  8 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.11.1-5
- Rebuild with new libassuan.

* Mon Oct  2 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.11.1-4
- Rebuild.

* Tue Sep 26 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.11.1-3
- Rebuild with new libassuan.

* Sat Sep  2 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.11.1-2
- Rebuild.

* Wed May 31 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.11.1-1
- 0.11.1.
- Avoid some multilib conflicts.

* Sun May  7 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.11.0-2
- Sync example paths in openct.conf with ctapi-common.
- Update URL.

* Thu May  4 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.11.0-1
- 0.11.0.

* Thu Apr 27 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.11.0-0.1.rc2
- 0.11.0-rc2.

* Sat Apr 22 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.11.0-0.1.rc1
- 0.11.0-rc1.

* Mon Mar  6 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.10.1-3
- Rebuild.

* Wed Feb 15 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.10.1-2
- Avoid standard rpaths on lib64 archs.

* Sun Jan  8 2006 Ville Skyttä <ville.skytta at iki.fi> - 0.10.1-1
- 0.10.1.

* Wed Nov  9 2005 Ville Skyttä <ville.skytta at iki.fi> - 0.10.0-1
- 0.10.0.
- Adapt to modularized X.Org.

* Wed Oct 26 2005 Ville Skyttä <ville.skytta at iki.fi> - 0.10.0-0.1.rc2
- 0.10.0-rc2.
- Install signer plugin only to plugin dir.

* Sat Oct 22 2005 Ville Skyttä <ville.skytta at iki.fi> - 0.10.0-0.1.rc1
- 0.10.0-rc1.

* Wed Oct 19 2005 Ville Skyttä <ville.skytta at iki.fi> - 0.10.0-0.1.beta2.rc1
- 0.10.0-beta2-rc1.
- Specfile cleanups.

* Tue Apr 26 2005 Ville Skyttä <ville.skytta at iki.fi> - 0.9.6-2
- 0.9.6, build patch applied upstream.
- Package summary and description improvements.
- Drop explicit openct dependency.

* Fri Mar 18 2005 Ville Skyttä <ville.skytta at iki.fi> - 0.9.4-3
- Fix FC4 build.
- Rename opensc-pam to pam_opensc per package naming guidelines.

* Wed Feb  9 2005 Michael Schwendt <mschwendt[AT]users.sf.net> - 0.9.4-2
- Substitute hardcoded 'lib' in OpenSSL checks for multi-lib platforms.
- Use --with-plugin-dir instead of --with-plugin-path (fixes x86_64).

* Thu Feb  3 2005 Ville Skyttä <ville.skytta at iki.fi> - 0.9.4-1
- Drop unnecessary Epochs, pre-FC1 compat cruft, and no longer relevant
  --with(out) rpmbuild options.
- Exclude *.la.

* Wed Nov  3 2004 Ville Skyttä <ville.skytta at iki.fi> - 0:0.9.4-0.fdr.1
- Update to 0.9.4, parallel build patch applied upstream.
- Patch to fix library paths and LDFLAGS.
- Don't require mozilla, but the plugin dir in signer.
- Build with dependency tracking disabled.

* Tue Jul 27 2004 Ville Skyttä <ville.skytta at iki.fi> - 0:0.9.2-0.fdr.2
- Building the signer plugin can be disabled with "--without signer".
  Thanks to Fritz Elfert for the idea.
- Update description.

* Sun Jul 25 2004 Ville Skyttä <ville.skytta at iki.fi> - 0:0.9.2-0.fdr.1
- Update to 0.9.2, old patches applied upstream.
- Add patch to fix parallel builds.
- Convert man pages to UTF-8.

* Thu Jul 22 2004 Ville Skyttä <ville.skytta at iki.fi> - 0:0.9.1-0.fdr.1
- Update to 0.9.1 (preview).

* Thu Jul  1 2004 Ville Skyttä <ville.skytta at iki.fi> - 0:0.9.0-0.fdr.0.1.alpha
- Update to 0.9.0-alpha.

* Sat May  1 2004 Ville Skyttä <ville.skytta at iki.fi> - 0:0.8.1-0.fdr.8
- Rebuild with libassuan 0.6.5.

* Sat Jan 31 2004 Ville Skyttä <ville.skytta at iki.fi> - 0:0.8.1-0.fdr.7
- Rebuild with libassuan 0.6.3.
- Add gdm example to PAM quickstart.

* Mon Jan 19 2004 Ville Skyttä <ville.skytta at iki.fi> - 0:0.8.1-0.fdr.6
- Use /%%{_lib} instead of hardcoding /lib.

* Sat Dec 20 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:0.8.1-0.fdr.5
- Split PAM support into a subpackage.
- Rebuild with libassuan 0.6.2.

* Sun Nov 23 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:0.8.1-0.fdr.4
- Rebuild with libassuan 0.6.1.
- Include PAM quickstart doc snippet.

* Fri Nov 14 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:0.8.1-0.fdr.3
- Require OpenCT.

* Fri Oct 17 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:0.8.1-0.fdr.2
- Install example config files as documentation.

* Tue Oct 14 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:0.8.1-0.fdr.1
- Update to 0.8.1.

* Wed Aug 27 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:0.8.0-0.fdr.2
- Signer can be built with oldssl too.

* Wed Aug 27 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:0.8.0-0.fdr.1
- Update to 0.8.0.

* Wed Jul 30 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:0.8.0-0.fdr.0.2.cvs20030730
- Update to 20030730.
- Clean up %%docs.
- Include *.la (uses ltdl).
- Own the %%{_libdir}/pkcs11 directory.
- Disable signer; assuan has disappeared from the tarball :(

* Fri May 23 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:0.8.0-0.fdr.0.1.rc1
- First build.
