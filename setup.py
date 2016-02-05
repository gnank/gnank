#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Gnank - cercador d'horaris de la FIB
# Copyright (C) 2006 - 2007  Albert Gasset Romo
#               2011 - 2016  Marc Cornellà
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

import sys
from os.path import join
sys.path[0] = join(sys.path[0], "src")

import config
from distutils.core import setup


data_files = []
excluded_dlls = []

if sys.platform == "win32":
    import py2exe

    data_files = [
        "src/gnank.png",
        "src/web.png",
        "src/ajuda.txt"
    ]

    # Exclude these DLLs unless we're on Windows 7
    # This wasn't tested on Windows 8/8.1
    from platform import release
    if int(release()) > 7:
        excluded_dlls = [
            "api-ms-win-core-errorhandling-l1-1-1.dll",
            "api-ms-win-core-libraryloader-l1-2-0.dll",
            "api-ms-win-core-processthreads-l1-1-2.dll",
            "api-ms-win-core-profile-l1-1-0.dll",
            "api-ms-win-core-sysinfo-l1-2-1.dll"
        ]

setup(
    name = "gnank",
    version = config.VERSIO,
    author = config.AUTOR,
    author_email = config.EMAIL_AUTOR,
    license = config.LLICENCIA,
    description = config.DESCRIPCIO,
    url = config.URL_WEB,
    scripts = ['src/gnank'],
    data_files = data_files,
    windows = [{
        "script": "src/gnank",
        'icon_resources': [(1, "paquets/win32/gnank.ico")],
    }],
    options = {"py2exe": {
        "packages": "encodings",
        "includes": "cairo, pango, pangocairo, atk, gobject, gio",
        "excludes": "gdk, ltihooks, email.Generator, email.Iterators, email.Utils",
        "dll_excludes": excluded_dlls
    }},
)
