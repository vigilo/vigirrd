%define module  @SHORT_NAME@

Name:       vigilo-%{module}
Summary:    @SUMMARY@
Version:    @VERSION@
Release:    @RELEASE@%{?dist}
Source0:    %{name}-%{version}.tar.gz
URL:        @URL@
Group:      System/Servers
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-build
License:    GPLv2
Buildarch:  noarch

BuildRequires:   python-distribute
BuildRequires:   python-babel

Requires:   python-distribute
Requires:   vigilo-turbogears
Requires:   rrdtool-python >= 1.3
Requires:   python-simplejson
Requires:   mod_wsgi

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

make apidoc || :

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
%config(noreplace) /etc/httpd/conf.d/%{module}.conf
%config(noreplace) /etc/cron.d/*
%dir %{_localstatedir}/log/vigilo/
%attr(750,apache,apache) %{_localstatedir}/log/vigilo/%{module}
%config(noreplace) /etc/logrotate.d/%{module}
%attr(750,apache,apache) %{_localstatedir}/cache/vigilo/sessions
%attr(750,apache,apache) %dir %{_localstatedir}/cache/vigilo/vigirrd
%attr(750,apache,apache) %dir %{_localstatedir}/cache/vigilo/vigirrd/img
%attr(750,vigiconf,apache) %dir %{_localstatedir}/cache/vigilo/vigirrd/db
%{python_sitelib}/*

