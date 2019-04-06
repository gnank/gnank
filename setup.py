#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Gnank - cercador d'horaris de la FIB
# Copyright (C) 2006 - 2007  Albert Gasset Romo
#               2011 - 2019  Marc Cornellà
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os, site, sys
from cx_Freeze import setup, Executable

sys.path[0] = os.path.join(sys.path[0], "src")
import config

include_files = ['src/ajuda.txt', 'src/gnank.png', 'src/web.png']

# On MSYS2's MINGW64/32 enrironments, the DLLs we want are in PATH.
# Typically this means /mingw64/bin/libwhatever.dll.

required_dll_search_paths = os.getenv("PATH", os.defpath).split(os.pathsep)
required_dlls = [
	'libgtk-3-0.dll',
	'libgdk_pixbuf-2.0-0.dll',
	'libpango-1.0-0.dll',
	'libpangocairo-1.0-0.dll',
	'libpangoft2-1.0-0.dll',
	'libpangowin32-1.0-0.dll',
	'libatk-1.0-0.dll',
	'libepoxy-0.dll',
]

for dll in required_dlls:
	dll_path = None
	for p in required_dll_search_paths:
		p = os.path.join(p, dll)
		if os.path.isfile(p):
			dll_path = p
			break
	assert dll_path is not None, \
		"Unable to locate {} in {}".format(dll, p)
	include_files.append((dll_path, dll))


# Gtk libs are under the root of the MINGW64 directory, and
# they should go in lib/ or share/ directories.

gtkLibs = [
	'lib\\gdk-pixbuf-2.0',
	'lib\\girepository-1.0',
	'lib\\gtk-3.0',
	'share\\glib-2.0'
]

for lib in gtkLibs:
	include_files.append((os.path.join('C:\\msys64\\mingw64', lib), lib))

setup(
	name = "gnank",
	version = config.VERSIO,
	author = config.AUTOR,
	author_email = config.EMAIL_AUTOR,
	license = config.LLICENCIA,
	description = config.DESCRIPCIO,
	options = {
		"build_exe": {
			"packages": ['gi', 'cairo'],
			"include_files": include_files
		},
	},
	executables = [Executable(
		script="src/main.py",
		targetName="gnank.exe",
		base="Win32GUI",
		icon="paquets/win32/gnank.ico"
	)]
)
