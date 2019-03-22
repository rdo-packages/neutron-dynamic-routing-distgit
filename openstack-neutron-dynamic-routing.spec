%global milestone .0rc1
# Macros for py2/py3 compatibility
%if 0%{?fedora} || 0%{?rhel} > 7
%global pyver %{python3_pkgversion}
%else
%global pyver 2
%endif
%global pyver_bin python%{pyver}
%global pyver_sitelib %python%{pyver}_sitelib
%global pyver_install %py%{pyver}_install
%global pyver_build %py%{pyver}_build
# End of macros for py2/py3 compatibility
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
%global modulename neutron_dynamic_routing
%global servicename neutron-dynamic-routing

%define major_version %(echo %{version} | awk 'BEGIN { FS=\".\"}; {print $1}')
%define next_version %(echo $((%{major_version} + 1)))
%define neutron_epoch 1

Name: openstack-%{servicename}
Version: 14.0.0
Release: 0.1%{?milestone}%{?dist}
Summary: OpenStack Neutron Dynamic Routing
License: ASL 2.0
URL: https://github.com/openstack/%{servicename}
Source0: http://tarballs.openstack.org/%{servicename}/%{servicename}-%{upstream_version}.tar.gz
#
# patches_base=14.0.0.0rc1
#

Source2: neutron-bgp-dragent.service

BuildArch: noarch

BuildRequires: openstack-macros
BuildRequires: python%{pyver}-devel
BuildRequires: git
BuildRequires: systemd

BuildRequires: python%{pyver}-neutron >= %{neutron_epoch}:%{major_version}
BuildRequires: python%{pyver}-oslo-config
BuildRequires: python%{pyver}-pbr
BuildRequires: python%{pyver}-setuptools
BuildRequires: python%{pyver}-os-ken >= 0.3.1

# Requirements needed by tests
BuildRequires: python%{pyver}-mock >= 2.0
# neutron.tests is imported but not specified in test-requirements.txt
# since it's in neutron project, but packaged in python-neutron-tests
BuildRequires: python%{pyver}-neutron-tests >= %{neutron_epoch}:%{major_version}
BuildRequires: python%{pyver}-neutron-tests-tempest
BuildRequires: python%{pyver}-neutron-lib-tests
BuildRequires: python%{pyver}-oslotest >= 1.10.0
BuildRequires: python%{pyver}-oslo-concurrency >= 3.8.0
BuildRequires: python%{pyver}-stestr
BuildRequires: python%{pyver}-subunit >= 0.0.18
BuildRequires: python%{pyver}-testresources >= 0.2.4
BuildRequires: python%{pyver}-testtools >= 1.4.0
BuildRequires: python%{pyver}-testscenarios >= 0.4
BuildRequires: python%{pyver}-tempest >= 17.1.0
BuildRequires: python%{pyver}-webob >= 1.7.1

# Handle python2 exception
%if %{pyver} == 2
# Requirements needed by tests
BuildRequires: python-requests-mock >= 1.1
BuildRequires: python-webtest >= 2.0
%else
# Requirements needed by tests
BuildRequires: python%{pyver}-requests-mock >= 1.1
BuildRequires: python%{pyver}-webtest >= 2.0
%endif

Requires: openstack-%{servicename}-common = %{version}-%{release}

Requires(pre): shadow-utils
%if 0%{?rhel} && 0%{?rhel} < 8
%{?systemd_requires}
%else
%{?systemd_ordering} # does not exist on EL7
%endif

%description
This is a Dynamic Routing addons for OpenStack Neutron (Networking) service.

%package -n python%{pyver}-%{servicename}
Summary: Neutron Dynamic Routing python library
%{?python_provide:%python_provide python%{pyver}-%{servicename}}

Requires: python%{pyver}-neutron >= %{neutron_epoch}:%{major_version}
Requires: python%{pyver}-eventlet >= 0.18.2
Requires: python%{pyver}-netaddr >= 0.7.18
Requires: python%{pyver}-sqlalchemy >= 1.2.0
Requires: python%{pyver}-alembic >= 0.8.10
Requires: python%{pyver}-six >= 1.10.0
Requires: python%{pyver}-neutron-lib >= 1.21.0
Requires: python%{pyver}-oslo-config >= 2:5.2.0
Requires: python%{pyver}-oslo-db >= 4.27.0
Requires: python%{pyver}-oslo-log >= 3.36.0
Requires: python%{pyver}-oslo-messaging >= 5.29.0
Requires: python%{pyver}-oslo-serialization >= 2.18.0
Requires: python%{pyver}-oslo-service >= 1.24.0
Requires: python%{pyver}-oslo-utils >= 3.33.0

# Handle python2 exception
%if %{pyver} == 2
Requires: python-httplib2 >= 0.9.1
%else
Requires: python%{pyver}-httplib2 >= 0.9.1
%endif

%description -n python%{pyver}-%{servicename}
This is Dynamic Routing service plugin for OpenStack Neutron (Networking) service.

This package contains the Neutron Dynamic Routing Python library.

