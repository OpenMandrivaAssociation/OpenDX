%define samplesname 	dxsamples
%define sver	4.4.0
%define dxdir	%{_libdir}/dx

Summary:	IBM OpenDX (Data Explorer)
Name:		OpenDX
Version:	4.4.4
Release:	18
Source:		http://opendx.npaci.edu/source/dx-%{version}.tar.bz2
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
URL:		http://www.opendx.org/
Group:		Sciences/Other
License:	IBM Public License
BuildRequires:	autoconf libtool
BuildRequires:  bison
BuildRequires:  flex
BuildRequires:  freetype-devel
BuildRequires:	mesa-common-devel
BuildRequires:  magic-devel
BuildRequires:  lesstif-devel
BuildRequires:  jbig-devel
BuildRequires:  netcdf-devel
BuildRequires:	imagemagick
BuildRequires:	kernel-source
%ifnarch ppc
BuildRequires:	HDF
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
%patch4 -p1 -b .errno
%patch5 -p1 -b .xkb
%patch6 -p1 -b .types
%patch7 -p1 -b .string
%patch8 -p1 -b .returnval
%patch9 -p1 -b .implicit
%patch10 -p1 -b .uninit
%patch11 -p1 -b .undefined
%patch12 -p0
%patch13 -p1 -b .open
%patch14 -p1 -b .gcc43
%patch15 -p1 -b .autoconf
%patch16 -p0 -b .str
%patch17 -p0 -b .link
%patch18 -p1 -b .tmp
%patch19 -p0 -b .imagemagick

rm -f configure; autoreconf -fi

%build

CFLAGS="%optflags -O1 -fno-fast-math -fno-exceptions -I/usr/src/linux/include -I%{_includedir}/ImageMagick" \
CXXFLAGS="%optflags -O1 -fno-fast-math -fno-exceptions -Wno-deprecated -I/usr/src/linux/include -I%{_includedir}/ImageMagick" \

#fix netcdf hdf5 linking
sed -i 's/-lnetcdf/-lnetcdf -lhdf5_hl -lhdf5 -lz/g' ./configure

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
rm -rf %{buildroot}
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

%clean
rm -rf %{buildroot}

%if %mdkversion < 200900
%post
%{update_menus}
%{update_icon_cache hicolor}
%endif

