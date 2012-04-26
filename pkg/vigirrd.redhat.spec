%define module  @SHORT_NAME@

%define pyver 26
%define pybasever 2.6
%define __python /usr/bin/python%{pybasever}
%define __os_install_post %{__python26_os_install_post}
%{!?python26_sitelib: %define python26_sitelib %(python26 -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:       vigilo-%{module}
Summary:    @SUMMARY@
Version:    @VERSION@
Release:    @RELEASE@%{?dist}
Source0:    %{name}-%{version}.tar.gz
URL:        @URL@
Group:      Applications/System
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-build
License:    GPLv2
Buildarch:  noarch

BuildRequires:   python26-distribute
BuildRequires:   python26-babel

Requires:   python26-distribute
Requires:   vigilo-turbogears
Requires:   rrdtool-python26 >= 1.3
Requires:   python26-simplejson
Requires:   dejavu-lgc-fonts
Requires:   python26-mod_wsgi
Requires:   python26-pytz

# For the api doc generation
#BuildRequires: epydoc python26-rrdtool

# VigiConf
Requires:   vigilo-vigiconf-local
Obsoletes:  %{name}-confmgr < 1.13-2
Provides:   %{name}-confmgr = %{version}-%{release}
Obsoletes:  %{name}-vigiconf < 2.0.0-2
Provides:   %{name}-vigiconf = %{version}-%{release}

# Pour l'utilisateur vigilo-metro
Requires(pre):   vigilo-connector-metro

Obsoletes:  vigilo-rrdgraph <= 2.0.1
Provides:   vigilo-rrdgraph = %{version}-%{release}


%description
@DESCRIPTION@
This application is part of the Vigilo Project <http://vigilo-project.org>

%prep
%setup -q

%build

%install
rm -rf $RPM_BUILD_ROOT
make install_pkg \
    DESTDIR=$RPM_BUILD_ROOT \
    SYSCONFDIR=%{_sysconfdir} \
    LOCALSTATEDIR=%{_localstatedir} \
    PYTHON=%{__python}

#%find_lang %{name}


%pre
usermod -a -G vigilo-metro apache

%post
/sbin/service httpd condrestart > /dev/null 2>&1 || :

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc COPYING.txt README.txt
%attr(755,root,root) %{_bindir}/%{module}-*
%dir %{_sysconfdir}/vigilo
%dir %{_sysconfdir}/vigilo/%{module}
%config(noreplace) %{_sysconfdir}/vigilo/%{module}/*.conf
%config(noreplace) %{_sysconfdir}/vigilo/%{module}/*.py
%config(noreplace) %{_sysconfdir}/vigilo/%{module}/*.wsgi
%config(noreplace) %attr(640,root,apache) %{_sysconfdir}/vigilo/%{module}/*.ini
%ghost %{_sysconfdir}/vigilo/%{module}/*.pyo
%ghost %{_sysconfdir}/vigilo/%{module}/*.pyc
%config(noreplace) /etc/httpd/conf.d/%{name}.conf
%config(noreplace) /etc/cron.d/*
%dir %{_localstatedir}/log/vigilo/
%attr(750,apache,apache) %{_localstatedir}/log/vigilo/%{module}
%config(noreplace) /etc/logrotate.d/%{name}
%attr(750,apache,apache) %{_localstatedir}/cache/vigilo/sessions
%attr(750,apache,apache) %dir %{_localstatedir}/cache/vigilo/vigirrd
%attr(750,apache,apache) %dir %{_localstatedir}/cache/vigilo/vigirrd/img
%attr(750,vigiconf,apache) %dir %{_localstatedir}/cache/vigilo/vigirrd/db
%{python26_sitelib}/*
