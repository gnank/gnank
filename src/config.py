# -*- coding: utf-8 -*-

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

import logging
import os
from os.path import abspath, dirname, join
import re
import sys

NOM = "Gnank"
VERSIO = "4.0.2"
DESCRIPCIO = "Cercador d'horaris de la FIB"
URL_WEB = "https://github.com/gnank/gnank"
COPYRIGHT = """\
Copyright © 2006 - 2007 Albert Gasset Romo
Copyright © 2011 - 2019 Marc Cornellà
"""
AUTOR = "Marc Cornellà"
EMAIL_AUTOR = "marc.cornella@live.com"
LLICENCIA = "GPL"
AUTORS = [
	"Desenvolupador actual:",
	"Marc Cornellà <marc.cornella@live.com>",
	"",
	"Desenvolupador principal:",
	"Albert Gasset Romo <albert.gasset@gmail.com>",
	"",
	"Paquet Debian i pedaços:",
	"Jordà Polo <jorda@ettin.org>"
]
INFO_LLICENCIA = """\
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

if sys.platform == "win32":
	import winreg

	def regval(key, subkey, name):
		key = winreg.OpenKey(key, subkey)
		try:
			ret = winreg.QueryValueEx(key, name)
		except WindowsError:
			return None
		key.Close()
		if ret[1] == winreg.REG_EXPAND_SZ:
			substenv = lambda m: os.environ.get(m.group(1), m.group(0))
			return re.compile(r'%([^|<>=^%]+)%').sub(substenv, ret[0])
		return ret[0]
	DIR_USUARI = join(regval(winreg.HKEY_CURRENT_USER,
			"Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders",
			"AppData"), "Gnank")
else:
	DIR_USUARI = join(os.environ['HOME'], ".gnank")


HORARIS_USUARI = join(DIR_USUARI, "horaris")
REGISTRE_USUARI = join(DIR_USUARI, "registre")


def crea_dir_usuari():
	try:
		if not os.path.exists(DIR_USUARI):
			os.makedirs(DIR_USUARI)
	except OSError:
		pass


def cami(fitxer):
	cami_fitxer = join(gnank_dir, fitxer)
	if os.access(cami_fitxer, os.F_OK):
		return cami_fitxer
	logging.warning("No es pot accedir al fitxer: %s", fitxer)
	return None
