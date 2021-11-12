%define _hardened_build 1
%{!?release: %define release 2}
Name:                trafficserver
Version:             9.1.0
Release:             3
Summary:             Apache Traffic Server, a reverse, forward and transparent HTTP proxy cache
License:             Apache-2.0
URL:                 https://trafficserver.apache.org/
Source0:             http://www.apache.org/dist/%{name}/%{name}-%{version}.tar.bz2
Patch0000:           Add-openeuler-support.patch
Patch0001:           CVE-2021-37147.patch
Patch0002:           CVE-2021-37149.patch
Patch0003:           CVE-2021-41585.patch
Patch0004:           CVE-2021-43082.patch
Patch0005:           Fix-status-failure-after-stopping-service.patch
BuildRequires:       expat-devel hwloc-devel openssl-devel pcre-devel zlib-devel xz-devel
BuildRequires:       libcurl-devel ncurses-devel gcc gcc-c++ perl-ExtUtils-MakeMaker
BuildRequires:       libcap-devel cmake libunwind-devel automake
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
%configure \
  --enable-layout=Gentoo \
  --libdir=%{_libdir}/trafficserver \
  --libexecdir=%{_libdir}/trafficserver/plugins \
  --sysconfdir=%{_sysconfdir}/trafficserver \
  --enable-experimental-plugins \
  --with-user=ats --with-group=ats \
  %{DISABLE_UNWIND} \
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

%post
/sbin/ldconfig
%systemd_post trafficserver.service

%pre
getent group ats >/dev/null || groupadd -r ats -g 176 &>/dev/null
getent passwd ats >/dev/null || useradd -r -u 176 -g ats -d / -s /sbin/nologin -c "Apache Traffic Server" ats &>/dev/null

%preun
%systemd_preun trafficserver.service

%postun
/sbin/ldconfig
%systemd_postun_with_restart trafficserver.service

%files
%defattr(-, root, root, -)
%{!?_licensedir:%global license %%doc}
%license LICENSE
%doc README CHANGELOG* NOTICE STATUS
%config(noreplace) /etc/trafficserver/*
%{_bindir}/traffic_*
%{_bindir}/tspush
%dir %{_libdir}/trafficserver
%dir %{_libdir}/trafficserver/plugins
%{_libdir}/trafficserver/libts*.so*
%{_libdir}/trafficserver/plugins/*.so
/lib/systemd/system/trafficserver.service
%attr(0755, ats, ats) %dir /etc/trafficserver
%attr(0755, ats, ats) %dir /var/log/trafficserver
%attr(0755, ats, ats) %dir /run/trafficserver
%attr(0755, ats, ats) %dir /var/cache/trafficserver
%attr(0644, ats, ats) /etc/trafficserver/*.config
%attr(0644, ats, ats) /etc/trafficserver/*.yaml

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
* Fri Nov 12 2021 lingsheng <lingsheng@huawei.com> - 9.1.0-3
- fix stop service fail and remove SysVinit script

* Mon Nov 08 2021 wangkai <wangkai385@huawei.com> - 9.1.0-2
- fix CVE-2021-37147 CVE-2021-37149 CVE-2021-41585 CVE-2021-43082

* Tue Aug 31 2021 liyanan <liyanan32@huawei.com> - 9.1.0-1
- package init
