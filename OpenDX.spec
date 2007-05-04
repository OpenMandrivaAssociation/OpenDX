%define samplesname 	dxsamples
%define sver	4.4.0
%define dxdir	%{_libdir}/dx

Name:		OpenDX
Summary:	IBM OpenDX (Data Explorer)

Version:	4.4.4
Release:	%mkrel 3

Source:		http://opendx.npaci.edu/source/dx-%{version}.tar.bz2
Source1:	http://opendx.npaci.edu/source/dxsamples-%{sver}.tar.bz2
Source2:	icons-dx.tar.bz2
Patch4:		dx-4.2.0-errno.patch
Patch5:		dx-4.2.0-xkb.patch
Patch6:		dx-4.3.2-types.patch
Patch7:		dx-4.4.4-String.patch
Patch8:		dx-4.4.4-returnval.patch
Patch9:		dx-4.4.4-implicit_decl.patch
Patch10:	dx-4.4.4-unitialized.patch
Patch11:	dx-4.4.4-undefined.patch
URL:		http://www.opendx.org/
Group:		Sciences/Other
License:	IBM Public License
BuildRequires:	autoconf2.5
BuildRequires:  bison
BuildRequires:  flex
BuildRequires:  freetype-devel
BuildRequires:	libMesaGLU-devel
BuildRequires:  libMagick-devel
BuildRequires:  lesstif-devel
BuildRequires:  libjbig-devel
BuildRequires:  netcdf-devel
%ifnarch ppc
BuildRequires:	HDF
%endif
BuildRoot:	%{_tmppath}/%{name}-%{version}-root

%description
OpenDX is a uniquely powerful, full-featured software package for the
visualization of scientific, engineering and analytical data: Its open
system design is built on a standard interface environments. And its
sophisticated data model provides users with great flexibility in
creating visualizations.

%package devel
Summary:	Development libraries for OpenDX
Group:		Development/C

%description devel
This package contains the header files and includes necessary to for developing
applications with OpenDX.

%prep
%setup -q -n dx-%{version} -a 1
%patch4 -p1 -b .errno
%patch5 -p1 -b .xkb
%patch6 -p1 -b .types
%patch7 -p1 -b .string
%patch8 -p1 -b .returnval
%patch9 -p1 -b .implicit
%patch10 -p1 -b .uninit
%patch11 -p1 -b .undefined
autoconf

%build
CFLAGS="%optflags -O1 -fno-fast-math -fno-exceptions" \
CXXFLAGS="%optflags -O1 -fno-fast-math -fno-exceptions -Wno-deprecated" \
%configure2_5x \
	--prefix=%{_libdir} \
	--with-x \
	--with-magick \
	--with-netcdf \
	--with-jbig \
	--without-javadx
make

(cd %{samplesname}-%{sver}
%configure --prefix=%{_libdir}
%make) 

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{_libdir} \
	$RPM_BUILD_ROOT%{_includedir}
%makeinstall prefix=$RPM_BUILD_ROOT%{_libdir} \
	libdir=$RPM_BUILD_ROOT%{dxdir} \
	mandir=$RPM_BUILD_ROOT%{_mandir}
ln -sf %{dxdir}/include/dxconfig.h $RPM_BUILD_ROOT%{_includedir}/dxconfig.h
ln -sf %{dxdir}/include/dxl.h $RPM_BUILD_ROOT%{_includedir}/dxl.h
ln -sf %{dxdir}/include/dx $RPM_BUILD_ROOT%{_includedir}/dx
ln -sf %{dxdir}/lib_linux/libDX.a $RPM_BUILD_ROOT%{_libdir}/libDX.a
ln -sf %{dxdir}/lib_linux/libDXcallm.a $RPM_BUILD_ROOT%{_libdir}/libDXcallm.a
ln -sf %{dxdir}/lib_linux/libDXL.a $RPM_BUILD_ROOT%{_libdir}/libDXL.a
ln -sf %{dxdir}/lib_linux/libDXlite.a $RPM_BUILD_ROOT%{_libdir}/libDXlite.a
rm -rf $RPM_BUILD_ROOT%{dxdir}/man
#
(cd $RPM_BUILD_ROOT/%{dxdir}/html
ln -sf allguide.htm index.htm
ln -sf allguide.htm index.html
)
#
(cd %{samplesname}-%{sver}
make install prefix=$RPM_BUILD_ROOT%{_libdir}
)

