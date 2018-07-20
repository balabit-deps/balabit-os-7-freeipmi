#
# Copyright (c) 2003-2010 FreeIPMI Core Team
#

%define name freeipmi
%define version 1.4.11
%if %{?_with_debug:1}%{!?_with_debug:0}
%define release 1.debug%{?dist}
%else
%define release 1%{?dist}
%endif

Name: %{name}
Version: %{version}
Release: %{release}
License: GPLv2+
Group: Applications/System
URL: http://www.gnu.org/software/freeipmi/
Source: ftp://ftp.gnu.org/gnu/freeipmi/%{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: libgcrypt-devel texinfo
Requires(post): info
Requires(preun): info
Obsoletes: freeipmi-ipmimonitoring
# Necessary as only those archs implement iopl and friends (#368541)
ExclusiveArch: %{ix86} x86_64 ia64 alpha
Summary: FreeIPMI
%description
The FreeIPMI project provides "Remote-Console" (out-of-band) and
"System Management Software" (in-band) based on Intelligent
Platform Management Interface specification.

%package devel
Summary: Development package for FreeIPMI
Group: Development/System
Requires: freeipmi = %{version}-%{release}
%description devel
Development package for FreeIPMI.  This package includes the FreeIPMI
header files and static libraries.

%package bmc-watchdog
Summary: FreeIPMI BMC watchdog
Group: Applications/System
Requires: freeipmi = %{version}-%{release}
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig
%description bmc-watchdog
Provides a watchdog daemon for OS monitoring and recovery.

%package ipmidetectd
Summary: IPMI node detection monitoring daemon
Group: Applications/System
Requires: freeipmi = %{version}-%{release}
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig
%description ipmidetectd
IPMI node detection daemon.  Regularly IPMI-pings remote nodes to
provide data for a number of IPMI detection tools and features.

%package ipmiseld
Summary: IPMI SEL syslog logging daemon
Group: Applications/System
Requires: freeipmi = %{version}-%{release}
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig
%description ipmiseld
IPMI SEL syslog logging daemon.

%if %{?_with_debug:1}%{!?_with_debug:0}
  %define _enable_debug --enable-debug --enable-trace
%endif

%prep
%setup -q

%build
%configure --program-prefix=%{?_program_prefix:%{_program_prefix}} \
           %{?_enable_debug} --disable-static
