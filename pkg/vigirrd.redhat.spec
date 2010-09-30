%define module  vigirrd
%define name    vigilo-%{module}
%define version 2.0.0
%define release 1%{?svn}%{?dist}

%define pyver 26
%define pybasever 2.6
%define __python /usr/bin/python%{pybasever}
%define __os_install_post %{__python26_os_install_post}
%{!?python26_sitelib: %define python26_sitelib %(python26 -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:       %{name}
Summary:    Web interface to display RRD files in vigilo
Version:    %{version}
Release:    %{release}
Source0:    %{module}-%{version}.tar.gz
URL:        http://www.projet-vigilo.org
Group:      System/Servers
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-build
License:    GPLv2
Buildarch:  noarch

BuildRequires:   python26-distribute

Requires:   python26-distribute
Requires:   vigilo-turbogears
Requires:   rrdtool-python26 >= 1.3
Requires:   python26-simplejson
Requires:   dejavu-lgc-fonts
Requires:   mod_wsgi-python26

# For the api doc generation
#BuildRequires: epydoc python26-rrdtool

Obsoletes:  vigilo-rrdgraph <= 2.0.1
Provides:   vigilo-rrdgraph = %{version}-%{release}


%description
Web interface to display RRD files
Web interface based on mod_python to display the RRD graphs.
This application is part of the Vigilo Project <http://vigilo-project.org>

%package    vigiconf
Summary:    Vigiconf setup for VigiRRD
Requires:   vigilo-vigirrd
Group:      System/Servers

%description vigiconf
This package creates the links to use Vigiconf's generated configuration files
with VigiRRD.

%prep
%setup -q -n %{module}-%{version}

%build

%install
rm -rf $RPM_BUILD_ROOT
make install \
    DESTDIR=$RPM_BUILD_ROOT \
    SYSCONFDIR=%{_sysconfdir} \
    PYTHON=%{__python}

make apidoc || :

# Vigiconf
ln -s %{_sysconfdir}/vigilo/vigiconf/prod/vigirrd.conf.py \
    $RPM_BUILD_ROOT%{_sysconfdir}/vigilo/%{module}/graphs.conf.py

#%find_lang %{name}

%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(644,root,root,755)
%doc COPYING 
%dir %{_sysconfdir}/vigilo
%dir %{_sysconfdir}/vigilo/%{module}
%config(noreplace) %{_sysconfdir}/vigilo/%{module}/*.conf
%config(noreplace) %{_sysconfdir}/vigilo/%{module}/*.py
%config(noreplace) %{_sysconfdir}/vigilo/%{module}/*.wsgi
%config(noreplace) %attr(640,root,apache) %{_sysconfdir}/vigilo/%{module}/*.ini
%ghost %{_sysconfdir}/vigilo/%{module}/*.pyo
%ghost %{_sysconfdir}/vigilo/%{module}/*.pyc
%exclude %{_sysconfdir}/vigilo/%{module}/graphs.conf.py
%{_sysconfdir}/vigilo/%{module}/graphs.py.dist
%config(noreplace) %{_sysconfdir}/httpd/conf.d/*
%config(noreplace) %{_sysconfdir}/cron.d/*
%dir %{_localstatedir}/log/vigilo/
%attr(750,apache,apache) %{_localstatedir}/log/vigilo/%{module}
%attr(750,apache,apache) %{_localstatedir}/cache/vigilo/sessions
%{python26_sitelib}/*

%files vigiconf
%defattr(644,root,root,755)
%{_sysconfdir}/vigilo/%{module}/graphs.conf.py

