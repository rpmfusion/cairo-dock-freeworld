%global	urlver		3.4
%global	mainver	3.4.0

%global	plugin_least_ver	3.4.0

Name:			cairo-dock-freeworld
Version:		3.4.1
Release:		8%{?dist}
Summary:		Light eye-candy fully themable animated dock

License:		GPLv3+
URL:			http://glx-dock.org/
#Source0:		http://launchpad.net/cairo-dock-core/%{urlver}/%{mainver}/+download/cairo-dock-%{mainver}.tar.gz
Source0:		https://github.com/Cairo-Dock/cairo-dock-core/archive/%{version}/cairo-dock-%{version}.tar.gz
Source1:		cairo-dock-freeworld-oldchangelog

BuildRequires:	cmake
BuildRequires:	gcc-c++
#BuildRequires:	desktop-file-utils
BuildRequires:	gettext
BuildRequires:	intltool

BuildRequires:	pkgconfig(cairo)
BuildRequires:	pkgconfig(dbus-1)
BuildRequires:	pkgconfig(dbus-glib-1)
BuildRequires:	pkgconfig(gl)
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(glu)
BuildRequires:	pkgconfig(gthread-2.0)
BuildRequires:	pkgconfig(gtk+-3.0)
BuildRequires:	pkgconfig(libcurl)
BuildRequires:	pkgconfig(librsvg-2.0)
BuildRequires:	pkgconfig(libxml-2.0)
BuildRequires:	pkgconfig(wayland-client)
BuildRequires:	pkgconfig(x11)
BuildRequires:	pkgconfig(xcomposite)
BuildRequires:	pkgconfig(xinerama)
BuildRequires:	pkgconfig(xrandr)
BuildRequires:	pkgconfig(xrender)
BuildRequires:	pkgconfig(xtst)

Requires:	cairo-dock%{?_isa} = %{version}
Requires:	%{name}-libs%{?_isa} = %{version}-%{release}

%description
This is a metapackage for installing all default packages
related to cairo-dock-freeworld.

%package	libs
Summary:	Library files for %{name}

%description	libs
This package contains library files for %{name}.

%prep
#%%setup -q -n cairo-dock-%%{version}
%setup -q -n cairo-dock-core-%{version}

## permission
# %%_fixperms cannot fix permissions completely here
for dir in */
do
	find $dir -type f | xargs chmod 0644
done
chmod 0644 [A-Z]*
chmod 0755 */

# cmake issue
sed -i.debuglevel \
	-e '\@add_definitions@s|-O3|-O2|' \
	CMakeLists.txt
sed -i.stat \
	-e 's|\${MSGFMT_EXECUTABLE}|\${MSGFMT_EXECUTABLE} --statistics|' \
	po/CMakeLists.txt

%build
rm -f CMakeCache.txt
%cmake -DCMAKE_SKIP_RPATH:BOOL=ON .
make -C src/gldit %{?_smp_mflags}

%install
rm -rf TMPINSTDIR
make  -C src/gldit\
	install \
	DESTDIR=$(pwd)/TMPINSTDIR
chmod 0755 TMPINSTDIR/%{_libdir}/lib*.so.*

mkdir -p $RPM_BUILD_ROOT/%{_libdir}/%{name}
cp -a \
	TMPINSTDIR/%{_libdir}/lib*.so.* \
	$RPM_BUILD_ROOT/%{_libdir}/%{name}/
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/ld.so.conf.d/
cat > $RPM_BUILD_ROOT/%{_sysconfdir}/ld.so.conf.d/%{name}-%{_arch}.conf <<EOF
%{_libdir}/%{name}
EOF

# Collect docment files
rm -rf documents licenses
mkdir documents licenses
install -cpm 644 \
	ChangeLog \
	data/ChangeLog*.txt \
	documents/

cat %{SOURCE1} | gzip > documents/rpm-oldchangelog.gz

install -cpm 644 \
	LGPL-2 \
	LICENSE \
	copyright \
	licenses/


%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

%files

%files	libs
%license	licenses/*
%doc	documents/*

%{_sysconfdir}/ld.so.conf.d/%{name}-%{_arch}.conf
%dir	%{_libdir}/%{name}
%{_libdir}/%{name}/libgldi.so.3*

%changelog
* Tue Feb 04 2020 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 3.4.1-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Fri Aug 09 2019 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 3.4.1-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Mon Mar 04 2019 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 3.4.1-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Thu Jul 26 2018 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 3.4.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Feb 28 2018 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 3.4.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Aug 31 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 3.4.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sat Mar 18 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 3.4.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Fri Mar  6 2015 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.4.1-1
- 3.4.1

* Wed Mar  4 2015 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.4.0-10
- Trim down old changelog
- Remove unneeded BR

* Fri Jan  2 2015 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.4.0-9
- Package libgldi.so only for -freeworld

* Tue Dec 30 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.4.0-8
- Make -kde, -xfce installed as default, per request from
  the upstream (no extra dependency will be added)

* Mon Dec 29 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.4.0-7
- Build unstable plug-ins (except for KDE experimental)
  (not installed by default option)

* Mon Dec 29 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.4.0-6
- Enable vala interface

* Sat Dec 20 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.4.0-5
- Make plug-ins depending on python(2), due to cairo-dock-launcher-API-daemon
  dependency (bug 3470)

* Fri Dec 19 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.4.0-4
- Add Dbus demos

* Fri Dec 19 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.4.0-3
- Build ruby

* Fri Dec 12 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.4.0-2
- Build Messaging-Menu, Status-Notifier

* Mon Dec  1 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.4.0-1
- 3.4.0

