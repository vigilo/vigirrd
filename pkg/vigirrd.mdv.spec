%define module  vigirrd
%define name    vigilo-%{module}
%define version 2.0.0
%define release 1%{?svn}

Name:       %{name}
Summary:    Web interface to display RRD files in vigilo
Version:    %{version}
Release:    %{release}
Source0:    %{module}.tar.bz2
URL:        http://www.projet-vigilo.org
Group:      System/Servers
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-build
License:    GPLv2

BuildRequires:   python-setuptools

Requires:   python >= 2.5
Requires:   python-setuptools
Requires:   vigilo-turbogears
Requires:   python-rrdtool >= 1.3
Requires:   python-simplejson
Requires:   fonts-ttf-dejavu
Requires:   apache-mod_wsgi

# For the api doc generation
#BuildRequires: epydoc python-rrdtool

Buildarch:  noarch

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
Obsoletes:  %{name}-confmgr < 1.13-2
Provides:   %{name}-confmgr = %{version}-%{release}

%description vigiconf
This package creates the links to use Vigiconf's generated configuration files
with VigiRRD.

%prep
%setup -q -n %{module}

%build

%install
rm -rf $RPM_BUILD_ROOT
make install \
    DESTDIR=$RPM_BUILD_ROOT \
	SYSCONFDIR=%{_sysconfdir} \
    PYTHON=%{_bindir}/python

make apidoc || :

# Vigiconf
ln -s %{_sysconfdir}/vigilo/vigiconf/prod/rrdgraph.conf.py \
    $RPM_BUILD_ROOT%{_sysconfdir}/vigilo/%{module}/graphs.conf.py

%find_lang %{name}

%clean
rm -rf $RPM_BUILD_ROOT


%files -f %{name}.lang
%defattr(-,root,root)
%doc COPYING 
%dir %{_sysconfdir}/vigilo
%dir %{_sysconfdir}/vigilo/%{module}
%config(noreplace) %{_sysconfdir}/vigilo/%{module}/*.conf
%config(noreplace) %{_sysconfdir}/vigilo/%{module}/*.py
%config(noreplace) %{_sysconfdir}/vigilo/%{module}/*.ini
%config(noreplace) %{_sysconfdir}/vigilo/%{module}/*.wsgi
%exclude %{_sysconfdir}/vigilo/%{module}/graphs.conf.py
%{_sysconfdir}/vigilo/%{module}/graphs.py.dist
%config(noreplace) %{_sysconfdir}/httpd/conf/webapps.d/*
%config(noreplace) %{_sysconfdir}/cron.d/*
%dir %{_localstatedir}/log/vigilo/
%attr(750,apache,apache) %{_localstatedir}/log/vigilo/%{module}
%{python_sitelib}/*

%files vigiconf
%defattr(-,root,root)
%{_sysconfdir}/vigilo/%{module}/graphs.conf.py

