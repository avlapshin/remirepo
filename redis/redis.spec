# Check for status of man pages
# http://code.google.com/p/redis/issues/detail?id=202

%ifarch %{ix86} x86_64 ppc
# available only on selected architectures
%global with_perftools 1
%endif

%if 0%{?fedora} >= 15 || 0%{?rhel} >= 7
%global with_systemd 1
%else
%global with_systemd 0
%endif

Name:             redis
Version:          2.6.10
Release:          %{?prever:0.}1%{?prever:.%{prever}}%{?dist}
Summary:          A persistent key-value database

Group:            Applications/Databases
License:          BSD
URL:              http://redis.io
Source0:          http://redis.googlecode.com/files/%{name}-%{version}%{?prever:-%{prever}}.tar.gz
Source1:          %{name}.logrotate
Source2:          %{name}.init
Source3:          %{name}.service
# Update configuration for Fedora
Patch0:           %{name}-2.6.10-conf.patch

BuildRoot:        %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%if !0%{?el5}
BuildRequires:    tcl >= 8.5
%if 0%{?with_perftools}
BuildRequires:    google-perftools-devel
%endif
%endif

Requires:         logrotate
Requires(pre):    shadow-utils
%if %{with_systemd}
BuildRequires:    systemd-units
Requires(post):   systemd-units
Requires(preun):  systemd-units
Requires(postun): systemd-units
%else
Requires(post):   chkconfig
Requires(preun):  chkconfig
Requires(preun):  initscripts
Requires(postun): initscripts
%endif


%description
Redis is an advanced key-value store. It is similar to memcached but the data
set is not volatile, and values can be strings, exactly like in memcached, but
also lists, sets, and ordered sets. All this data types can be manipulated with
atomic operations to push/pop elements, add/remove elements, perform server side
union, intersection, difference between sets, and so forth. Redis supports
different kind of sorting abilities.

%prep
%setup -q -n %{name}-%{version}%{?prever:-%{prever}}
%patch0 -p1 -b .orig


%build
make %{?_smp_mflags} \
  DEBUG="" \
  CFLAGS='%{optflags}' \
%if 0%{?rhel} >= 6 || 0%{?fedora} >= 13
%if 0%{?with_perftools}
  USE_TCMALLOC=yes \
%endif
%endif
  all

%check
%if !0%{?el5}
# make test
%endif

%install
make install PREFIX=%{buildroot}%{_prefix}
# Install misc other
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
install -p -D -m 644 %{name}.conf %{buildroot}%{_sysconfdir}/%{name}.conf
install -d -m 755 %{buildroot}%{_localstatedir}/lib/%{name}
install -d -m 755 %{buildroot}%{_localstatedir}/log/%{name}
install -d -m 755 %{buildroot}%{_localstatedir}/run/%{name}

# Install systemd unit
%if %{with_systemd}
install -p -D -m 644 %{SOURCE3} %{buildroot}%{_unitdir}/%{name}.service
%else
sed -e '/^daemonize/s/no/yes/' \
    -i %{buildroot}%{_sysconfdir}/%{name}.conf
install -p -D -m 755 %{SOURCE2} %{buildroot}%{_initrddir}/%{name}
%endif

# Fix non-standard-executable-perm error
chmod 755 %{buildroot}%{_bindir}/%{name}-*

# Ensure redis-server location doesn't change
mkdir -p %{buildroot}%{_sbindir}
mv %{buildroot}%{_bindir}/%{name}-server %{buildroot}%{_sbindir}/%{name}-server

%post
%if 0%{?systemd_post:1}
%systemd_post redis.service
%else
if [ $1 = 1 ]; then
  # Initial installation
%if %{with_systemd}
  /bin/systemctl daemon-reload >/dev/null 2>&1 || :
%else
  /sbin/chkconfig --add redis
%endif
fi
%endif

%pre
getent group redis &> /dev/null || groupadd -r redis &> /dev/null
getent passwd redis &> /dev/null || \
useradd -r -g redis -d %{_sharedstatedir}/redis -s /sbin/nologin \
        -c 'Redis Server' redis &> /dev/null
exit 0

%preun
%if 0%{?systemd_preun:1}
%systemd_preun redis.service
%else
if [ $1 = 0 ]; then
  # Package removal, not upgrade
%if %{with_systemd}
  /bin/systemctl --no-reload disable redis.service >/dev/null 2>&1 || :
  /bin/systemctl stop redis.service >/dev/null 2>&1 || :
%else
  /sbin/service redis stop &> /dev/null
  /sbin/chkconfig --del redis &> /dev/null
%endif
fi
%endif

%if 0%{?systemd_postun_with_restart:1}
%systemd_postun_with_restart redis.service
%else
%if %{with_systemd}
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ]; then
  # Package upgrade, not uninstall
  /bin/systemctl try-restart redis.service >/dev/null 2>&1 || :
fi
%else
if [ $1 -ge 1 ]; then
  /sbin/service redis condrestart >/dev/null 2>&1 || :
fi
%endif
%endif


%files
%defattr(-,root,root,-)
%doc 00-RELEASENOTES BUGS CONTRIBUTING COPYING README
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/%{name}.conf
%dir %attr(0755, redis, root) %{_localstatedir}/lib/%{name}
%dir %attr(0755, redis, root) %{_localstatedir}/log/%{name}
%dir %attr(0755, redis, root) %{_localstatedir}/run/%{name}
%{_bindir}/%{name}-*
%{_sbindir}/%{name}-*
%if %{with_systemd}
%{_unitdir}/%{name}.service
%else
%{_initrddir}/%{name}
%endif


