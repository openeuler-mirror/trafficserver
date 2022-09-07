%define _hardened_build 1
Name:                trafficserver
Version:             9.1.3
Release:             4
Summary:             Apache Traffic Server, a reverse, forward and transparent HTTP proxy cache
License:             Apache-2.0
URL:                 https://trafficserver.apache.org/
Source0:             http://www.apache.org/dist/%{name}/%{name}-%{version}.tar.bz2
Patch0000:           Add-openeuler-support.patch
Patch0001:           Fix-status-failure-after-stopping-service.patch
Patch0002:           Fix-log-in-debug-mode.patch
Patch0003:           config-layout-openEuler.patch
BuildRequires:       expat-devel hwloc-devel openssl-devel pcre-devel zlib-devel xz-devel
BuildRequires:       libcurl-devel ncurses-devel gcc gcc-c++ perl-ExtUtils-MakeMaker
BuildRequires:       libcap-devel cmake libunwind-devel automake chrpath
Requires:            expat hwloc openssl pcre zlib xz libcurl
Requires:            systemd ncurses pkgconfig libcap initscripts
Requires(postun): systemd
%description
Apache Traffic Server is an OpenSource HTTP / HTTPS / HTTP/2 / QUIC reverse,
forward and transparent proxy and cache.

%package devel
Summary:             Apache Traffic Server devel package
Requires:            trafficserver = %{version}-%{release}
%description devel
Include files and various tools for ATS developers.

%package perl
Summary:             ATS management Perl bindings
Requires:            trafficserver = %{version}-%{release}
%description perl
This package contains some Perl APIs for talking to the ATS management port.

%prep
%autosetup -n %{name}-%{version} -p1

%build
autoreconf
./configure \
  --enable-layout=openEuler \
  --libdir=%{_libdir}/trafficserver \
  --libexecdir=%{_libdir}/trafficserver/plugins \
  --enable-experimental-plugins \
  --with-user=ats --with-group=ats \
  --disable-silent-rules
