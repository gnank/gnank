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

"""Mòdul per a obtenir i desar les dades dels horaris."""

from urllib import urlopen
from domini import Quadri, Classe
import re, os

# Adreça per obtenir una llista de les assignatures.
_adr_assigs = "http://www.fib.upc.es/FIB/plsql/PUB_HORARIS.assignatures"

# Adreça per obtenir les dades dels horaris de les assugnatures passades
# per GET amb el paràmetre 'assignatures'.
_adr_classes = "http://www.fib.upc.es/FIB/plsql/PUB_HORARIS.horari_text"

# Expressió regular d'una classe
_er_classe = "^([^\s]+)\s([0-9]+)\s([0-9]+)\s([0-9]+):00\s([^\s]+)\s([^\s]+)$"

class ErrorDades(Exception):
	"""Indica que no s'ha pogut obtenir les dades."""
	pass

class ErrorCau(Exception):
	"""Indica que no s'han pogut llegir o desar les dades de la cau."""
	pass

def obre(nom_fitxer):
	"""Llegeix les dades del fitxer indicat."""

	try:
		fitxer = file(nom_fitxer, 'r')
		dades = fitxer.read()
		fitxer.close()
	except IOError:
		raise ErrorDades
	_prepara_quadri(dades)


def actualitza():
	"""Actualitza les dades des del servidor de la FIB."""

	assigs = []
	try:
		for a in urlopen(_adr_assigs):
			assigs.append(a[:-1])
		params = "?assignatures=" + "&assignatures=".join(assigs)
		dades = urlopen(_adr_classes + params).read()
	except IOError:
		raise ErrorDades
	_prepara_quadri(dades)



def _prepara_quadri(dades):
	"""Analitza i assigna les dades al quadrimestre."""

	if not dades: raise ErrorDades
	er = re.compile(_er_classe)
	Quadri().init()
	for linia in dades.splitlines():
		m = er.match(linia)
		if not m: raise ErrorDades
		try:
			assig, grup = m.group(1), int(m.group(2))
			dia, hora = int(m.group(3)), int(m.group(4))
			tipus, aula = m.group(5), m.group(6)
			classe = Classe(assig, grup, dia, hora, tipus, aula)
		except ErrorClasse:
			raise ErrorDades
		Quadri().afegeix(classe)

	
def desa(nom_fitxer):
	"""Desa les dades del quadrimestre al fixer especificat."""

	try:
		fitxer = file(nom_fitxer, "w")
		for c in sorted(Quadri().totes_les_classes()):
			linia = "%s\t%d\t%d\t%02d:00\t%s\t%s\n" % (c.assig(), c.grup(),
				c.dia(), c.hora(), c.tipus(), c.aula())
			fitxer.write(linia)
		fitxer.close()
	except IOError:
		raise ErrorDades


def desa_cau():
	"""Desa les dades del quadrimestre a la cau de l'usuari."""

	try:
		directori_cau = os.path.join(os.environ['HOME'], '.gnank')
		if not os.path.exists(directori_cau):
			os.makedirs(directori_cau)
		cau = os.path.join(directori_cau, 'cau')
	except OSError:
		raise ErrorCau
		return
	try: desa(cau)
	except ErrorDades:
		raise ErrorCau


def obre_cau():
	"""Llegeix les dades de la cau."""

	cau = os.path.join(os.environ['HOME'], '.gnank', 'cau')
	if os.path.exists(cau):
		try: obre(cau)
		except ErrorDades:
			raise ErrorCau