%changelog
* Mon Feb 11 2013 Remi Collet <remi@fedoraproject.org> - 2.6.10-1
- Redis 2.6.10
  upgrade urgency: MODERATE, this release contains many non
  critical fixes and many small improvements.

* Thu Jan 17 2013 Remi Collet <remi@fedoraproject.org> - 2.6.9-1
- Redis 2.6.9
  upgrade urgency: MODERATE if you use replication.

* Fri Jan 11 2013 Remi Collet <remi@fedoraproject.org> - 2.6.8-1
- Redis 2.6.8
  upgrade urgency: MODERATE if you use Lua scripting. Otherwise LOW.

* Tue Dec  4 2012 Remi Collet <remi@fedoraproject.org> - 2.6.7-1
- Redis 2.6.7
  upgrade urgency: MODERATE (unless you BLPOP using the same
  key multiple times).

* Fri Nov 23 2012 Remi Collet <remi@fedoraproject.org> - 2.6.5-1
- Redis 2.6.5 (upgrade urgency: moderate)

* Fri Nov 16 2012 Remi Collet <remi@fedoraproject.org> - 2.6.4-1
- Redis 2.6.4 (upgrade urgency: low)

* Sun Oct 28 2012 Remi Collet <remi@fedoraproject.org> - 2.6.2-1
- Redis 2.6.2 (upgrade urgency: low)
- fix typo in systemd macro

* Wed Oct 24 2012 Remi Collet <remi@fedoraproject.org> - 2.6.0-1
- Redis 2.6.0 is the latest stable version
- add patch for old glibc on RHEL-5

* Sat Oct 20 2012 Remi Collet <remi@fedoraproject.org> - 2.6.0-0.2.rc8
- Update to redis 2.6.0-rc8
- improve systemd integration

* Thu Aug 30 2012 Remi Collet <remi@fedoraproject.org> - 2.6.0-0.1.rc6
- Update to redis 2.6.0-rc6

* Thu Aug 30 2012 Remi Collet <remi@fedoraproject.org> - 2.4.16-1
- Update to redis 2.4.16

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.15-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sun Jul 08 2012 Silas Sewell <silas@sewell.org> - 2.4.15-2
- Remove TODO from docs

* Sun Jul 08 2012 Silas Sewell <silas@sewell.org> - 2.4.15-1
- Update to redis 2.4.15

* Sat May 19 2012 Silas Sewell <silas@sewell.org> - 2.4.13-1
- Update to redis 2.4.13

* Sat Mar 31 2012 Silas Sewell <silas@sewell.org> - 2.4.10-1
- Update to redis 2.4.10

* Fri Feb 24 2012 Silas Sewell <silas@sewell.org> - 2.4.8-1
- Update to redis 2.4.8

* Sat Feb 04 2012 Silas Sewell <silas@sewell.org> - 2.4.7-1
- Update to redis 2.4.7

* Wed Feb 01 2012 Fabian Deutsch <fabiand@fedoraproject.org> - 2.4.6-4
- Fixed a typo in the spec

* Tue Jan 31 2012 Fabian Deutsch <fabiand@fedoraproject.org> - 2.4.6-3
- Fix .service file, to match config (Type=simple).

* Tue Jan 31 2012 Fabian Deutsch <fabiand@fedoraproject.org> - 2.4.6-2
- Fix .service file, credits go to Timon.

* Thu Jan 12 2012 Fabian Deutsch <fabiand@fedoraproject.org> - 2.4.6-1
- Update to 2.4.6
- systemd unit file added
- Compiler flags changed to compile 2.4.6
- Remove doc/ and Changelog

* Sun Jul 24 2011 Silas Sewell <silas@sewell.org> - 2.2.12-1
- Update to redis 2.2.12

* Fri May 06 2011 Dan Horák <dan[at]danny.cz> - 2.2.5-2
- google-perftools exists only on selected architectures

* Sat Apr 23 2011 Silas Sewell <silas@sewell.ch> - 2.2.5-1
- Update to redis 2.2.5

* Sat Mar 26 2011 Silas Sewell <silas@sewell.ch> - 2.2.2-1
- Update to redis 2.2.2

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sun Dec 19 2010 Silas Sewell <silas@sewell.ch> - 2.0.4-1
- Update to redis 2.0.4

* Tue Oct 19 2010 Silas Sewell <silas@sewell.ch> - 2.0.3-1
- Update to redis 2.0.3

* Fri Oct 08 2010 Silas Sewell <silas@sewell.ch> - 2.0.2-1
- Update to redis 2.0.2
- Disable checks section for el5

* Sat Sep 11 2010 Silas Sewell <silas@sewell.ch> - 2.0.1-1
- Update to redis 2.0.1

* Sat Sep 04 2010 Silas Sewell <silas@sewell.ch> - 2.0.0-1
- Update to redis 2.0.0

* Thu Sep 02 2010 Silas Sewell <silas@sewell.ch> - 1.2.6-3
- Add Fedora build flags
- Send all scriplet output to /dev/null
- Remove debugging flags
- Add redis.conf check to init script

* Mon Aug 16 2010 Silas Sewell <silas@sewell.ch> - 1.2.6-2
- Don't compress man pages
- Use patch to fix redis.conf

* Tue Jul 06 2010 Silas Sewell <silas@sewell.ch> - 1.2.6-1
- Initial package
