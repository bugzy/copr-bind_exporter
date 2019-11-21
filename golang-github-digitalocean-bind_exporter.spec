%global debug_package %{nil}
%global gitdate 20190923
%global gitcommit 13c5eb2110ddbc7fd22c8e69e5cd4b97840d529b
%global shortcommit %(c=%{gitcommit}; echo ${c:0:7})

%global provider        github
%global provider_tld    com
%global project         digitalocean
%global repo            bind_exporter
# https://github.com/digitalocean/bind_exporter/
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}
%global import_path     %{provider_prefix}

Name:    golang-%{provider}-%{project}-%{repo}
Version: 0.2
Release: 0.git%{gitdate}%{?dist}
Summary: Prometheus exporter for BIND
License: ASL 2.0
URL:     https://%{provider_prefix}
Source0: https://%{provider_prefix}/archive/%{gitcommit}/%{repo}-%{shortcommit}.tar.gz
Source1: %{repo}.service
Source2: %{repo}.default

%{?el7:%{?systemd_requires}}
Requires(pre): shadow-utils
BuildRequires: golang, git, systemd

%description

Export BIND(named/dns) v9+ service metrics to Prometheus.

%prep

%setup -q -n %{repo}-%{gitcommit}

%build
mkdir _build
export GOPATH=$(pwd)/_build
go get -v -d
#go build -v %{repo}.go
cd $GOPATH/src/github.com/digitalocean/bind_exporter
make

%install
cd _build/src/github.com/digitalocean/bind_exporter
mkdir -vp %{buildroot}/%{_sharedstatedir}/bind_exporter
mkdir -vp %{buildroot}/%{_bindir}
mkdir -vp %{buildroot}/%{_unitdir}
mkdir -vp %{buildroot}/%{_sysconfdir}/%{repo}
install -m 755 %{repo} %{buildroot}/%{_bindir}/%{repo}
install -m 644 %{SOURCE1} %{buildroot}/%{_unitdir}/%{repo}.service
install -m 644 %{SOURCE2} %{buildroot}/%{_sysconfdir}/%{repo}/%{repo}.conf

%pre
getent group bind_exporter >/dev/null || groupadd -r bind_exporter
getent passwd bind_exporter >/dev/null || \
  useradd -r -g bind_exporter -d /%{_sharedstatedir}/bind_exporter -s /sbin/nologin \
          -c "Prometheus DNS metrics exporter" bind_exporter
exit 0

%post
%systemd_post %{repo}.service

%preun
%systemd_preun %{repo}.service

%postun
%systemd_postun %{repo}.service

%files
%{_bindir}/%{repo}
%{_unitdir}/%{repo}.service
%config(noreplace) /etc/%{repo}/%{repo}
%attr(755, bind_exporter, bind_exporter)/%{_sharedstatedir}/bind_exporter
%doc CHANGELOG.md LICENSE NOTICE README.md

%changelog
* Thu Nov 21 2019 Bugzy Little <bugzylittle@gmail.com> - 0.2-0.git20190923
- Change config paths 
- Change systemd unit files
- Change daemon user and group
- Remove unused init files

* Mon Sep 23 2019 Rick Elrod <relrod@redhat.com> - 0.0-0.git20190923
- Nuke el6 conditionals, assume el7+
- Fix the build
- Use rpm macros where we can instead of hardcoded paths

* Thu Jan 19 2017 Ilya Otyutskiy <ilya.otyutskiy@icloud.com> - 0.0-0.git20170119.vortex
- Initial packaging
