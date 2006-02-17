
# -*- coding: UTF-8 -*-

# Gnank - cercador d'horaris de la FIB
# Copyright (C) 2006  Albert Gasset Romo
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# ERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os

NOM = "Gnank"
VERSIO = "1.0"
LLANCAMENT = False
REVISIO = "$Revision$".split()[1]
DESCRIPCIO =  "Cercador d'horaris de la FIB"
COPYRIGHT = "Copyright © 2006  Albert Gasset Romo"
AUTOR = "Albert Gasset Romo"
EMAIL_AUTOR = "albert.gasset@gmail.com"
LLICENCIA = "GPL"
AUTORS = [
	"Albert Gasset Romo <albert.gasset@gmail.com>",
	"Jordà Polo <jorda@ettin.org>"
]
INFO_LLICENCIA = """\
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
ERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""

ICONA="gnank.png"
PIXMAPS="/usr/share/pixmaps/"
DESKTOP="gnank.desktop"
APPLICATIONS="/usr/share/applications"
DOC="/usr/share/doc/gnank/"

def cami(directori, fitxer):
	if os.access(fitxer,os. F_OK): return fitxer
	if os.access(directori+fitxer,os. F_OK): return directori + fitxer
	return None