%package -n python%{pyver}-%{servicename}-tests
Summary: Neutron Dynamic Routing tests
%{?python_provide:%python_provide python%{pyver}-%{servicename}-tests}

Requires: python%{pyver}-%{servicename}
Requires: python%{pyver}-neutron >= %{neutron_epoch}:%{major_version}
Requires: python%{pyver}-mock >= 2.0
Requires: python%{pyver}-oslotest >= 1.10.0
Requires: python%{pyver}-oslo-concurrency >= 3.8.0
Requires: python%{pyver}-stestr
Requires: python%{pyver}-os-ken >= 0.3.1
Requires: python%{pyver}-subunit >= 0.0.18
Requires: python%{pyver}-testresources >= 0.2.4
Requires: python%{pyver}-testtools >= 1.4.0
Requires: python%{pyver}-testscenarios >= 0.4
Requires: python%{pyver}-tempest >= 16.1.0
Requires: python%{pyver}-webob >= 1.7.1

# Handle python2 exception
%if %{pyver} == 2
Requires: python-requests-mock >= 1.1
Requires: python-webtest >= 2.0
%else
Requires: python%{pyver}-requests-mock >= 1.1
Requires: python%{pyver}-webtest >= 2.0
%endif

%description -n python%{pyver}-%{servicename}-tests
This is a Dynamic Routing service plugin for Openstack Neutron (Networking) service.

This package contains Neutron Dynamic Routing test files.

%package common
Summary: Neutron Dynamic Routing common package
Requires: python%{pyver}-%{servicename} = %{version}-%{release}
Requires: openstack-neutron-common

%description common
This is Dynamic Routing service plugin for OpenStack Neutron (Networking) service.

This package contains Dynamic Routing common files.

%package -n openstack-neutron-bgp-dragent
Summary: Neutron BGP Dynamic Routing agent
Requires: openstack-neutron-dynamic-routing-common = %{version}-%{release}
Requires: python%{pyver}-os-ken >= 0.3.1

%description -n openstack-neutron-bgp-dragent
This package contains the Neutron BGP Dynamic Routing agent that will host
different BGP speaking drivers and makes the required BGP peering session/s for
Neutron.

%prep
%autosetup -n %{servicename}-%{upstream_version} -S git

# Let's handle dependencies ourseleves
%py_req_cleanup

%build
%{pyver_build}

# Generate sample config files
for file in `ls etc/oslo-config-generator/*`; do
    oslo-config-generator-%{pyver} --config-file=$file
done

find etc -name *.sample | while read filename
do
    filedir=$(dirname $filename)
    file=$(basename $filename .sample)
    mv ${filename} ${filedir}/${file}
done

%install
%{pyver_install}

# Remove unused files
rm -rf %{buildroot}%{pyver_sitelib}/bin
rm -rf %{buildroot}%{pyver_sitelib}/doc
rm -rf %{buildroot}%{pyver_sitelib}/tools

# Setup directories
install -d -m 755 %{buildroot}%{_datadir}/%{servicename}
install -d -m 755 %{buildroot}%{_sharedstatedir}/%{servicename}
install -d -m 755 %{buildroot}%{_localstatedir}/log/%{servicename}

# Move config files to proper location
install -d -m 755 %{buildroot}%{_sysconfdir}/neutron

# The generated config files are not moved automatically by setup.py
mv etc/*.ini %{buildroot}%{_sysconfdir}/neutron

# Install systemd units
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/neutron-bgp-dragent.service

# Create configuration directories that can be populated by users with custom *.conf files
mkdir -p %{buildroot}/%{_sysconfdir}/neutron/conf.d/neutron-bgp-dragent

%check
# FIXME(jpena): we need to ignore unit test results
# until https://bugs.launchpad.net/neutron/+bug/1803745 is fixed
stestr-%{pyver} run || true

%post -n openstack-neutron-bgp-dragent
%systemd_post neutron-bgp-dragent.service

%preun -n openstack-neutron-bgp-dragent
%systemd_preun neutron-bgp-dragent.service

%postun -n openstack-neutron-bgp-dragent
%systemd_postun_with_restart neutron-bgp-dragent.service

%files -n python%{pyver}-%{servicename}
%license LICENSE
%doc AUTHORS CONTRIBUTING.rst README.rst
%{pyver_sitelib}/%{modulename}
%{pyver_sitelib}/%{modulename}-*.egg-info
%exclude %{pyver_sitelib}/%{modulename}/tests

%files -n python%{pyver}-%{servicename}-tests
%{pyver_sitelib}/%{modulename}/tests

%files common
%license LICENSE

%files -n openstack-neutron-bgp-dragent
%license LICENSE
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/bgp_dragent.ini
%{_sysconfdir}/neutron/conf.d/neutron-bgp-dragent
%{_bindir}/neutron-bgp-dragent
%{_unitdir}/neutron-bgp-dragent.service

%changelog
* Fri Mar 22 2019 RDO <dev@lists.rdoproject.org> 14.0.0-0.1.0rc1
- Update to 14.0.0.0rc1

