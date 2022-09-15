%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0x2426b928085a020d8a90d0d879ab7008d0896c8a
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
%global modulename neutron_dynamic_routing
%global servicename neutron-dynamic-routing

%define major_version %(echo %{version} | awk 'BEGIN { FS=\".\"}; {print $1}')
%define next_version %(echo $((%{major_version} + 1)))
%define neutron_epoch 1

Name: openstack-%{servicename}
Version: XXX
Release: XXX
Summary: OpenStack Neutron Dynamic Routing
License: ASL 2.0
URL: https://github.com/openstack/%{servicename}
Source0: http://tarballs.openstack.org/%{servicename}/%{servicename}-%{upstream_version}.tar.gz
Source2: neutron-bgp-dragent.service
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
Source101:        http://tarballs.openstack.org/%{servicename}/%{servicename}-%{upstream_version}.tar.gz.asc
Source102:        https://releases.openstack.org/_static/%{sources_gpg_sign}.txt
%endif

BuildArch: noarch

# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
BuildRequires:  /usr/bin/gpgv2
%endif

BuildRequires: openstack-macros
BuildRequires: python3-devel
BuildRequires: git-core
BuildRequires: systemd

BuildRequires: python3-neutron >= %{neutron_epoch}:%{major_version}
BuildRequires: python3-oslo-config
BuildRequires: python3-pbr
BuildRequires: python3-setuptools
BuildRequires: python3-os-ken >= 0.3.1

# Requirements needed by tests
BuildRequires: python3-mock >= 2.0
# neutron.tests is imported but not specified in test-requirements.txt
# since it's in neutron project, but packaged in python-neutron-tests
BuildRequires: python3-neutron-tests >= %{neutron_epoch}:%{major_version}
BuildRequires: python3-neutron-tests-tempest
BuildRequires: python3-neutron-lib-tests
BuildRequires: python3-oslotest >= 1.10.0
BuildRequires: python3-oslo-concurrency >= 3.8.0
BuildRequires: python3-stestr
BuildRequires: python3-subunit >= 0.0.18
BuildRequires: python3-testresources >= 0.2.4
BuildRequires: python3-testtools >= 1.4.0
BuildRequires: python3-testscenarios >= 0.4
BuildRequires: python3-tempest >= 17.1.0
BuildRequires: python3-webob >= 1.7.1

# Requirements needed by tests
BuildRequires: python3-requests-mock >= 1.1
BuildRequires: python3-webtest >= 2.0

Requires: openstack-%{servicename}-common = %{version}-%{release}

Requires(pre): shadow-utils
%if 0%{?rhel} && 0%{?rhel} < 8
%{?systemd_requires}
%else
%{?systemd_ordering} # does not exist on EL7
%endif

%description
This is a Dynamic Routing addons for OpenStack Neutron (Networking) service.

%package -n python3-%{servicename}
Summary: Neutron Dynamic Routing python library
%{?python_provide:%python_provide python3-%{servicename}}

Requires: python3-neutron >= %{neutron_epoch}:%{major_version}
Requires: python3-eventlet >= 0.18.2
Requires: python3-netaddr >= 0.7.18
Requires: python3-sqlalchemy >= 1.3.3
Requires: python3-alembic >= 0.9.6
Requires: python3-neutron-lib >= 1.26.0
Requires: python3-oslo-config >= 2:5.2.0
Requires: python3-oslo-db >= 4.44.0
Requires: python3-oslo-log >= 3.36.0
Requires: python3-oslo-messaging >= 5.29.0
Requires: python3-oslo-serialization >= 2.18.0
Requires: python3-oslo-service >= 1.24.0
Requires: python3-oslo-utils >= 4.5.0
Requires: python3-pbr >= 2.0.0

Requires: python3-httplib2 >= 0.9.1

%description -n python3-%{servicename}
This is Dynamic Routing service plugin for OpenStack Neutron (Networking) service.

This package contains the Neutron Dynamic Routing Python library.

%package -n python3-%{servicename}-tests
Summary: Neutron Dynamic Routing tests
%{?python_provide:%python_provide python3-%{servicename}-tests}

Requires: python3-%{servicename}
Requires: python3-neutron >= %{neutron_epoch}:%{major_version}
Requires: python3-mock >= 2.0
Requires: python3-oslotest >= 1.10.0
Requires: python3-oslo-concurrency >= 3.8.0
Requires: python3-stestr
Requires: python3-os-ken >= 0.3.1
Requires: python3-subunit >= 0.0.18
Requires: python3-testresources >= 0.2.4
Requires: python3-testtools >= 1.4.0
Requires: python3-testscenarios >= 0.4
Requires: python3-tempest >= 16.1.0
Requires: python3-webob >= 1.7.1

Requires: python3-requests-mock >= 1.1
Requires: python3-webtest >= 2.0

%description -n python3-%{servicename}-tests
This is a Dynamic Routing service plugin for Openstack Neutron (Networking) service.

This package contains Neutron Dynamic Routing test files.

%package common
Summary: Neutron Dynamic Routing common package
Requires: python3-%{servicename} = %{version}-%{release}
Requires: openstack-neutron-common

%description common
This is Dynamic Routing service plugin for OpenStack Neutron (Networking) service.

This package contains Dynamic Routing common files.

%package -n openstack-neutron-bgp-dragent
Summary: Neutron BGP Dynamic Routing agent
Requires: openstack-neutron-dynamic-routing-common = %{version}-%{release}
Requires: python3-os-ken >= 0.3.1

%description -n openstack-neutron-bgp-dragent
This package contains the Neutron BGP Dynamic Routing agent that will host
different BGP speaking drivers and makes the required BGP peering session/s for
Neutron.

%prep
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
%{gpgverify}  --keyring=%{SOURCE102} --signature=%{SOURCE101} --data=%{SOURCE0}
%endif
%autosetup -n %{servicename}-%{upstream_version} -S git

# Let's handle dependencies ourseleves
%py_req_cleanup

%build
%{py3_build}

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
%{py3_install}

# Remove unused files
rm -rf %{buildroot}%{python3_sitelib}/bin
rm -rf %{buildroot}%{python3_sitelib}/doc
rm -rf %{buildroot}%{python3_sitelib}/tools

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
# FIXME: we need to ignore unit test results since
# https://bugzilla.redhat.com/show_bug.cgi?id=1829932
stestr run || true

%post -n openstack-neutron-bgp-dragent
%systemd_post neutron-bgp-dragent.service

%preun -n openstack-neutron-bgp-dragent
%systemd_preun neutron-bgp-dragent.service

%postun -n openstack-neutron-bgp-dragent
%systemd_postun_with_restart neutron-bgp-dragent.service

%files -n python3-%{servicename}
%license LICENSE
%doc AUTHORS CONTRIBUTING.rst README.rst
%{python3_sitelib}/%{modulename}
%{python3_sitelib}/%{modulename}-*.egg-info
%exclude %{python3_sitelib}/%{modulename}/tests

%files -n python3-%{servicename}-tests
%{python3_sitelib}/%{modulename}/tests

%files common
%license LICENSE

%files -n openstack-neutron-bgp-dragent
%license LICENSE
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/bgp_dragent.ini
%{_sysconfdir}/neutron/conf.d/neutron-bgp-dragent
%{_bindir}/neutron-bgp-dragent
%{_unitdir}/neutron-bgp-dragent.service

%changelog
