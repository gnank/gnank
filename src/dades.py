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

import re
import json
import logging
from urllib.request import urlopen

import sys
if getattr(sys, 'frozen', False):
	import ssl
	ssl._create_default_https_context = ssl._create_unverified_context

CARRERES = [
	("Grau en Enginyeria Informàtica", 'GRAU'),
	("Grau en Bioinformàtica", 'GBIO'),
	("Grau en Ciència i Enginyeria de Dades", 'GCED'),
	("Màster en Enginyeria Informàtica", 'MEI'),
	("Màster en Lògica Pura i Aplicada", 'MPAL'),
	("Master in Artificial Intelligence", 'MAI'),
	("Master in Innovation and Research in Informatics", 'MIRI'),
	("Erasmus Mundus in Big Data Management and Analytics", 'BDMA'),
	("Erasmus Mundus en Tecnologies de la Informació per a la Intel·ligència Empresarial", 'IT4BI'),
	("Màster en Formació del Professorat d'ESO i Batxillerat, FP i Ensenyament d'Idiomes (MPFS-FP)", 'MFPS-FP'),
	("Màster en Formació del Professorat d'ESO i Batxillerat, FP i Ensenyament d'Idiomes (MPFS-TEC)", 'MFPS-TEC')
]

CLIENT_ID = 'DGdJQPNkDnvzssbFsfWkaAAWHuOC2QheX10G7M9U'

API_URL = 'https://api.fib.upc.edu/v2'
URL_ASSIGS = API_URL + '/assignatures/?format=json&client_id={0}&pla='.format(CLIENT_ID)
URL_QUATRI = API_URL + '/quadrimestres/actual-horaris/?format=json&client_id={0}'.format(CLIENT_ID)

_ER_CLASSE = re.compile(r'[^\s]+\s+[^\s]+\s+[0-9]+\s+[0-9]+(:00)?\s+[^\s]+\s+[^\s]+')
_ER_HORARI = re.compile(r'[^\s]+\s+[^\s]+(\s+[^\s]+\s+[^\s]+)*')


class ErrorOpcions(Exception):
	pass


class ErrorDades(Exception):
	pass


def obre(fitxer):
	carrera = ""
	classes = []
	horaris = []
	separador_trobat = False
	plaestudis_trobat = False

	try:
		f = open(fitxer, "r")
	except IOError:
		raise ErrorDades

	try:
		for linia in f:
			linia = linia.strip()
			if linia == "":
				continue
			elif not plaestudis_trobat:
				carrera = linia
				plaestudis_trobat = True
			elif linia == ";":
				separador_trobat = True
			elif separador_trobat:
				if not _ER_HORARI.match(linia):
					raise ErrorDades
				linia = linia.split()
				horaris.append(list(zip(linia[::2], linia[1::2])))
			else:
				if not _ER_CLASSE.match(linia):
					raise ErrorDades
				linia = linia.split()
				linia[3] = linia[3].split(":")[0]
				classes.append(linia)
	finally:
		f.close()

	return carrera, classes, horaris


def desa(fitxer, carrera, classes, horaris=None):
	try:
		f = open(fitxer, "w")
		f.write(carrera)
		f.write("\n")
		for classe in classes:
			f.write(" ".join(classe))
			f.write("\n")
		if horaris is not None:
			f.write(";\n")
			for horari in horaris:
				f.write(" ".join([a + " " + g for a, g in horari]))
				f.write("\n")
	except IOError:
		raise ErrorDades
	else:
		f.close()


def obre_http(carrera):
	classes = []
	try:
		if carrera == "":
			raise ErrorOpcions

		# obtenim les assignatures
		assigs = [a['id'] for a in json.load(urlopen(URL_ASSIGS + carrera))['results']]
		if not assigs:
			return []

		# obtenim la URL dels horaris i els horaris
		URL_CLASSES = json.load(urlopen(URL_QUATRI))['classes']
		params = '&client_id={0}&codi_assig={1}'.format(CLIENT_ID, ','.join(assigs))

		for classe in json.load(urlopen(URL_CLASSES + params))['results']:
			nom = classe['codi_assig']
			# ignora noms d'assignatura especials
			if nom in ["EXAMENS", "TANCAT", "RESERVAT"]:
				continue

			grup = classe['grup']
			dia = classe['dia_setmana']
			tipus = classe['tipus']
			aules = ''.join(classe['aules'].split(' '))

			hora = int(classe['inici'].split(':')[0])
			durada = classe['durada']

			for i in range(durada):
				classes.append([nom, grup, dia, hora + i, tipus, aules])
	except IOError as e:
		logging.error(e)
		raise ErrorDades
	return classes