%if %mdkversion < 200900
%postun
%{clean_menus}
%{clean_icon_cache hicolor}
%endif

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
%{_iconsdir}/hicolor/48x48/apps/dx.png
%{_iconsdir}/hicolor/32x32/apps/dx.png
%{_iconsdir}/hicolor/16x16/apps/dx.png
%{_datadir}/applications/*.desktop
%exclude %{dxdir}/lib/mdf2c.awk

%files devel
%defattr(-,root,root)
%attr(644,root,root) %{_libdir}/*.a
%doc dxsamples-%{sver}/ChangeLog
%{_includedir}/*
%{dxdir}/include
%{dxdir}/samples
%{dxdir}/lib_linux
%{dxdir}/lib/mdf2c.awk


%changelog
* Sat May 07 2011 Oden Eriksson <oeriksson@mandriva.com> 4.4.4-15mdv2011.0
+ Revision: 671966
- mass rebuild

* Sat Jul 10 2010 Funda Wang <fwang@mandriva.org> 4.4.4-14mdv2011.0
+ Revision: 549994
- rebuild for new imagemagick

* Tue Jan 19 2010 Emmanuel Andry <eandry@mandriva.org> 4.4.4-13mdv2010.1
+ Revision: 493463
- fix netcdf hdf5 linking
- use configure2_5x for samples too

* Sat Jan 16 2010 Emmanuel Andry <eandry@mandriva.org> 4.4.4-12mdv2010.1
+ Revision: 492283
- rebuild for netcdf

* Thu Jan 14 2010 Funda Wang <fwang@mandriva.org> 4.4.4-11mdv2010.1
+ Revision: 491509
- fix build with newer imagemagick

  + Oden Eriksson <oeriksson@mandriva.com>
    - rebuilt against libjpeg v8

* Sat Aug 15 2009 Oden Eriksson <oeriksson@mandriva.com> 4.4.4-10mdv2010.0
+ Revision: 416646
- rebuilt against libjpeg v7

* Sun Aug 09 2009 Oden Eriksson <oeriksson@mandriva.com> 4.4.4-9mdv2010.0
+ Revision: 413006
- rebuild

* Sat Jan 31 2009 Funda Wang <fwang@mandriva.org> 4.4.4-8mdv2009.1
+ Revision: 335832
- add gentoo patch to fix make
- fix build
- BR our own libtool
- adopt fedora patch to build with autoconf
- rediff patch4

* Thu Aug 07 2008 Thierry Vignaud <tv@mandriva.org> 4.4.4-8mdv2009.0
+ Revision: 265265
- rebuild early 2009.0 package (before pixel changes)

  + Pixel <pixel@mandriva.com>
    - rpm filetriggers deprecates update_menus/update_scrollkeeper/update_mime_database/update_icon_cache/update_desktop_database/post_install_gconf_schemas

* Wed May 21 2008 Oden Eriksson <oeriksson@mandriva.com> 4.4.4-7mdv2009.0
+ Revision: 209744
- sync with fedora

* Mon Feb 11 2008 Oden Eriksson <oeriksson@mandriva.com> 4.4.4-6mdv2008.1
+ Revision: 165173
- rebuilt against latest imagemagick libs

  + Thierry Vignaud <tv@mandriva.org>
    - fix mesaglu-devel BR

* Tue Jan 08 2008 Oden Eriksson <oeriksson@mandriva.com> 4.4.4-5mdv2008.1
+ Revision: 146561
- fix build
- rebuilt against new imagemagick libs (6.3.7)

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

  + Adam Williamson <awilliamson@mandriva.org>
    - buildrequires kernel-source
    - rebuild against new lesstif
    - switch to fd.o icons
    - drop old menu and X-Mandriva category

* Fri May 04 2007 Herton Ronaldo Krzesinski <herton@mandriva.com.br> 4.4.4-3mdv2008.0
+ Revision: 22589
- Rebuild against new libjasper.
- Small identation fixes.


* Sun Feb 18 2007 Giuseppe GhibÃ² <ghibo@mandriva.com> 4.4.4-2mdv2007.0
+ Revision: 122367
- xdg menu.
- bunzip2 patches.
- Merged Patch8,9,10,11 from opensuse.

* Sat Feb 17 2007 Giuseppe GhibÃ² <ghibo@mandriva.com> 4.4.4-2mdv2007.1
+ Revision: 122165
- Rebuilt against ImageMagick 6.3.2.

* Sun Jan 14 2007 Giuseppe GhibÃ² <ghibo@mandriva.com> 4.4.4-1mdv2007.1
+ Revision: 108778
- Import OpenDX

* Mon Dec 04 2006 Giuseppe Ghibò <ghibo@mandriva.com> 4.4.4-1mdv2007.0
- Release 4.4.4.

* Fri May 05 2006 Giuseppe Ghibò <ghibo@mandriva.com> 4.4.0-1mdk
- Release 4.4.
- Removed Patch7, merged upstream.

* Fri Mar 17 2006 Giuseppe Ghibò <ghibo@mandriva.com> 4.3.2-14mdk
- Rebuilt against new ImageMagick libs.

* Sat Jan 07 2006 Mandriva Linux Team <http://www.mandrivaexpert.com/> 4.3.2-13mdk
- Rebuild

* Mon Dec 19 2005 Giuseppe Ghibo <ghibo@mandriva.com> 4.3.2-12mdk
- Added Patch7 for overflow (from opensuse).

* Thu Aug 25 2005 Oden Eriksson <oeriksson@mandriva.com> 4.3.2-11mdk
- rebuilt against new Magick libs

* Tue Jul 12 2005 Giuseppe Ghibò <ghibo@mandriva.com> 4.3.2-10mdk
- Rebuilt with gcc 4.0.1.
- Added Patch6 to avoid problems with graphwiz types.h.

* Wed Mar 23 2005 Giuseppe Ghibò <ghibo@mandrakesoft.com> 4.3.2-9mdk
- Rebuilt against latest ImageMagick.

* Mon Feb 07 2005 Giuseppe Ghibò <ghibo@mandrakesoft.com> 4.3.2-8mdk
- Rebuilt against latest ImageMagick.

* Thu Jan 20 2005 Frederic Lepied <flepied@mandrakesoft.com> 4.3.2-7mdk
- rebuild to have the correct dependencies

* Sat Aug 21 2004 Laurent MONTEL <lmontel@mandrakesoft.com> 4.3.2-6mdk
- Rebuild with new menu

* Fri Jul 30 2004 Giuseppe Ghibò <ghibo@mandrakesoft.com> 4.3.2-5mdk
- Merged Gwenole patch: fix deps (from AMD64 4.3.2-1.1mdk version).

* Tue Jul 20 2004 Giuseppe Ghibò <ghibo@mandrakesoft.com> 4.3.2-4mdk
- Rebuilt under new gcc 3.4.1.

* Fri Jul 02 2004 Michael Scherer <misc@mandrake.org> 4.3.2-3mdk 
- rebuild for new ImageMagick

* Sun Jun 13 2004 Giuseppe Ghibò <ghibo@mandrakesoft.com> 4.3.2-2mdk
- Rebuilt.