CFLAGS="$RPM_OPT_FLAGS" make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT
DESTDIR="$RPM_BUILD_ROOT" make install
# fix coherance problems with associated script filenames
mkdir -p $RPM_BUILD_ROOT/%{_initrddir}/
# if check needed for SLES systems
if [[ "%{_sysconfdir}/init.d" != "%{_initrddir}" ]]
then
mv $RPM_BUILD_ROOT/%{_sysconfdir}/init.d/bmc-watchdog $RPM_BUILD_ROOT/%{_initrddir}/bmc-watchdog
mv $RPM_BUILD_ROOT/%{_sysconfdir}/init.d/ipmidetectd $RPM_BUILD_ROOT/%{_initrddir}/ipmidetectd
mv $RPM_BUILD_ROOT/%{_sysconfdir}/init.d/ipmiseld $RPM_BUILD_ROOT/%{_initrddir}/ipmiseld
fi
rm -f %{buildroot}%{_infodir}/dir
# kludge to get around rpmlint complaining about 0 length semephore file
echo freeipmi > %{buildroot}%{_localstatedir}/lib/freeipmi/ipckey
# Remove .la files
rm -rf $RPM_BUILD_ROOT/%{_libdir}/*.la

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ -x /sbin/install-info ]; then
   #/sbin/install-info %{_infodir}/freeipmi.info.gz %{_infodir}/dir
   /sbin/install-info %{_infodir}/freeipmi-faq.info.gz %{_infodir}/dir
fi
/sbin/ldconfig

%preun
if [ $1 = 0 ]; then
   if [ -x /sbin/install-info ]; then
      #/sbin/install-info --delete %{_infodir}/freeipmi.info.gz %{_infodir}/dir
      /sbin/install-info --delete %{_infodir}/freeipmi-faq.info.gz %{_infodir}/dir
   fi
fi

%postun -p /sbin/ldconfig

%post bmc-watchdog
if [ "$1" = 1 ]; then
   if [ -x %{_initrddir}/bmc-watchdog ]; then
      /sbin/chkconfig --add bmc-watchdog
      /sbin/chkconfig bmc-watchdog off
   fi
fi
if [ $1 -ge 1 ]; then
   if [ -x %{_initrddir}/bmc-watchdog ]; then
      if %{_initrddir}/bmc-watchdog status | grep -q running; then
         %{_initrddir}/bmc-watchdog restart
      else
         %{_initrddir}/bmc-watchdog condrestart
      fi
   fi
fi

%preun bmc-watchdog
#
# Stop bmc-watchdog if it is running 
#
if [ "$1" = 0 ]; then
    if [ -x %{_initrddir}/bmc-watchdog ]; then
       if %{_initrddir}/bmc-watchdog status | grep -q running; then
          %{_initrddir}/bmc-watchdog stop
       fi
       /sbin/chkconfig --del bmc-watchdog
    fi
fi

%post ipmidetectd
if [ "$1" = 1 ]; then
   if [ -x %{_initrddir}/ipmidetectd ]; then
      /sbin/chkconfig --add ipmidetectd
      /sbin/chkconfig ipmidetectd off
   fi
fi
if [ $1 -ge 1 ]; then
   if [ -x %{_initrddir}/ipmidetectd ]; then
      if %{_initrddir}/ipmidetectd status | grep -q running; then
         %{_initrddir}/ipmidetectd restart
      else
         %{_initrddir}/ipmidetectd condrestart
      fi
   fi
fi

%preun ipmidetectd
#
# Stop ipmidetectd if it is running 
#
if [ "$1" = 0 ]; then
    if [ -x %{_initrddir}/ipmidetectd ]; then
       if %{_initrddir}/ipmidetectd status | grep -q running; then
          %{_initrddir}/ipmidetectd stop
       fi
       /sbin/chkconfig --del ipmidetectd
    fi
fi

%post ipmiseld
if [ "$1" = 1 ]; then
   if [ -x %{_initrddir}/ipmiseld ]; then
      /sbin/chkconfig --add ipmiseld
      /sbin/chkconfig ipmiseld off
   fi
fi
if [ $1 -ge 1 ]; then
   if [ -x %{_initrddir}/ipmiseld ]; then
      if %{_initrddir}/ipmiseld status | grep -q running; then
         %{_initrddir}/ipmiseld restart
      else
         %{_initrddir}/ipmiseld condrestart
      fi
   fi
fi

%preun ipmiseld
#
# Stop ipmiseld if it is running 
#
if [ "$1" = 0 ]; then
    if [ -x %{_initrddir}/ipmiseld ]; then
       if %{_initrddir}/ipmiseld status | grep -q running; then
          %{_initrddir}/ipmiseld stop
       fi
       /sbin/chkconfig --del ipmiseld
    fi
fi

%files
%defattr(-,root,root)
%dir %{_sysconfdir}/freeipmi/
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/freeipmi/freeipmi.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/freeipmi/freeipmi_interpret_sel.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/freeipmi/freeipmi_interpret_sensor.conf
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/freeipmi/ipmidetect.conf
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/freeipmi/libipmiconsole.conf
%doc %{_infodir}/*
%dir %{_datadir}/doc/%{name}
%doc %{_datadir}/doc/%{name}/AUTHORS
%doc %{_datadir}/doc/%{name}/COPYING
%doc %{_datadir}/doc/%{name}/ChangeLog
%doc %{_datadir}/doc/%{name}/ChangeLog.0
%doc %{_datadir}/doc/%{name}/INSTALL
%doc %{_datadir}/doc/%{name}/NEWS
%doc %{_datadir}/doc/%{name}/README
%doc %{_datadir}/doc/%{name}/README.argp
%doc %{_datadir}/doc/%{name}/README.build
%doc %{_datadir}/doc/%{name}/README.openipmi
%doc %{_datadir}/doc/%{name}/TODO
%doc %{_datadir}/doc/%{name}/COPYING.ipmiping
%doc %{_datadir}/doc/%{name}/COPYING.ipmipower
%doc %{_datadir}/doc/%{name}/COPYING.ipmiconsole
%doc %{_datadir}/doc/%{name}/COPYING.ipmimonitoring
%doc %{_datadir}/doc/%{name}/COPYING.pstdout
%doc %{_datadir}/doc/%{name}/COPYING.ipmidetect
%doc %{_datadir}/doc/%{name}/COPYING.ipmi-fru
%doc %{_datadir}/doc/%{name}/COPYING.ipmi-dcmi
%doc %{_datadir}/doc/%{name}/COPYING.sunbmc
%doc %{_datadir}/doc/%{name}/COPYING.ZRESEARCH
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmiping
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmipower
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmiconsole
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmimonitoring
%doc %{_datadir}/doc/%{name}/DISCLAIMER.pstdout
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmidetect
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmi-fru
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmi-dcmi
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmiping.UC
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmipower.UC
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmiconsole.UC
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmimonitoring.UC
%doc %{_datadir}/doc/%{name}/DISCLAIMER.pstdout.UC
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmidetect.UC
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmi-fru.UC
%doc %{_datadir}/doc/%{name}/freeipmi-coding.txt
%doc %{_datadir}/doc/%{name}/freeipmi-design.txt
%doc %{_datadir}/doc/%{name}/freeipmi-hostrange.txt
%doc %{_datadir}/doc/%{name}/freeipmi-libraries.txt
%doc %{_datadir}/doc/%{name}/freeipmi-bugs-issues-and-workarounds.txt
%doc %{_datadir}/doc/%{name}/freeipmi-testing.txt
%doc %{_datadir}/doc/%{name}/freeipmi-oem-documentation-requirements.txt
%dir %{_datadir}/doc/%{name}/contrib
%dir %{_datadir}/doc/%{name}/contrib/ganglia
%doc %{_datadir}/doc/%{name}/contrib/ganglia/*
%dir %{_datadir}/doc/%{name}/contrib/nagios
%doc %{_datadir}/doc/%{name}/contrib/nagios/*
%dir %{_datadir}/doc/%{name}/contrib/pet
%doc %{_datadir}/doc/%{name}/contrib/pet/*
%{_libdir}/libipmiconsole*so.*
%{_libdir}/libfreeipmi*so.*
%{_libdir}/libipmidetect*so.*
%{_libdir}/libipmimonitoring.so.*
%{_libdir}/pkgconfig/*
%{_localstatedir}/lib/*
%{_sbindir}/bmc-config
%{_sbindir}/bmc-info
%{_sbindir}/bmc-device
%{_sbindir}/ipmi-config
%{_sbindir}/ipmi-fru
%{_sbindir}/ipmi-locate
%{_sbindir}/ipmi-oem
%{_sbindir}/ipmi-pef-config
%{_sbindir}/pef-config
%{_sbindir}/ipmi-raw
%{_sbindir}/ipmi-sel
%{_sbindir}/ipmi-sensors
%{_sbindir}/ipmi-sensors-config
%{_sbindir}/ipmiping
%{_sbindir}/ipmi-ping
%{_sbindir}/ipmipower
%{_sbindir}/ipmi-power
%{_sbindir}/rmcpping
%{_sbindir}/rmcp-ping
%{_sbindir}/ipmiconsole
%{_sbindir}/ipmi-console
%{_sbindir}/ipmimonitoring
%{_sbindir}/ipmi-chassis
%{_sbindir}/ipmi-chassis-config
%{_sbindir}/ipmi-dcmi
%{_sbindir}/ipmi-pet
%{_sbindir}/ipmidetect
%{_sbindir}/ipmi-detect
%{_mandir}/man8/bmc-config.8*
%{_mandir}/man5/bmc-config.conf.5*
%{_mandir}/man8/bmc-info.8*
%{_mandir}/man8/bmc-device.8*
%{_mandir}/man8/ipmi-config.8*
%{_mandir}/man5/ipmi-config.conf.5*
%{_mandir}/man8/ipmi-fru.8*
%{_mandir}/man8/ipmi-locate.8*
%{_mandir}/man8/ipmi-oem.8*
%{_mandir}/man8/ipmi-pef-config.8*
%{_mandir}/man8/pef-config.8*
%{_mandir}/man8/ipmi-raw.8*
%{_mandir}/man8/ipmi-sel.8*
%{_mandir}/man8/ipmi-sensors.8*
%{_mandir}/man8/ipmi-sensors-config.8*
%{_mandir}/man8/ipmiping.8*
%{_mandir}/man8/ipmi-ping.8*
%{_mandir}/man8/ipmipower.8*
%{_mandir}/man8/ipmi-power.8*
%{_mandir}/man5/ipmipower.conf.5*
%{_mandir}/man8/rmcpping.8*
%{_mandir}/man8/rmcp-ping.8*
%{_mandir}/man8/ipmiconsole.8*
%{_mandir}/man8/ipmi-console.8*
%{_mandir}/man5/ipmiconsole.conf.5*
%{_mandir}/man8/ipmimonitoring.8*
%{_mandir}/man5/ipmi_monitoring_sensors.conf.5*
%{_mandir}/man5/ipmimonitoring_sensors.conf.5*
%{_mandir}/man5/ipmimonitoring.conf.5*
%{_mandir}/man5/libipmimonitoring.conf.5*
%{_mandir}/man5/freeipmi_interpret_sel.conf.5*
%{_mandir}/man5/freeipmi_interpret_sensor.conf.5*
%{_mandir}/man8/ipmi-chassis.8*
%{_mandir}/man8/ipmi-chassis-config.8*
%{_mandir}/man8/ipmi-dcmi.8*
%{_mandir}/man8/ipmi-pet.8*
%{_mandir}/man8/ipmidetect.8*
%{_mandir}/man8/ipmi-detect.8*
%{_mandir}/man5/freeipmi.conf.5*
%{_mandir}/man5/ipmidetect.conf.5*
%{_mandir}/man7/freeipmi.7*
%{_mandir}/man5/libipmiconsole.conf.5*
%dir %{_localstatedir}/cache/ipmimonitoringsdrcache

%files devel
%defattr(-,root,root)
%dir %{_datadir}/doc/%{name}/contrib/libipmimonitoring
%doc %{_datadir}/doc/%{name}/contrib/libipmimonitoring/*
%{_libdir}/libipmiconsole.so
%{_libdir}/libfreeipmi.so
%{_libdir}/libipmidetect.so
%{_libdir}/libipmimonitoring.so
%dir %{_includedir}/freeipmi
%dir %{_includedir}/freeipmi/api
%dir %{_includedir}/freeipmi/cmds
%dir %{_includedir}/freeipmi/debug
%dir %{_includedir}/freeipmi/driver
%dir %{_includedir}/freeipmi/fiid
%dir %{_includedir}/freeipmi/fru
%dir %{_includedir}/freeipmi/interface
%dir %{_includedir}/freeipmi/interpret
%dir %{_includedir}/freeipmi/locate
%dir %{_includedir}/freeipmi/payload
%dir %{_includedir}/freeipmi/record-format
%dir %{_includedir}/freeipmi/sdr
%dir %{_includedir}/freeipmi/sel
%dir %{_includedir}/freeipmi/sensor-read
%dir %{_includedir}/freeipmi/spec
%dir %{_includedir}/freeipmi/templates
%dir %{_includedir}/freeipmi/util
%{_includedir}/ipmiconsole.h
%{_includedir}/ipmidetect.h
%{_includedir}/ipmi_monitoring*.h
%{_includedir}/freeipmi/*.h
%{_includedir}/freeipmi/api/*.h
%{_includedir}/freeipmi/cmds/*.h
%{_includedir}/freeipmi/debug/*.h
%{_includedir}/freeipmi/driver/*.h
%{_includedir}/freeipmi/fiid/*.h
%{_includedir}/freeipmi/fru/*.h
%{_includedir}/freeipmi/interface/*.h
%{_includedir}/freeipmi/interpret/*.h
%{_includedir}/freeipmi/locate/*.h
%{_includedir}/freeipmi/payload/*.h
%{_includedir}/freeipmi/record-format/*.h
%{_includedir}/freeipmi/sdr/*.h
%{_includedir}/freeipmi/sel/*.h
%{_includedir}/freeipmi/sensor-read/*.h
%{_includedir}/freeipmi/spec/*.h
%{_includedir}/freeipmi/templates/*.h
%{_includedir}/freeipmi/util/*.h
%{_mandir}/man3/*

%files bmc-watchdog
%defattr(-,root,root)
%doc %{_datadir}/doc/%{name}/COPYING.bmc-watchdog
%doc %{_datadir}/doc/%{name}/DISCLAIMER.bmc-watchdog
%doc %{_datadir}/doc/%{name}/DISCLAIMER.bmc-watchdog.UC
%config(noreplace) %{_initrddir}/bmc-watchdog
%config(noreplace) %{_sysconfdir}/sysconfig/bmc-watchdog
%{_sbindir}/bmc-watchdog
%{_mandir}/man8/bmc-watchdog.8*

%files ipmidetectd
%defattr(-,root,root)
%config(noreplace) %{_initrddir}/ipmidetectd
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/freeipmi/ipmidetectd.conf
%{_sbindir}/ipmidetectd
%{_mandir}/man5/ipmidetectd.conf.5*
%{_mandir}/man8/ipmidetectd.8*

%files ipmiseld
%defattr(-,root,root)
%doc %{_datadir}/doc/%{name}/COPYING.ipmiseld
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmiseld
%config(noreplace) %{_initrddir}/ipmiseld
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/freeipmi/ipmiseld.conf
%{_sbindir}/ipmiseld
%{_mandir}/man5/ipmiseld.conf.5*
%{_mandir}/man8/ipmiseld.8*
%dir %{_localstatedir}/cache/ipmiseld

%changelog
* Mon Aug 26 2013 Albert Chu <chu11@llnl.gov> 1.4.1
- Add ipmi-config tool and manpage

* Tue Jul 10 2012 Albert Chu <chu11@llnl.gov> 1.2.1
- Add ipmiseld daemon and subpackage.
- Update paths for libfreeipmi changes.

* Mon May 3 2012 Albert Chu <chu11@llnl.gov> 1.2.1
- Remove bmc-watchdog logrotate file.

* Mon Dec 12 2011 Albert Chu <chu11@llnl.gov> 1.1.1
- Add contrib and ipmi-pet files.
- Make main package own logdir.

* Wed Jun 29 2011 Albert Chu <chu11@llnl.gov> 1.0.4
- Add pkgconfig files.

* Fri Nov 5 2010 Albert Chu <chu11@llnl.gov> 0.9.0
- Add interpret sub-library.
- Support new config files.
- Support /etc/freeipmi/ config dir.
- Support new ipmi_monitoring*.h files.
- Support new manpages.
- Support new compatability symlinks/manpages.

* Wed Sep 30 2009 Albert Chu <chu11@llnl.gov> 0.8.0
- Update for dcmi.
- Update for renaming of pef-config.
- Update for new .h files.
- Add new ipmimonitoring config manpages.
- Add ipmidetectd.conf

* Tue Sep 29 2008 Albert Chu <chu11@llnl.gov> 0.7.0
- Add README.build

* Tue Aug 12 2008 Albert Chu <chu11@llnl.gov> 0.7.0
- Add README.sunbmc

* Mon Aug 04 2008 Albert Chu <chu11@llnl.gov> 0.7.0
- Add ipmi-chassis-config.

* Thu Jul 10 2008 Albert Chu <chu11@llnl.gov> 0.7.0
- Add freeipmi.conf default file. 
- Make 0644 perms default for config files.

* Sat May 21 2008 Albert Chu <chu11@llnl.gov> 0.7.0
- Add freeipmi.conf.5.

* Sat May 3 2008 Albert Chu <chu11@llnl.gov> 0.7.0
- Add bmc-device.

* Mon Apr 7 2008 Albert Chu <chu11@llnl.gov> 0.6.0
- Add freeipmi.7 and libfreeipmi.3 manpage.

* Wed Apr 2 2008 Albert Chu <chu11@llnl.gov> 0.6.0
- Add freeipmi-bugs-and-workarounds.txt.

* Tue Mar 27 2008 Albert Chu <chu11@llnl.gov> 0.6.0
- Add ipmi-oem tool and manpage.

* Mon Feb 18 2008 Albert Chu <chu11@llnl.gov> 0.6.0
- Add ipmi-sensors-config tool and manpage.

* Wed Jan 9 2008 Albert Chu <chu11@llnl.gov> 0.6.0
- Obsolete old subpackage freeipmi-ipmimonitoring.

* Tue Dec 18 2007 Albert Chu <chu11@llnl.gov> 0.6.0
- Use %{version} instead of 1.4.11 for substitution in paths.

* Fri Dec 14 2007 Albert Chu <chu11@llnl.gov> 0.6.0
- Update packaging for libfreeipmi reorganization

* Wed Nov 19 2007 Albert Chu <chu11@llnl.gov> 0.5.0
- Remove ipmimonitoring subpackage.  Merge into head package.

* Wed Nov 19 2007 Phil Knirsch <pknirsch@redhat.com> 0.5.0
- More fixes for Fedora Review:
 o Added ExclusiveArch due to missing lopl (#368541)
- Several fixes due to Fedora package review:
 o Fixed Group for all subpackages
 o Added missng Requires(Post|Preun) for several packages
 o Removed static libraries and .la files
 o Fixed open bug (missing mode for O_CREATE)
 o Fixed incorrect options for bmc-watchdog daemon
- Specfile cleanup for Fedora inclusion
- Fixed several rpmlint warnings and errors:
 o Moved all devel libs to proper package

* Wed Aug 01 2007 Troy Telford <ttelford@lnxi.com> 0.4.0
- Some package cleanup so it builds on SLES

* Wed Jun 13 2007 Phil Knirsch <pknirsch@redhat.com> 0.4.beta0-1
- Some package cleanup and split of configuration and initscript

* Fri Feb 28 2007 Albert Chu <chu11@llnl.gov> 0.4.beta0-1
- Add ipmidetectd subpackage.

* Fri Feb 16 2007 Albert Chu <chu11@llnl.gov> 0.4.beta0-1
- Add ipmimonitoring subpackage.

* Sun Jul 30 2006 Albert Chu <chu11@llnl.gov> 0.3.beta0-1
- Re-architect for 0.3.X

* Mon May 15 2006 Albert Chu <chu11@llnl.gov> 0.3.beta0-1
- Fixed up spec file to pass rpmlint