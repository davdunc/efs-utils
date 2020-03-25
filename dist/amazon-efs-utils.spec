#
# Copyright 2017-2018 Amazon.com, Inc. and its affiliates. All Rights Reserved.
#
# Licensed under the MIT License. See the LICENSE accompanying this file
# for the specific language governing permissions and limitations under
# the License.

# Added to fix the short name for the base directory in later versions
%global short_name efs-utils

%bcond_with test
%if 0%{?amzn1}
%global python_requires system-python
%global pytest pytest
%elseif 0%{?fedora} >= 30 || 0%{?rhel} >= 8
%global python_requires python3
%global pytest pytest-3
%global long_name %{name}-v%{version}
%else
%global python_requires python2
%global pytest pytest-2
%endif

%if 0%{?amzn1} || 0%{?rhel} == 6
%global with_systemd 0
%else
%global with_systemd 1
%endif

Name      : amazon-%{short_name}
Version   : 1.24
Release   : 1%{?dist}
Summary   : This package provides utilities for simplifying the use of EFS file systems
License   : MIT
URL       : https://aws.amazon.com/efs

%if 0%{?fedora} || 0%{?rhel}
## The Packager:, and Vendor: tags MUST NOT be used
## The Group: tag SHOULD NOT be used
## The Source: tags document where to find the upstream sources for the package
Source0    : https://github.com/aws/efs-utils/archive/v%{version}/%{short_name}-v%{version}.tar.gz
%else
Group     : Amazon/Tools
# Source    : %{name}.tar.gz
Packager  : Amazon.com, Inc. <http://aws.amazon.com>
Vendor    : Amazon.com
%endif
BuildArch : noarch

Requires  : nfs-utils
Requires  : stunnel >= 4.56
Requires  : %{python_requires}
%if %{with test}
BuildRequires    : python3-pytest
%endif
%if %{with_systemd}
BuildRequires    : systemd
BuildRequires    : systemd-rpm-macros
%{?systemd_requires}
%else
Requires(post)   : /sbin/chkconfig
Requires(preun)  : /sbin/service /sbin/chkconfig
Requires(postun) : /sbin/service
%endif


%description
This package provides utilities for simplifying the use of EFS file systems

%prep -n %{short_name}-%{version}
%setup -q -n %{short_name}-%{version}
%build -n %{short_name}-%{version}
%if 0%{?rhel} > 7 || 0%{?fedora}
# Replace the first line in .py to "#!/usr/bin/env python3" no matter what it was before
sed -i -e '1 s/^.*$/\#!\/usr\/bin\/env python3/' src/watchdog/__init__.py
sed -i -e '1 s/^.*$/\#!\/usr\/bin\/env python3/' src/mount_efs/__init__.py
%endif


%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_sysconfdir}/amazon/efs

%if %{with_systemd}
mkdir -p %{buildroot}%{_unitdir}
install -p -m 644 dist/amazon-efs-mount-watchdog.service %{buildroot}%{_unitdir}
%else
mkdir -p %{buildroot}%{_sysconfdir}/init
install -p -m 644 %{_builddir}/%{short_name}/dist/amazon-efs-mount-watchdog.conf %{buildroot}%{_sysconfdir}/init
%endif

mkdir -p %{buildroot}/sbin
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_localstatedir}/log/amazon/efs
mkdir -p  %{buildroot}%{_mandir}/man8

install -p -m 644 dist/efs-utils.conf %{buildroot}%{_sysconfdir}/amazon/efs
install -p -m 444 dist/efs-utils.crt %{buildroot}%{_sysconfdir}/amazon/efs
install -p -m 755 src/mount_efs/__init__.py %{buildroot}/sbin/mount.efs
install -p -m 755 src/watchdog/__init__.py %{buildroot}%{_bindir}/amazon-efs-mount-watchdog
install -p -m 644 man/mount.efs.8 %{buildroot}%{_mandir}/man8

%files
%defattr(-,root,root,-)
%if %{with_systemd}
%{_unitdir}/amazon-efs-mount-watchdog.service
%else
%config(noreplace) %{_sysconfdir}/init/amazon-efs-mount-watchdog.conf
%endif
%{_sysconfdir}/amazon/efs/efs-utils.crt
/sbin/mount.efs
%{_bindir}/amazon-efs-mount-watchdog
/var/log/amazon
%{_mandir}/man8/mount.efs.8.gz

%config(noreplace) %{_sysconfdir}/amazon/efs/efs-utils.conf

%if %{with_systemd}
%post
%systemd_post amazon-efs-mount-watchdog.service

%preun
%systemd_preun amazon-efs-mount-watchdog.service

%postun
%systemd_postun_with_restart amazon-efs-mount-watchdog.service

%else

%preun
if [ $1 -eq 0 ]; then
   /sbin/stop amazon-efs-mount-watchdog &> /dev/null || true
fi

%postun
if [ $1 -eq 1 ]; then
    /sbin/restart amazon-efs-mount-watchdog &> /dev/null || true
fi

%endif
%if 0%{?rhel} || 0%{?fedora}
# The %clean section SHOULD NOT be used.
%else
%clean
%endif
%if %{with test}
%check
%{pytest} 

flake8
%endif
%changelog
* Wed Mar 25 2020 David Duncan <davdunc@amazon.com> - 1.24-1
- Update to latest release

