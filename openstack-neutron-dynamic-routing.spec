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
URL: http://launchpad.net/neutron/
Source0: http://tarballs.openstack.org/%{servicename}/%{servicename}-%{upstream_version}.tar.gz
Source2: neutron-bgp-dragent.service

BuildArch: noarch

BuildRequires: openstack-macros
BuildRequires: python2-devel
BuildRequires: python-neutron >= %{neutron_epoch}:%{major_version}
BuildConflicts: python-neutron >= %{neutron_epoch}:%{next_version}
BuildRequires: python-neutron-lib
BuildRequires: python-pbr >= 2.0.0
BuildRequires: python-setuptools
BuildRequires: git
BuildRequires: systemd
BuildRequires: systemd-units

Requires: openstack-%{servicename}-common = %{version}-%{release}

Requires(pre): shadow-utils
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description
This is a Dynamic Routing addons for OpenStack Neutron (Networking) service.


%package -n python-%{servicename}
Summary: Neutron Dynamic Routing python library

Requires: python-neutron >= %{neutron_epoch}:%{major_version}
Conflicts: python-neutron >= %{neutron_epoch}:%{next_version}
# alembic is >= 0.8.10 in upstream g-r.txt but we ship 0.8.7 only
Requires: python-alembic >= 0.8.7
Requires: python-netaddr >= 0.7.16
Requires: python-oslo-config >= 2:4.0.0
Requires: python-oslo-db >= 4.24.0
Requires: python-oslo-log >= 3.22.0
Requires: python-oslo-messaging >= 5.24.2
Requires: python-oslo-serialization >= 1.10.0
Requires: python-oslo-service >= 1.10.0
Requires: python-oslo-utils >= 3.20.0
Requires: python-pbr >= 2.0.0
Requires: python-six >= 1.9.0
Requires: python-sqlalchemy >= 1.0.10

%description -n python-%{servicename}
This is Dynamic Routing service plugin for OpenStack Neutron (Networking) service.

This package contains the Neutron Dynamic Routing Python library.


%package common
Summary: Neutron Dynamic Routing common package
Requires: python-%{servicename} = %{version}-%{release}

%description common
This is Dynamic Routing service plugin for OpenStack Neutron (Networking) service.

This package contains Dynamic Routing common files.

%prep
%autosetup -n %{servicename}-%{upstream_version} -S git

# Let's handle dependencies ourseleves
%py_req_cleanup


%package -n openstack-neutron-bgp-dragent
Summary: BGP Dragent

%description -n openstack-neutron-bgp-dragent
This is a BGP Dynamic Routing Agent



%build
%py2_build

# Generate sample config files
GEN_CMD=oslo-config-generator

if ! type "$GEN_CMD" > /dev/null; then
    echo "ERROR: $GEN_CMD not installed on the system."
    exit 1
fi

for file in `ls etc/oslo-config-generator/*`; do
    $GEN_CMD --config-file=$file
done

find etc -name *.sample | while read filename
do
    filedir=$(dirname $filename)
    file=$(basename $filename .sample)
    mv ${filename} ${filedir}/${file}
done


%install
%py2_install

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


%post
%systemd_post neutron-bgp-dragent.service

%preun
%systemd_preun neutron-bgp-dragent.service

%postun
%systemd_postun_with_restart neutron-bgp-dragent.service


%files -n python-%{servicename}
%license LICENSE
%{python2_sitelib}/%{modulename}
%{python2_sitelib}/%{modulename}-*.egg-info
%exclude %{python2_sitelib}/%{modulename}/tests


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

