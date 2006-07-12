#!/usr/bin/env python2.4
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

from gnank import config
from distutils.core import setup

if __name__ == '__main__':

	setup(	name = "gnank",
			version = config.VERSIO,
			author = config.AUTOR,
			author_email = config.EMAIL_AUTOR,
			license = config.LLICENCIA,
			description = config.DESCRIPCIO,
			packages = ['gnank'],
			scripts = ['gnank/gnank'],
			data_files = [ (config.PIXMAPS, [config.ICONA]),
				(config.APPLICATIONS, [config.DESKTOP]),
				(config.DOC, ["GPL.txt", "LLEGIU-ME.txt", "NOVETATS.txt"])
			],
			url = config.URL_WEB
	)

