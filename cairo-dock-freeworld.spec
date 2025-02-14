%global	urlver	3.5
%global	mainver	3.5.99

%global	plugin_least_ver	3.5.99

%global	use_git	1
%global	gitdate	20250214
%global	githash	ddcff9ea6cfee0556909f1a48a968c5c649e68ce
%global	shorthash	%(c=%{githash} ; echo ${c:0:7})

%global	tarballver	%{mainver}%{?use_git:-%{gitdate}git%{shorthash}}

%global	baserelease	1
%global	alphatag		.rc2

%undefine _ld_strict_symbol_defs
%undefine __brp_mangle_shebangs

##########################################
%global		flagrel	%{nil}
%global		use_gcc_strict_sanitize	0

%if	0%{?use_gcc_strict_sanitize} >= 1
%global		flagrel	%{flagrel}.san
%endif
##########################################

Name:			cairo-dock-freeworld
Version:		%{mainver}%{?use_git:^%{gitdate}git%{shorthash}}
Release:		%{baserelease}%{?alphatag}%{?dist}%{flagrel}
Summary:		Light eye-candy fully themable animated dock

License:		GPLv3+
URL:			http://glx-dock.org/
%if 0%{?use_git} >= 1
Source0:		https://github.com/Cairo-Dock/cairo-dock-core/archive/%{githash}/cairo-dock-%{mainver}-%{gitdate}git%{shorthash}.tar.gz
%else
Source0:		https://github.com/Cairo-Dock/cairo-dock-core/archive/%{version}/cairo-dock-%{mainver}.tar.gz
%endif
Source1:		cairo-dock-freeworld-oldchangelog

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  extra-cmake-modules
BuildRequires:  systemd-rpm-macros
%if 0%{?use_gcc_strict_sanitize}
BuildRequires:  libasan
BuildRequires:  libubsan
%endif

#BuildRequires:	desktop-file-utils
BuildRequires:	gettext
BuildRequires:	intltool

BuildRequires:	pkgconfig(cairo)
BuildRequires:	pkgconfig(dbus-1)
BuildRequires:	pkgconfig(dbus-glib-1)
#BuildRequires:	pkgconfig(egl)
BuildRequires:	pkgconfig(gl)
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(glu)
BuildRequires:	pkgconfig(gthread-2.0)
BuildRequires:	pkgconfig(gtk-layer-shell-0)
BuildRequires:	pkgconfig(gtk+-3.0)
BuildRequires:	pkgconfig(libcurl)
BuildRequires:	pkgconfig(librsvg-2.0)
BuildRequires:	pkgconfig(libxml-2.0)
BuildRequires:	pkgconfig(nlohmann_json)
BuildRequires:	pkgconfig(systemd)
BuildRequires:	pkgconfig(wayland-egl)
BuildRequires:	pkgconfig(wayland-client)
BuildRequires:	pkgconfig(x11)
BuildRequires:	pkgconfig(xcomposite)
BuildRequires:	pkgconfig(xinerama)
BuildRequires:	pkgconfig(xrandr)
BuildRequires:	pkgconfig(xrender)
BuildRequires:	pkgconfig(xtst)

Requires:	cairo-dock%{?_isa} >= %{version}
Requires:	%{name}-libs%{?_isa} = %{version}-%{release}

%description
This is a metapackage for installing all default packages
related to cairo-dock-freeworld.

%package	libs
Summary:	Library files for %{name}

%description	libs
This package contains library files for %{name}.


%prep
%if 0%{?use_git} >= 1
%autosetup -n cairo-dock-core-%{githash} -p1
%else
%autosetup -n cairo-dock-core-%{mainver} -p1
%endif

## permission
# %%_fixperms cannot fix permissions completely here
for dir in */
do
	find $dir -type f | xargs -r chmod 0644
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

# Modify version forcely
sed -i CMakeLists.txt -e '\@set (VERSION @s|VERSION.*|VERSION "%{mainver}")|'

%build
%set_build_flags

%if 0%{?use_gcc_strict_sanitize}
export CC="${CC} -fsanitize=address -fsanitize=undefined"
export CXX="${CXX} -fsanitize=address -fsanitize=undefined"
export LDFLAGS="${LDFLAGS} -pthread"

# Currently -fPIE binary cannot work with ASAN on kernel 4.12
# https://github.com/google/sanitizers/issues/837
export CFLAGS="$(echo $CFLAGS     | sed -e 's|-specs=[^ \t][^ \t]*hardened[^ \t][^ \t]*||g')"
export CXXFLAGS="$(echo $CXXFLAGS | sed -e 's|-specs=[^ \t][^ \t]*hardened[^ \t][^ \t]*||g')"
export LDFLAGS="$(echo $LDFLAGS   | sed -e 's|-specs=[^ \t][^ \t]*hardened[^ \t][^ \t]*||g')"
%endif

