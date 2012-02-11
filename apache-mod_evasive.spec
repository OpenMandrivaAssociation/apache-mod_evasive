#Module-Specific definitions
%define mod_name mod_evasive
%define mod_conf A11_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	Evasive Maneuvers Module for the apache web server
Name:		apache-%{mod_name}
Version:	1.10.1
Release:	%mkrel 16
Group:		System/Servers
License:	Apache License
URL:		http://www.zdziarski.com/projects/mod_evasive/
Source0: 	http://www.zdziarski.com/projects/mod_evasive/%{mod_name}_%{version}.tar.gz
Source1:	%{mod_conf}
Patch0:		mod_evasive-small_fix.diff
Requires:	mailx
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	file
Epoch:		1
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
A module for apache giving Apache the ability to fend off
request-based DoS attacks conserving your system resources and
bandwidth. This new tool maintains an internal table of IP
addresses and URLs and will deny repeated requests for the same
URL from the same IP address, blacklisting the address for
10-seconds per extraneous request. Obviously, this module will
not fend off attacks consuming all available bandwidth or more
resources than are available to send 403's, but is very successful
in typical flood attacks or cgi flood attacks. 

%prep

%setup -q -n mod_evasive
%patch0 -p0

rm -rf .libs
rm -f %{mod_name}.c
mv %{mod_name}20.c %{mod_name}.c

cp %{SOURCE1} %{mod_conf}

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build
%{_sbindir}/apxs -c %{mod_name}.c

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

install -m0755 .libs/*.so %{buildroot}%{_libdir}/apache-extramodules/
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

install -d %{buildroot}%{_var}/www/html/addon-modules
ln -s ../../../..%{_docdir}/%{name}-%{version} %{buildroot}%{_var}/www/html/addon-modules/%{name}-%{version}

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc README
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
%{_var}/www/html/addon-modules/*