mkdir -p $RPM_BUILD_ROOT%{dxdir}/lib
install -m 644 ./lib/mdf2c.awk $RPM_BUILD_ROOT%{dxdir}/lib/

# fix dxexec path
mv $RPM_BUILD_ROOT%{_bindir}/dxexec $RPM_BUILD_ROOT%{dxdir}/bin_linux/dxexec
ln -s %{dxdir}/bin_linux/dxexec $RPM_BUILD_ROOT%{_bindir}/dxexec

# remove files not packaged
rm -rf $RPM_BUILD_ROOT%{_libdir}/bin/dx

# icons
mkdir -p $RPM_BUILD_ROOT%{_iconsdir} \
	 $RPM_BUILD_ROOT%{_menudir}
tar xjf %{SOURCE2} -C $RPM_BUILD_ROOT%{_iconsdir}

# menu
cat >$RPM_BUILD_ROOT%{_menudir}/OpenDX <<EOF
?package(OpenDX): command="%{_bindir}/dx" \
needs="X11" \
icon="dx.png" \
section="Applications/Sciences/Mathematics" \
title="OpenDX" \
%if %{mdkversion} >= 200610
xdg=true \
%endif
longtitle="Visualization Data Explorer"
EOF

# desktop menu
mkdir -p $RPM_BUILD_ROOT%{_datadir}/applications
cat > $RPM_BUILD_ROOT%{_datadir}/applications/mandriva-%{name}.desktop <<EOF
[Desktop Entry]
Name=OpenDX
Comment=Visualization Data Explorer
Exec=%{_bindir}/dx
Terminal=false
Type=Application
Icon=dx
Categories=X-MandrivaLinux-MoreApplications-Sciences-Mathematics;Science;Math;
StartupWMClass=startupWindow
EOF

# Clean installed tree
find $RPM_BUILD_ROOT/%_libdir -type f -or -type d | xargs chmod go-w
rm -f $RPM_BUILD_ROOT%{dxdir}/samples/outboard/Makefile_os2 \
	$RPM_BUILD_ROOT%{dxdir}/samples/user/Makefile_os2

rm -f $RPM_BUILD_ROOT/%_libdir/dx/samples/data/externalfilter_alphax
rm -f $RPM_BUILD_ROOT/%_libdir/dx/samples/data/externalfilter_hp700
rm -f $RPM_BUILD_ROOT/%_libdir/dx/samples/data/externalfilter_ibm6000
rm -f $RPM_BUILD_ROOT/%_libdir/dx/samples/data/externalfilter_sgi
rm -f $RPM_BUILD_ROOT/%_libdir/dx/samples/data/externalfilter_solaris

%clean
rm -rf $RPM_BUILD_ROOT

%post
%{update_menus}

%postun
%{clean_menus}

%files
%defattr(-,root,root)
%doc AUTHORS LICENSE README
%dir %{dxdir}
%{_bindir}/*
%{_mandir}/*/*
%{dxdir}/bin
%{dxdir}/bin_linux
%{dxdir}/doc
%{dxdir}/fonts
%{dxdir}/help
%{dxdir}/html
%{dxdir}/lib
%{dxdir}/ui
%{dxdir}/java
%{_iconsdir}/dx.*
%{_liconsdir}/dx.*
%{_miconsdir}/dx.*
%{_menudir}/OpenDX
%{_datadir}/applications/*.desktop

%files devel
%defattr(-,root,root)
%attr(644,root,root) %{_libdir}/*.a
%doc dxsamples-%{sver}/ChangeLog
%{_includedir}/*
%{dxdir}/include
%{dxdir}/samples
%{dxdir}/lib_linux
%{dxdir}/lib/mdf2c.awk