rm -f CMakeCache.txt
%cmake \
	-B . \
	-DCMAKE_SKIP_RPATH:BOOL=ON \
	-Denable-egl-support:BOOL=ON \
	%{nil}
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


%ldconfig_scriptlets libs

%files

%files	libs
%license	licenses/*
%doc	documents/*

%{_sysconfdir}/ld.so.conf.d/%{name}-%{_arch}.conf
%dir	%{_libdir}/%{name}
%{_libdir}/%{name}/libgldi.so.3*

%changelog
* Fri Feb 14 2025 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.5.99^20250214gitddcff9e-1.rc2
- Update to the latest git (20250214gitddcff9e)

* Thu Feb 13 2025 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.5.99^20250211git443d8da-1.rc1
- Update to the latest git (20250211git443d8da)

* Thu Jan 30 2025 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.5.99^20250120gitd2fd789-1.rc1
- Update to the latest git (20250120gitd2fd789)

* Sun Jan 19 2025 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.5.99^20250118gitb0f5d5c-1.beta6
- Update to the latest git (20250118gitb0f5d5c)

* Sun Dec 29 2024 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.5.99^20241218gitf852640-1.beta6
- Update to the latest git (20241218gitf852640)

* Mon Dec 16 2024 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.5.99^20241216git4f36d13-1.beta6
- Update to the latest git (20241216git4f36d13)

* Sun Dec 08 2024 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.5.99^20241207gitea4bd97-1.beta5
- Update to the latest git (20241207gitea4bd97)

* Tue Nov 19 2024 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.5.99^20241118git575a251-1
- Update to the latest git (20241118git575a251)

* Thu Oct 24 2024 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.5.99^20241024git9f9421e-1
- Update to the latest git (20241024git9f9421e)

* Sun Oct 20 2024 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.5.99^20241016gitea5d37e-1
- Update to the latest git (20241016gitea5d37e)

* Mon Oct 14 2024 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.5.99^20241013git0324720-1
- Update to the latest git (20241013git0324720)

* Sun Oct 06 2024 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.5.99^20241007.1git2149e52-1
- Update to the latest git (20241007git2149e52)

* Thu Sep 26 2024 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.5.99^20240926git7b3ac7f-1
- Update to the latest git (20240926git7b3ac7f)

* Wed Sep 18 2024 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.5.99^20240915git1458bc8-1
- Update to the latest git (20240915git1458bc8)

* Thu Aug 22 2024 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.5.99^20240822gitb196136-1
- Update to the latest git (20240822gitb196136)

* Wed Aug 07 2024 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.5.99^20240805git23c0be5-1
- Update to the latest git (20240805git23c0be5)

* Thu Aug 01 2024 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 3.5.99^20240505git13fb151-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_41_Mass_Rebuild

* Sun May 05 2024 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.5.99^20240505git13fb151-1
- Update to the latest git (20240505git13fb151)
- Enable Wayfire IPC support

* Sat May 04 2024 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.5.99^20240501git1f31686-1
- Update to latest git (20240501git1f31686)

* Mon Feb 26 2024 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.5.0-1
- Update to 3.5.0

* Sat Feb 03 2024 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 3.4.1-15.D20210327git6c569e6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Wed Aug 02 2023 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.4.1-14.D20210327git6c569e6
- Pass -r option to xargs because new rpm creates empty directory

* Wed Aug 02 2023 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 3.4.1-13.D20210327git6c569e6.3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_39_Mass_Rebuild

* Sat Aug 06 2022 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 3.4.1-13.D20210327git6c569e6.2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_37_Mass_Rebuild and ffmpeg
  5.1

* Wed Feb 09 2022 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 3.4.1-13.D20210327git6c569e6.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Mon Sep 20 2021 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.4.1-13.D20210327git6c569e6
- wayland-manager: allocate new wl_output information by checking id
  (Fix segfault on KDE Plasma wayland session: redhat bug 2000812)
- Explicitly disable EGL support for now

* Mon Aug 02 2021 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 3.4.1-12.D20210327git6c569e6.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Wed Mar 31 2021 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.4.1-12.D20210327git6c569e6
- Update to the latest git

* Wed Feb 03 2021 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 3.4.1-11.20201103git0836f5d.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Sun Jan  3 2021 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.4.1-11.20201103git0836f5d
- Update to the latest git

* Mon Aug 17 2020 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 3.4.1-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Fri Aug  7 2020 Mamoru TASAKA <mtasaka@fedoraproject.org> - 3.4.1-9
- Minor fix for recent cmake invocation change

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

