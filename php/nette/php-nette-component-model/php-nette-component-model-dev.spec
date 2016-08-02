# remirepo/fedora spec file for php-nette-component-model
#
# Copyright (c) 2015-2016 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/4.0/
#
# Please, preserve the changelog entries
#
%global gh_commit    07bce436051fd92d084642ce7a47f00045e0d1e5
#global gh_date      20150728
%global gh_short     %(c=%{gh_commit}; echo ${c:0:7})
%global gh_owner     nette
%global gh_project   component-model
%global ns_vendor    Nette
%global ns_project   ComponentModel
%global php_home     %{_datadir}/php
%global with_tests   0%{!?_without_tests:1}

Name:           php-%{gh_owner}-%{gh_project}
Version:        2.2.4
%global specrel 2
Release:        %{?gh_date:0.%{specrel}.%{?prever}%{!?prever:%{gh_date}git%{gh_short}}}%{!?gh_date:%{specrel}}%{?dist}
Summary:        Nette Component Model

Group:          Development/Libraries
License:        BSD or GPLv2 or GPLv3
URL:            https://github.com/%{gh_owner}/%{gh_project}
Source0:        %{name}-%{version}-%{gh_short}.tgz
# pull a git snapshot to get test sutie
Source1:        makesrc.sh

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  php-composer(theseer/autoload)
%if %{with_tests}
BuildRequires:  php(language) >= 5.3.1
BuildRequires:  php-pcre
BuildRequires:  php-reflection
BuildRequires:  php-composer(%{gh_owner}/utils) >= 2.3.5
# From composer.json, "require-dev": {
#        "nette/tester": "~1.4"
BuildRequires:  php-composer(%{gh_owner}/tester) >= 1.4
%endif

# from composer.json, "require": {
#        "php": ">=5.3.1"
#        "nette/utils": "^2.3.5"
Requires:       php(language) >= 5.3.1
Requires:       php-composer(%{gh_owner}/utils) >= 2.3.5
Requires:       php-composer(%{gh_owner}/utils) <  3
# from phpcompatinfo report for version 2.2.4
Requires:       php-pcre
Requires:       php-spl

Provides:       php-composer(%{gh_owner}/%{gh_project}) = %{version}


%description
Components are the foundation of reusable code. They make your work easier
and allow you to profit from community work. Components are wonderful.
Nette Framework introduces several classes and interfaces for all these
types of components.

Object inheritance allows us to have a hierarchic structure of classes like
in real world. We can create new classes by extending. These extended classes
are descendants of the original class and inherit its parameters and methods.
Extended class can add its own parameters and methods to the inherited ones.

To use this library, you just have to add, in your project:
  require_once '%{php_home}/%{ns_vendor}/%{ns_project}/autoload.php';


%prep
%setup -q -n %{gh_project}-%{gh_commit}


%build
: Generate a classmap autoloader
phpab --output src/%{ns_project}/autoload.php src

cat << 'EOF' | tee -a src/%{ns_project}/autoload.php
// Dependencies
require_once '%{php_home}/%{ns_vendor}/Utils/autoload.php';
EOF


%install
rm -rf       %{buildroot}
mkdir -p     %{buildroot}%{php_home}/%{ns_vendor}
cp -pr src/* %{buildroot}%{php_home}/%{ns_vendor}/


%check
%if %{with_tests}
: Generate configuration
cat /etc/php.ini /etc/php.d/*ini >php.ini
export LANG=fr_FR.utf8

: Generate autoloader
mkdir vendor
cat << 'EOF' | tee vendor/autoload.php
<?php
require_once '%{php_home}/Tester/autoload.php';
require_once '%{buildroot}%{php_home}/%{ns_vendor}/%{ns_project}/autoload.php';
EOF

: Run test suite in sources tree
nette-tester --colors 0 -p php -c ./php.ini tests -s
%else
: Test suite disabled
%endif


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%{!?_licensedir:%global license %%doc}
%license license.md
%doc readme.md
%doc composer.json
%{php_home}/%{ns_vendor}/%{ns_project}


%changelog
* Tue Nov  3 2015 Remi Collet <remi@fedoraproject.org> - 2.2.4-2
- fix package description and summary

* Tue Oct 20 2015 Remi Collet <remi@fedoraproject.org> - 2.2.4-1
- initial package