make %{?_smp_mflags} V=1

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install
mkdir -p %{buildroot}/lib/systemd/system
cp rc/trafficserver.service %{buildroot}/lib/systemd/system
find %{buildroot} -type f -name "*.la" -delete
find %{buildroot} -type f -name "*.a" -delete
find %{buildroot} -type f -name "*.pod" -delete
find %{buildroot} -type f -name "*.in" -delete
find %{buildroot} -type f -name ".packlist" -delete
find %{buildroot} -type f -name "plugin_*.so" -delete
mkdir -p %{buildroot}%{_datadir}/perl5
mv %{buildroot}/usr/lib/perl5/* %{buildroot}%{_datadir}/perl5
mkdir -p %{buildroot}/run/trafficserver
mkdir -p %{buildroot}%{_datadir}/pkgconfig
mv %{buildroot}%{_libdir}/trafficserver/pkgconfig/trafficserver.pc %{buildroot}%{_datadir}/pkgconfig
rm -f %{buildroot}%{_bindir}/trafficserver

file `find %{buildroot}/%{_bindir} -type f` | grep -w ELF | awk -F: '{print $1}' | xargs chrpath -d
chrpath -d  %{buildroot}/%{_libdir}/trafficserver/libtsmgmt.so.9.1.3
chrpath -d  %{buildroot}/%{_libdir}/trafficserver/libtscore.so.9.1.3
chrpath -d  %{buildroot}/%{_libdir}/trafficserver/plugins/server_push_preload.so
chrpath -d  %{buildroot}/%{_libdir}/trafficserver/plugins/redo_cache_lookup.so

mkdir -p %{buildroot}/etc/ld.so.conf.d

echo "/usr/lib64/trafficserver" > %{buildroot}/etc/ld.so.conf.d/%{name}-%{_arch}.conf

%post
/sbin/ldconfig
if [ $1 -eq 1 ] && [ -x /usr/bin/systemctl ]; then
    # Initial installation
    /usr/bin/systemctl --no-reload preset trafficserver.service || :
fi

%pre
getent group ats >/dev/null || groupadd -r ats -g 176 &>/dev/null
getent passwd ats >/dev/null || useradd -r -u 176 -g ats -d / -s /sbin/nologin -c "Apache Traffic Server" ats &>/dev/null

%preun
if [ $1 -eq 0 ] && [ -x /usr/bin/systemctl ]; then
    # Package removal, not upgrade
    /usr/bin/systemctl --no-reload disable --now trafficserver.service || :
fi

%postun
/sbin/ldconfig
if [ $1 -ge 1 ] && [ -x /usr/bin/systemctl ]; then
    # Package upgrade, not uninstall
    /usr/bin/systemctl try-restart trafficserver.service || :
fi

%files
%defattr(-, root, root, -)
%{!?_licensedir:%global license %%doc}
%license LICENSE
%doc README CHANGELOG* NOTICE STATUS
%config(noreplace) /usr/etc/trafficserver/*
%{_bindir}/traffic_*
%{_bindir}/tspush
%dir %{_libdir}/trafficserver
%dir %{_libdir}/trafficserver/plugins
%{_libdir}/trafficserver/libts*.so*
%{_libdir}/trafficserver/plugins/*.so
/lib/systemd/system/trafficserver.service
%attr(0755, ats, ats) %dir /usr/etc/trafficserver
%attr(0755, ats, ats) %dir /usr/var/trafficserver/log
%attr(0755, ats, ats) %dir /usr/var/trafficserver/run
%attr(0755, ats, ats) %dir /usr/var/trafficserver/cache
%attr(0644, ats, ats) /usr/etc/trafficserver/*.config
%attr(0644, ats, ats) /usr/etc/trafficserver/*.yaml
%config(noreplace) /etc/ld.so.conf.d/*

%files perl
%defattr(-,root,root,-)
%{_mandir}/man3/*
%{_datadir}/perl5/Apache/*

%files devel
%defattr(-,root,root,-)
%{_bindir}/tsxs
%{_includedir}/ts
%{_includedir}/tscpp
%{_datadir}/pkgconfig/trafficserver.pc

%changelog
* Wed Sep 07 2022 wangkai <wangkai385@h-partners.com> - 9.1.3-4
- Add log,run,cache dir

* Tue Aug 30 2022 wangkai <wangkai385@h-partners.com> - 9.1.3-3
- Fix traffic_layout remove core dumped

* Thu Aug 25 2022 liyanan <liyanan32@h-partners.com> - 9.1.3-2
- fix rpath problem

* Mon Aug 22 2022 panyanshuang <panyanshuang@ncti-gba.cn> - 9.1.3-1
- Upgrade to 9.1.3 to  fix CVE-2022-31779

* Sat Jul 30 2022 Ge Wang <wangge20@h-partners.com> - 9.1.2-2
- Modify scriptlet

* Thu May 19 2022 wangkai <wangkai385@h-partners.com> - 9.1.2-1
- Update to 9.1.2 for fix CVE-2021-44040

* Mon May 09 2022 wulei <wulei80@h-partners.com> - 9.1.0-5
- Fix traffic_top build when using -Werror=format-security

* Sat Nov 13 2021 caodongxia <caodongxia@huawei.com> - 9.1.0-4
- fix log in debug mode

* Fri Nov 12 2021 lingsheng <lingsheng@huawei.com> - 9.1.0-3
- fix stop service fail and remove SysVinit script

* Mon Nov 08 2021 wangkai <wangkai385@huawei.com> - 9.1.0-2
- fix CVE-2021-37147 CVE-2021-37149 CVE-2021-41585 CVE-2021-43082

* Tue Aug 31 2021 liyanan <liyanan32@huawei.com> - 9.1.0-1
- package init
