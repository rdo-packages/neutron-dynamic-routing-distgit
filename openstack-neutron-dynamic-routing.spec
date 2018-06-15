%global service neutron-dynamic-routing

%global with_doc 1

%global common_desc \
Dynamic routing services for OpenStack Neutron.

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

%define major_neutron_version %(echo %{version} | awk 'BEGIN { FS=\".\"}; {print $1}')
%define next_neutron_version %(echo $((%{major_neutron_version} + 1)))

Name:             openstack-%{service}
Version:          XXX
Release:          XXX%{?dist}
Epoch:            1
Summary:          OpenStack Neutron Dynamic Routing
License:          ASL 2.0
URL:              https://github.com/openstack/%{service}
Source0:          http://tarballs.openstack.org/%{service}/%{service}-%{upstream_version}.tar.gz
Source10:         openstack-neutron-bgp-dragent.service

Provides:         openstack-neutron-bgp-dragent = %{epoch}:%{version}-%{release}

BuildArch:        noarch
BuildRequires:    gawk
BuildRequires:    openstack-macros
BuildRequires:    python2-devel
BuildRequires:    python-neutron >= 1:%{major_neutron_version}
BuildConflicts:   python-neutron >= 1:%{next_neutron_version}
BuildRequires:    python2-pbr
BuildRequires:    python2-setuptools
BuildRequires:    systemd
BuildRequires:    git

Requires:         python-%{service} = %{epoch}:%{version}-%{release}
Requires:         openstack-neutron >= 1:%{major_neutron_version}
Conflicts:        openstack-neutron >= 1:%{next_neutron_version}

%description
%{common_desc}

%package -n python-%{service}
Summary:          Neutron Dynamic Routing Python libraries

Requires:         python-neutron >= 1:%{major_neutron_version}
Conflicts:        python-neutron >= 1:%{next_neutron_version}
Requires:         python2-eventlet >= 0.18.2
Requires:         python-httplib2 >= 0.9.1
Requires:         python2-netaddr >= 0.7.18
Requires:         python2-sqlalchemy >= 1.0.10
Requires:         python2-alembic >= 0.8.10
Requires:         python2-six >= 1.10.0
Requires:         python2-neutron-lib >= 1.13.0
Requires:         python2-oslo-config >= 2:5.1.0
Requires:         python2-oslo-db >= 4.27.0
Requires:         python2-oslo-messaging >= 5.29.0
Requires:         python2-oslo-serialization >= 2.18.0
Requires:         python2-oslo-service >= 1.24.0
Requires:         python2-oslo-utils >= 3.33.0

%description -n python-%{service}
%{common_desc}

This package contains the Neutron Dynamic Routing Python library.

%package openstack-neutron-bgp-dragent
Summary:          Neutron BGP Dynamic Routing agent
Requires:         openstack-neutron-common = %{epoch}:%{version}-%{release}

Requires:         python-%{service} = %{epoch}:%{version}-%{release}
Requires:         python2-ryu >= 4.14

%description openstack-neutron-bgp-dragent
Neutron provides an API to dynamically request and configure virtual
networks.

This package contains the Neutron BGP Dynamic Routing agent that will host
different BGP speaking drivers and makes the required BGP peering session/s for
Neutron.

%prep
%autosetup -n %{service}-%{upstream_version} -S git

# Let's handle dependencies ourseleves
rm -f requirements.txt

%build
export SKIP_PIP_INSTALL=1
%{__python2} setup.py build

# Generate configuration files
PYTHONPATH=. tools/generate_config_file_samples.sh
find etc -name *.sample | while read filename
do
    filedir=$(dirname $filename)
    file=$(basename $filename .sample)
    mv ${filename} ${filedir}/${file}
done

%install
%{__python2} setup.py install -O1 --skip-build --root %{buildroot}

# Remove unused files
rm -rf %{buildroot}%{python2_sitelib}/bin
rm -rf %{buildroot}%{python2_sitelib}/doc
rm -rf %{buildroot}%{python2_sitelib}/tools

# Install systemd units
install -p -D -m 644 %{SOURCE10} %{buildroot}%{_unitdir}/openstack-neutron-bgp-dragent.service

# Create configuration directory
mkdir -p %{buildroot}/%{_sysconfdir}/neutron/conf.d/neutron-bgp-dragent

%post openstack-neutron-bgp-dragent
%systemd_post openstack-neutron-bgp-dragent.service

%preun openstack-neutron-bgp-dragent
%systemd_preun openstack-neutron-bgp-dragent.service

%postun openstack-neutron-bgp-dragent
%systemd_postun_with_restart openstack-neutron-bgp-dragent.service

%files openstack-neutron-bgp-dragent
%license LICENSE
%{_bindir}/neutron-bgp-dragent
%{_unitdir}/openstack-neutron-bgp-dragent.service
%dir %{_sysconfdir}/neutron/conf.d/neutron-bgp-dragent

%files -n python-%{service}
%{python2_sitelib}/neutron_dynamic_routing
%exclude %{python2_sitelib}/neutron_dynamic_routing/tests
