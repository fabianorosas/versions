%define ibm_release .1

%define pkvm_release .pkvm3_1_1

Name:       wok
Version:    2.2.0
Release:    4%{?dist}%{?pkvm_release}
Summary:    Wok - Webserver Originated from Kimchi
BuildRoot:  %{_topdir}/BUILD/%{name}-%{version}-%{release}
BuildArch:  noarch
Group:      System Environment/Base
License:    LGPL/ASL2
Source0:    %{name}.tar.gz
Requires:   gettext
Requires:   python-cherrypy >= 3.2.0
Requires:   python-cheetah
Requires:   m2crypto
Requires:   PyPAM
Requires:   python-jsonschema >= 1.3.0
Requires:   python-lxml
Requires:   nginx
Requires:   python-ldap
Requires:   python-psutil >= 0.6.0
Requires:   fontawesome-fonts
Requires:   open-sans-fonts
Requires:   logrotate
Requires:	policycoreutils
Requires:	policycoreutils-python

Requires(post): policycoreutils
Requires(post): policycoreutils-python
Requires(post): selinux-policy-targeted
Requires(postun): policycoreutils
Requires(postun): policycoreutils-python
Requires(postun): selinux-policy-targeted

BuildRequires:	gettext-devel
BuildRequires:	libxslt
BuildRequires:	openssl
BuildRequires:	python-lxml
BuildRequires:	selinux-policy-devel
BuildRequires:	policycoreutils-devel

%if 0%{?fedora} >= 15 || 0%{?rhel} >= 7
%global with_systemd 1
%endif

%if 0%{?rhel} == 6
Requires:   python-ordereddict
Requires:   python-imaging
BuildRequires:    python-unittest2
%endif

%if 0%{?with_systemd}
Requires:   systemd
Requires:   firewalld
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%endif

%if 0%{?with_systemd}
BuildRequires: systemd-units
%endif

BuildRequires: autoconf
BuildRequires: automake

%description
Wok is Webserver Originated from Kimchi.


%prep
%setup -n %{name}


%build
./autogen.sh --system
make
cd src/selinux
make -f /usr/share/selinux/devel/Makefile


%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install

%if 0%{?rhel} == 6
# Install the upstart script
install -Dm 0755 contrib/wokd-upstart.conf.fedora %{buildroot}/etc/init/wokd.conf
%endif
%if 0%{?rhel} == 5
# Install the SysV init scripts
install -Dm 0755 contrib/wokd.sysvinit %{buildroot}%{_initrddir}/wokd
%endif

install -Dm 0640 src/firewalld.xml %{buildroot}%{_prefix}/lib/firewalld/services/wokd.xml

# Install script to help open port in firewalld
install -Dm 0744 src/wok-firewalld.sh %{buildroot}%{_datadir}/wok/utils/wok-firewalld.sh

# Install SELinux policy
install -Dm 0744 src/selinux/wokd.pp %{buildroot}%{_datadir}/wok/selinux/wokd.pp

%post
if [ $1 -eq 1 ] ; then
    /bin/systemctl enable wokd.service >/dev/null 2>&1 || :
    # Initial installation
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :

    # Add wokd as default service into public chain of firewalld
    %{_datadir}/wok/utils/wok-firewalld.sh public add wokd
fi

# Install SELinux policy
semodule -i %{_datadir}/wok/selinux/wokd.pp

%preun

if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /bin/systemctl --no-reload disable wokd.service > /dev/null 2>&1 || :
    /bin/systemctl stop wokd.service > /dev/null 2>&1 || :

    # Remove wokd service from public chain of firewalld
    %{_datadir}/wok/utils/wok-firewalld.sh public del wokd
    firewall-cmd --reload >/dev/null 2>&1 || :
fi

exit 0


%postun
if [ "$1" -ge 1 ] ; then
    /bin/systemctl try-restart wokd.service >/dev/null 2>&1 || :
fi
if [ $1 -eq 0 ]; then
    # Remove the SELinux policy, only when uninstall the package
    semodule -r wokd
fi
exit 0

%clean
rm -rf $RPM_BUILD_ROOT

%files
%attr(-,root,root)
%{_bindir}/wokd
%{python_sitelib}/wok/*.py*
%{python_sitelib}/wok/control/*.py*
%{python_sitelib}/wok/model/*.py*
%{python_sitelib}/wok/xmlutils/*.py*
%{python_sitelib}/wok/API.json
%{python_sitelib}/wok/plugins/*.py*
%{python_sitelib}/wok/
%{_prefix}/share/locale/*/LC_MESSAGES/wok.mo
%{_datadir}/wok/ui/
%{_datadir}/wok
%{_sysconfdir}/nginx/conf.d/wok.conf.in
%{_sysconfdir}/wok/wok.conf
%{_sysconfdir}/wok/
%{_sysconfdir}/logrotate.d/wokd
%{_mandir}/man8/wokd.8.gz

%if 0%{?with_systemd}
%{_sysconfdir}/nginx/conf.d/wok.conf
%{_sharedstatedir}/wok/
%{_localstatedir}/log/wok/*
%{_localstatedir}/log/wok/
%{_unitdir}/wokd.service
%{_prefix}/lib/firewalld/services/wokd.xml
%endif
%if 0%{?rhel} == 6
/etc/init/wokd.conf
%endif
%if 0%{?rhel} == 5
%{_initrddir}/wokd
%endif

%changelog
* Wed Sep 07 2016 user - 2.2.0-4.pkvm3_1_1
- bea70fc Merge remote-tracking branch upstream/master into powerkvm-v3.1.1
8e5a84d Change location of User Requests Log
d164293 Save log entry IDs for requests that generate tasks
2ae31d2 Log AsyncTask success or failure
d25d822 Update Request Logger to handle AsyncTask status
0767b4b Create log_request() method for code simplification
cdb3c4e Blink dialog session timeout
86514d0 Minor fixes in form fields
bc54058 Removing Kimchi Peers dropdown from Wok navbar
b1f0fef Issue #122 - Add unit test to stop AsyncTask.
9a00bff Issue #122 - Make AsyncTask stoppable.
240f449 Merge remote-tracking branch upstream/master into powerkvm-v3.1.1

* Thu Sep 01 2016 Mauro S. M. Rodrigues <maurosr@linux.vnet.ibm.com> - 2.2.0-3.pkvm3_1_1
- Build August, 31st, 2016

* Thu Aug  4 2016 Paulo Vital <pvital@linux.vnet.ibm.com> 2.3
- Add SELinux policy to allow http context

* Fri Jun 19 2015 Lucio Correia <luciojhc@linux.vnet.ibm.com> 2.0
- Rename to wokd
- Remove kimchi specifics

* Thu Feb 26 2015 Frédéric Bonnard <frediz@linux.vnet.ibm.com> 1.4.0
- Add man page for kimchid

* Tue Feb 11 2014 Crístian Viana <vianac@linux.vnet.ibm.com> 1.1.0
- Add help pages and XSLT dependency

* Tue Jul 16 2013 Adam Litke <agl@us.ibm.com> 0.1.0-1
- Adapted for autotools build

* Thu Apr 04 2013 Aline Manera <alinefm@br.ibm.com> 0.0-1
- First build
