%define samplesname 	dxsamples
%define sver	4.4.0
%define dxdir	%{_libdir}/dx

Summary:	IBM OpenDX (Data Explorer)
Name:		OpenDX
Version:	4.4.4
Release:	22
Group:		Sciences/Other
License:	IBM Public License
Url:		http://www.opendx.org/
Source0:	http://opendx.npaci.edu/source/dx-%{version}.tar.bz2
Source1:	http://opendx.npaci.edu/source/dxsamples-%{sver}.tar.bz2
Source2:	dx.png
Patch4:		dx-4.4.4-errno.patch
Patch5:		dx-4.2.0-xkb.patch
Patch6:		dx-4.3.2-types.patch
Patch7:		dx-4.4.4-String.patch
Patch8:		dx-4.4.4-returnval.patch
Patch9:		dx-4.4.4-implicit_decl.patch
Patch10:	dx-4.4.4-unitialized.patch
Patch11:	dx-4.4.4-undefined.patch
Patch12:	dx-imagemagick-6.3.8.5.diff
Patch13:	dx-open.patch
Patch14:	dx-gcc43.patch
Patch15:	dx-4.4.4-autoconf.patch
Patch16:	dx-4.4.4-fix-str-fmt.patch
Patch17:	dx-4.4.4-linkage.patch
Patch18:	opendx-4.4.4-concurrent-make-fix.patch
Patch19:	dx-4.4.4-newer-imagemagick.patch
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	imagemagick
BuildRequires:	libtool
BuildRequires:	kernel-source
BuildRequires:	freetype-devel
BuildRequires:	jbig-devel
BuildRequires:	lesstif-devel
BuildRequires:	magic-devel
BuildRequires:	pkgconfig(glu)
BuildRequires:	pkgconfig(netcdf)
%ifnarch ppc
BuildRequires:	hdf-devel
%endif

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
%apply_patches
rm -f configure; autoreconf -fi

#fix netcdf hdf5 linking
sed -i 's/-lnetcdf/-lnetcdf -lhdf5_hl -lhdf5 -lz/g' ./configure

%build
CFLAGS="%optflags -O1 -fno-fast-math -fno-exceptions -I/usr/src/linux/include -I%{_includedir}/ImageMagick" \
CXXFLAGS="%optflags -O1 -fno-fast-math -fno-exceptions -Wno-deprecated -I/usr/src/linux/include -I%{_includedir}/ImageMagick" \

%configure2_5x \
	--prefix=%{_libdir} \
	--with-x \
	--with-magick \
	--with-netcdf \
	--with-jbig \
	--without-javadx
make 

(cd %{samplesname}-%{sver}
%configure2_5x --prefix=%{_libdir}
%make) 

%install
mkdir -p %{buildroot}%{_libdir} \
	%{buildroot}%{_includedir}
%makeinstall prefix=%{buildroot}%{_libdir} \
	libdir=%{buildroot}%{dxdir} \
	mandir=%{buildroot}%{_mandir} \
	LIBTOOL=%_bindir/libtool
ln -sf %{dxdir}/include/dxconfig.h %{buildroot}%{_includedir}/dxconfig.h
ln -sf %{dxdir}/include/dxl.h %{buildroot}%{_includedir}/dxl.h
ln -sf %{dxdir}/include/dx %{buildroot}%{_includedir}/dx
ln -sf %{dxdir}/lib_linux/libDX.a %{buildroot}%{_libdir}/libDX.a
ln -sf %{dxdir}/lib_linux/libDXcallm.a %{buildroot}%{_libdir}/libDXcallm.a
ln -sf %{dxdir}/lib_linux/libDXL.a %{buildroot}%{_libdir}/libDXL.a
ln -sf %{dxdir}/lib_linux/libDXlite.a %{buildroot}%{_libdir}/libDXlite.a
rm -rf %{buildroot}%{dxdir}/man
#
(cd %{buildroot}/%{dxdir}/html
ln -sf allguide.htm index.htm
ln -sf allguide.htm index.html
)
#
(cd %{samplesname}-%{sver}
make install prefix=%{buildroot}%{_libdir}
)

mkdir -p %{buildroot}%{dxdir}/lib
install -m 644 ./lib/mdf2c.awk %{buildroot}%{dxdir}/lib/

# fix dxexec path
mv %{buildroot}%{_bindir}/dxexec %{buildroot}%{dxdir}/bin_linux/dxexec
ln -s %{dxdir}/bin_linux/dxexec %{buildroot}%{_bindir}/dxexec

# remove files not packaged
rm -rf %{buildroot}%{_libdir}/bin/dx

# icons
mkdir -p %{buildroot}%{_iconsdir}/hicolor/{48x48,32x32,16x16}/apps
install -m 644 %{SOURCE2} %{buildroot}%{_iconsdir}/hicolor/48x48/apps/dx.png
convert -scale 32 %{SOURCE2} %{buildroot}%{_iconsdir}/hicolor/32x32/apps/dx.png
convert -scale 16 %{SOURCE2} %{buildroot}%{_iconsdir}/hicolor/16x16/apps/dx.png

# desktop menu
mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/mandriva-%{name}.desktop <<EOF
[Desktop Entry]
Name=OpenDX
Comment=Visualization Data Explorer
Exec=%{_bindir}/dx
Terminal=false
Type=Application
Icon=dx
Categories=Science;Math;
StartupWMClass=startupWindow
EOF

# Clean installed tree
find %{buildroot}/%_libdir -type f -or -type d | xargs chmod go-w
rm -f %{buildroot}%{dxdir}/samples/outboard/Makefile_os2 \
	%{buildroot}%{dxdir}/samples/user/Makefile_os2

rm -f %{buildroot}/%_libdir/dx/samples/data/externalfilter_alphax
rm -f %{buildroot}/%_libdir/dx/samples/data/externalfilter_hp700
rm -f %{buildroot}/%_libdir/dx/samples/data/externalfilter_ibm6000
rm -f %{buildroot}/%_libdir/dx/samples/data/externalfilter_sgi
rm -f %{buildroot}/%_libdir/dx/samples/data/externalfilter_solaris

%files
%doc AUTHORS LICENSE README
%dir %{dxdir}
%{_bindir}/*
%{_mandir}/man1/*
%{dxdir}/bin
%{dxdir}/bin_linux
%{dxdir}/doc
%{dxdir}/fonts
%{dxdir}/help
%{dxdir}/html
%{dxdir}/lib
%{dxdir}/ui
%{dxdir}/java
%{_iconsdir}/hicolor/48x48/apps/dx.png
%{_iconsdir}/hicolor/32x32/apps/dx.png
%{_iconsdir}/hicolor/16x16/apps/dx.png
%{_datadir}/applications/*.desktop
%exclude %{dxdir}/lib/mdf2c.awk

%files devel
%attr(644,root,root) %{_libdir}/*.a
%doc dxsamples-%{sver}/ChangeLog
%{_includedir}/*
%{dxdir}/include
%{dxdir}/samples
%{dxdir}/lib_linux
%{dxdir}/lib/mdf2c.awk

