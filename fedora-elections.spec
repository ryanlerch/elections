%{!?pyver: %define pyver %(%{__python} -c "import sys ; print sys.version[:3]")}

%define modname fedora_elections
%define eggname fedora_elections

Name:           fedora-elections
Version:        0.1
Release:        1%{?dist}
Summary:        Fedora elections application

Group:          Development/Languages
License:        GPLv2+
URL:            https://github.com/fedora-infra/elections
Source0:        %{name}/%{name}-%{version}.tar.gz
# Source0:        https://fedorahosted.org/releases/f/a/%{name}/%{name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  libxslt
BuildRequires:  python
BuildRequires:  python-babel
BuildRequires:  python-backports-ssl_match_hostname
BuildRequires:  python-bunch
BuildRequires:  python-chardet
BuildRequires:  python-fedora
BuildRequires:  python-fedora-flask
BuildRequires:  python-flask
BuildRequires:  python-flask-sqlalchemy
BuildRequires:  python-flask-wtf
BuildRequires:  python-jinja2
BuildRequires:  python-kitchen
BuildRequires:  python-lxml
BuildRequires:  python-openid
BuildRequires:  python-ordereddict
BuildRequires:  python-requests
BuildRequires:  python-setuptools
BuildRequires:  python-simplejson
BuildRequires:  python-six
BuildRequires:  python-sqlalchemy0.7
BuildRequires:  python-urllib3
BuildRequires:  python-wtforms

Requires:       libxslt
Requires:       python
Requires:       python-babel
Requires:       python-backports-ssl_match_hostname
Requires:       python-bunch
Requires:       python-chardet
Requires:       python-fedora
Requires:       python-fedora-flask
Requires:       python-flask
Requires:       python-flask-sqlalchemy
Requires:       python-flask-wtf
Requires:       python-jinja2
Requires:       python-kitchen
Requires:       python-lxml
Requires:       python-openid
Requires:       python-ordereddict
Requires:       python-requests
Requires:       python-setuptools
Requires:       python-simplejson
Requires:       python-six
Requires:       python-sqlalchemy0.7
Requires:       python-urllib3
Requires:       python-wtforms


%description
fedora-elections is the Fedora Elections application.

%prep
%setup -q
./configure.py


%build
# Remove CFLAGS=... for noarch packages (unneeded)
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

%{__mkdir_p} %{buildroot}%{_sysconfdir}/%{name}
%{__install} -m 444 %{name}.cfg %{buildroot}%{_sysconfdir}/%{name}/%{name}.cfg

%{__mkdir_p} %{buildroot}%{_sysconfdir}/httpd/conf.d
%{__install} -m 444 httpd-fedora-elections.conf \
    %{buildroot}%{_sysconfdir}/httpd/conf.d/httpd-fedora-elections.conf

%{__mkdir_p} %{buildroot}%{_datadir}/%{name}
%{__install} -m 544 createdb %{buildroot}%{_datadir}/%{name}/createdb
%{__install} -m 544 createdb.py %{buildroot}%{_datadir}/%{name}/createdb.py
%{__install} -m 444 %{name}.wsgi %{buildroot}%{_datadir}/%{name}/%{name}.wsgi

%{__mkdir_p} %{buildroot}%{_datadir}/%{name}/static
%{__install} -m 444 fedora_elections/static/* %{buildroot}%{_datadir}/%{name}/static

%{__mkdir_p} %{buildroot}%{_datadir}/%{name}/images
%{__install} -m 444 fedora_elections/images/* %{buildroot}%{_datadir}/%{name}/images

%{__mkdir_p} %{buildroot}%{_sharedstatedir}/%{name}

%{__mkdir_p} %{buildroot}%{python_sitelib}/%{modname}/templates
%{__mkdir_p} %{buildroot}%{python_sitelib}/%{modname}/templates/admin
%{__mkdir_p} %{buildroot}%{python_sitelib}/%{modname}/templates/auth
%{__mkdir_p} %{buildroot}%{python_sitelib}/%{modname}/templates/election
%{__mkdir_p} %{buildroot}%{python_sitelib}/%{modname}/templates/list
%{__install} -m 444 fedora_elections/templates/*.html \
    %{buildroot}%{python_sitelib}/%{modname}/templates
%{__install} -m 444 fedora_elections/templates/admin/* \
    %{buildroot}%{python_sitelib}/%{modname}/templates/admin
%{__install} -m 444 fedora_elections/templates/auth/* \
    %{buildroot}%{python_sitelib}/%{modname}/templates/auth
%{__install} -m 444 fedora_elections/templates/election/* \
    %{buildroot}%{python_sitelib}/%{modname}/templates/election
%{__install} -m 444 fedora_elections/templates/list/* \
    %{buildroot}%{python_sitelib}/%{modname}/templates/list


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc
%dir %{_sysconfdir}/%{name}
%dir %{_sharedstatedir}/%{name}/
%{_datadir}/%{name}/
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.cfg
%config(noreplace) %{_sysconfdir}/httpd/conf.d/httpd-%{name}.conf
%{python_sitelib}/%{modname}/
%{python_sitelib}/%{eggname}-%{version}-py%{pyver}.egg-info/


%post
cd %{_sharedstatedir}/%{name}
if [[ ! -f database.sqlite ]]
then
    #
    # The database does not exist create one.
    #
    echo "  Creating a database."
    %{_datadir}/%{name}/createdb
fi


%postun
cd %{_sharedstatedir}/%{name}
if [[ -f database.sqlite ]]
then
    #
    # Remove the database.
    #
    echo "  Removing the database."
    /bin/rm  database.sqlite
fi

cd ${_sharedstatedir}
if [[ -d %{_sharedstatedir}/%{name} ]]
then
    /bin/rmdir  %{_sharedstatedir}/%{name}
fi


%changelog
* Sat May 04 2013 Frank Chiulli <fchiulli@fedoraproject.org> - 0.1
- Creation
