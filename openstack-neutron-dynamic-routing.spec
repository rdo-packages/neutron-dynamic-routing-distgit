%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
%global modulename neutron_dynamic_routing
%global servicename neutron-dynamic-routing

%define major_version %(echo %{version} | awk 'BEGIN { FS=\".\"}; {print $1}')
%define next_version %(echo $((%{major_version} + 1)))
%define neutron_epoch 1

Name: openstack-%{servicename}
Version: 13.1.0
Release: 1%{?dist}
Summary: OpenStack Neutron Dynamic Routing
License: ASL 2.0
URL: https://github.com/openstack/%{servicename}
Source0: http://tarballs.openstack.org/%{servicename}/%{servicename}-%{upstream_version}.tar.gz
#

Source2: neutron-bgp-dragent.service

BuildArch: noarch

BuildRequires: openstack-macros
BuildRequires: python2-devel
BuildRequires: python-neutron >= %{neutron_epoch}:%{major_version}
BuildRequires: python-oslo-config
BuildRequires: python-pbr
BuildRequires: python-setuptools
BuildRequires: git
BuildRequires: systemd

# Requirements needed by tests
BuildRequires: python-mock >= 2.0
# neutron.tests is imported but not specified in test-requirements.txt
# since it's in neutron project, but packaged in python-neutron-tests
BuildRequires: python-neutron-tests >= %{neutron_epoch}:%{major_version}
BuildRequires: python2-neutron-lib-tests
BuildRequires: python-oslotest >= 1.10.0
BuildRequires: python-oslo-concurrency >= 3.8.0
BuildRequires: python-stestr
BuildRequires: python-requests-mock >= 1.1
BuildRequires: python-ryu >= 4.24
BuildRequires: python-subunit >= 0.0.18
BuildRequires: python-testresources >= 0.2.4
BuildRequires: python-testtools >= 1.4.0
BuildRequires: python-testscenarios >= 0.4
BuildRequires: python-tempest >= 17.1.0
BuildRequires: python-webob >= 1.7.1
BuildRequires: python-webtest >= 2.0
BuildRequires: python2-neutron-lib-tests
BuildRequires: python2-neutron-tests-tempest

Requires: openstack-%{servicename}-common = %{version}-%{release}

Requires(pre): shadow-utils
%{systemd_requires}

%description
This is a Dynamic Routing addons for OpenStack Neutron (Networking) service.

%package -n python2-%{servicename}
Summary: Neutron Dynamic Routing python library

Requires: python-neutron >= %{neutron_epoch}:%{major_version}
Requires: python2-eventlet >= 0.18.2
Requires: python-httplib2 >= 0.9.1
Requires: python2-netaddr >= 0.7.18
Requires: python2-sqlalchemy >= 1.2.0
Requires: python2-alembic >= 0.8.10
Requires: python2-six >= 1.10.0
Requires: python2-neutron-lib >= 1.18.0
Requires: python2-oslo-config >= 2:5.2.0
Requires: python2-oslo-db >= 4.27.0
Requires: python2-oslo-log >= 3.36.0
Requires: python2-oslo-messaging >= 5.29.0
Requires: python2-oslo-serialization >= 2.18.0
Requires: python2-oslo-service >= 1.24.0
Requires: python2-oslo-utils >= 3.33.0

%description -n python2-%{servicename}
This is Dynamic Routing service plugin for OpenStack Neutron (Networking) service.

This package contains the Neutron Dynamic Routing Python library.

%package -n python2-%{servicename}-tests
Summary: Neutron Dynamic Routing tests

Requires: python-neutron >= %{neutron_epoch}:%{major_version}
Requires: python2-%{servicename}
Requires: python-mock >= 2.0
Requires: python-oslotest >= 1.10.0
Requires: python-oslo-concurrency >= 3.8.0
Requires: python-stestr
Requires: python-requests-mock >= 1.1
Requires: python-ryu >= 4.24
Requires: python-subunit >= 0.0.18
Requires: python-testresources >= 0.2.4
Requires: python-testtools >= 1.4.0
Requires: python-testscenarios >= 0.4
Requires: python-tempest >= 16.1.0
Requires: python-webob >= 1.7.1
Requires: python-webtest >= 2.0

%description -n python2-%{servicename}-tests
This is a Dynamic Routing service plugin for Openstack Neutron (Networking) service.

