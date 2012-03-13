%define module  @SHORT_NAME@

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

BuildRequires:   python-setuptools
BuildRequires:   python-babel

Requires:   python >= 2.5
Requires:   python-setuptools
Requires:   vigilo-turbogears
Requires:   python-rrdtool >= 1.3
Requires:   python-simplejson
Requires:   fonts-ttf-dejavu
Requires:   apache-mod_wsgi
Requires:   python-pytz

# VigiConf
Requires:   vigilo-vigiconf-local
Obsoletes:  %{name}-confmgr < 1.13-2
Provides:   %{name}-confmgr = %{version}-%{release}
Obsoletes:  %{name}-vigiconf < 2.0.0-2
Provides:   %{name}-vigiconf = %{version}-%{release}

######### Dependance from python dependance tree ########
Requires:   vigilo-common
Requires:   vigilo-models
Requires:   vigilo-themes-default
Requires:   vigilo-turbogears
Requires:   python-addons
Requires:   python-babel
Requires:   python-beaker
Requires:   python-bytecodeassembler
# version >= 4.7.2 pour résolution BUG #313
Requires:   python-configobj >= 4.7.2
Requires:   python-decorator
Requires:   python-decoratortools
Requires:   python-EggTranslations
Requires:   python-extremes
Requires:   python-formencode
Requires:   python-genshi
Requires:   python-mako
Requires:   python-nose
Requires:   python-paste
Requires:   python-pastedeploy
Requires:   python-pastescript
Requires:   python-peak-rules
Requires:   python-prioritized_methods
Requires:   python-psycopg2
Requires:   python-pygments
Requires:   python-pylons
Requires:   python-dateutil
Requires:   python-repoze.tm2
Requires:   python-repoze.what
Requires:   python-repoze.what.plugins.sql
Requires:   python-repoze.what-pylons
Requires:   python-repoze.what-quickstart
Requires:   python-repoze.who
Requires:   python-repoze.who-friendlyform
Requires:   python-repoze.who.plugins.sa
Requires:   python-repoze.who-testutil
Requires:   python-routes
Requires:   python-rum
Requires:   python-RumAlchemy
Requires:   python-setuptools
Requires:   python-simplejson
Requires:   python-sqlalchemy
Requires:   python-sqlalchemy-migrate
Requires:   python-symboltype
Requires:   python-tempita
Requires:   python-tg.devtools
Requires:   python-TgRum
Requires:   python-toscawidgets
Requires:   python-transaction
Requires:   python-turbogears2
Requires:   python-turbojson
Requires:   python-tw.dojo
Requires:   python-tw.forms
Requires:   python-tw.rum
Requires:   python-weberror
Requires:   python-webflash
Requires:   python-webhelpers
Requires:   python-webob
Requires:   python-webtest
Requires:   python-zope-interface
Requires:   python-zope.sqlalchemy

# For the api doc generation
#BuildRequires: epydoc python-rrdtool

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

%find_lang %{name}


%pre
usermod -a -G vigilo-metro apache

%post
/sbin/service httpd condrestart > /dev/null 2>&1 || :

%clean
rm -rf $RPM_BUILD_ROOT

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc COPYING.txt README.txt
%attr(755,root,root) %{_bindir}/%{module}-*
%dir %{_sysconfdir}/vigilo
%dir %{_sysconfdir}/vigilo/%{module}
%config(noreplace) %{_sysconfdir}/vigilo/%{module}/*.conf
%config(noreplace) %{_sysconfdir}/vigilo/%{module}/*.py
%config(noreplace) %{_sysconfdir}/vigilo/%{module}/*.wsgi
%config(noreplace) %attr(640,root,apache) %{_sysconfdir}/vigilo/%{module}/*.ini
%config(noreplace) /etc/httpd/conf/webapps.d/%{name}.conf
%config(noreplace) /etc/cron.d/*
%dir %{_localstatedir}/log/vigilo/
%attr(750,apache,apache) %{_localstatedir}/log/vigilo/%{module}
%config(noreplace) /etc/logrotate.d/%{name}
%attr(750,apache,apache) %{_localstatedir}/cache/vigilo/sessions
%attr(750,apache,apache) %dir %{_localstatedir}/cache/vigilo/vigirrd
%attr(750,apache,apache) %dir %{_localstatedir}/cache/vigilo/vigirrd/img
%attr(750,vigiconf,apache) %dir %{_localstatedir}/cache/vigilo/vigirrd/db
%{python_sitelib}/*