This package contains Neutron Dynamic Routing test files.

%package common
Summary: Neutron Dynamic Routing common package
Requires: python2-%{servicename} = %{version}-%{release}
Requires: openstack-neutron-common

%description common
This is Dynamic Routing service plugin for OpenStack Neutron (Networking) service.

This package contains Dynamic Routing common files.

%package -n openstack-neutron-bgp-dragent
Summary: Neutron BGP Dynamic Routing agent
Requires: openstack-neutron-dynamic-routing-common = %{version}-%{release}
Requires: python2-ryu >= 4.24

%description -n openstack-neutron-bgp-dragent
This package contains the Neutron BGP Dynamic Routing agent that will host
different BGP speaking drivers and makes the required BGP peering session/s for
Neutron.

%prep
%autosetup -n %{servicename}-%{upstream_version} -S git

# Let's handle dependencies ourseleves
%py_req_cleanup

%build
%py2_build

# Generate sample config files
for file in `ls etc/oslo-config-generator/*`; do
    oslo-config-generator --config-file=$file
done

find etc -name *.sample | while read filename
do
    filedir=$(dirname $filename)
    file=$(basename $filename .sample)
    mv ${filename} ${filedir}/${file}
done

%install
%py2_install

# Remove unused files
rm -rf %{buildroot}%{python2_sitelib}/bin
rm -rf %{buildroot}%{python2_sitelib}/doc
rm -rf %{buildroot}%{python2_sitelib}/tools

# Setup directories
install -d -m 755 %{buildroot}%{_datadir}/%{servicename}
install -d -m 755 %{buildroot}%{_sharedstatedir}/%{servicename}
install -d -m 755 %{buildroot}%{_localstatedir}/log/%{servicename}

# Move policy files to proper location
install -d -m 755 %{buildroot}%{_sysconfdir}/neutron
mv %{buildroot}/usr/etc/neutron/policy.d %{buildroot}/%{_sysconfdir}/neutron

# Move config files to proper location
install -d -m 755 %{buildroot}%{_sysconfdir}/neutron

# The generated config files are not moved automatically by setup.py
mv etc/*.ini %{buildroot}%{_sysconfdir}/neutron

# Install systemd units
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/neutron-bgp-dragent.service

# Create configuration directories that can be populated by users with custom *.conf files
mkdir -p %{buildroot}/%{_sysconfdir}/neutron/conf.d/neutron-bgp-dragent

%check
stestr run

%post -n openstack-neutron-bgp-dragent
%systemd_post neutron-bgp-dragent.service

%preun -n openstack-neutron-bgp-dragent
%systemd_preun neutron-bgp-dragent.service

%postun -n openstack-neutron-bgp-dragent
%systemd_postun_with_restart neutron-bgp-dragent.service

%files -n python2-%{servicename}
%license LICENSE
%doc AUTHORS CONTRIBUTING.rst README.rst
%{python2_sitelib}/%{modulename}
%{python2_sitelib}/%{modulename}-*.egg-info
%exclude %{python2_sitelib}/%{modulename}/tests

%files -n python2-%{servicename}-tests
%{python2_sitelib}/%{modulename}/tests

%files common
%license LICENSE
%config(noreplace) %attr(-, root, neutron) %{_sysconfdir}/neutron/policy.d/*

%files -n openstack-neutron-bgp-dragent
%license LICENSE
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/bgp_dragent.ini
%{_sysconfdir}/neutron/conf.d/neutron-bgp-dragent
%{_bindir}/neutron-bgp-dragent
%{_unitdir}/neutron-bgp-dragent.service

%changelog
* Fri Feb 28 2020 RDO <dev@lists.rdoproject.org> 13.1.0-1
- Update to 13.1.0

* Wed Feb 27 2019 RDO <dev@lists.rdoproject.org> 13.0.1-1
- Update to 13.0.1

* Thu Oct 11 2018 RDO <dev@lists.rdoproject.org> 13.0.0-2
- Fix common package not being updated.

* Thu Aug 30 2018 RDO <dev@lists.rdoproject.org> 13.0.0-1
- Update to 13.0.0

* Mon Aug 20 2018 RDO <dev@lists.rdoproject.org> 13.0.0-0.1.0rc1
- Update to 13.0.0.0rc1
