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
from domini import Quadri, Classe, ErrorClasse
import re, os

# Adreça per obtenir una llista de les assignatures.
_adr_assigs = "http://www.fib.upc.es/FIB/plsql/PUB_HORARIS.assignatures"

# Adreça per obtenir les dades dels horaris de les assugnatures passades
# per GET amb el paràmetre 'assignatures'.
_adr_classes = "http://www.fib.upc.es/FIB/plsql/PUB_HORARIS.horari_text"

# Expressió regular d'una classe
_er_classe = "^([^\s]+)\s([0-9]+)\s([0-9]+)\s([0-9]+):00\s([^\s]+)\s([^\s]+)$"

# Expressió regular d'una seqüència de grups
_er_grups = "^[^\s]+\s[0-9]+(\s[^\s]+\s[0-9]+)*$"
_er_grup = "([^\s]+)\s([0-9]+)"

# Expressió regular de línia en blanc
_er_blanc = "^\s*$"

class ErrorDades(Exception):
	"""Indica que no s'ha pogut obtenir les dades."""
	pass

class ErrorCau(Exception):
	"""Indica que no s'han pogut llegir o desar les dades de la cau."""
	pass

def obre(nom_fitxer):
	"""Llegeix les dades del fitxer indicat.

	Retorna una llista de cerques. Una cerca és una llista d'horaris."""

	try:
		fitxer = file(nom_fitxer, 'r')
		dades = fitxer.read()
		fitxer.close()
	except IOError:
		raise ErrorDades
	dades = dades.split(";")
	dades_horaris, dades_cerques = dades[0], dades[1:]
	_prepara_quadri(dades_horaris)
	cerques = []
	for dades_cerca in dades_cerques:
		cerques.append(_deserialitza_cerca(dades_cerca))
	return cerques


def _deserialitza_cerca(dades):
	er = re.compile(_er_grups)
	grup = re.compile(_er_grup)
	blanc = re.compile(_er_blanc)
	cerca = []
	grups = lambda l: [(m.group(1), int(m.group(2))) for m in grup.finditer(l)]
	for linia in dades.splitlines():
		if not blanc.match(linia):
			m = er.match(linia)
			cerca.append(grups(linia))
	return cerca


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
	blanc = re.compile(_er_blanc)
	Quadri().init()
	for linia in dades.splitlines():
		if not blanc.match(linia):
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

	
def desa(nom_fitxer, cerques=None):
	"""Desa les dades i les cerques al fixer especificat.

	'cerques' és una seqüència de cerques. Una cerca és una
	seqüència d'horaris."""

	try:
		fitxer = file(nom_fitxer, "w")
		for c in sorted(Quadri().totes_les_classes()):
			linia = "%s\t%d\t%d\t%02d:00\t%s\t%s\n" % (c.assig(), c.grup(),
				c.dia(), c.hora(), c.tipus(), c.aula())
			fitxer.write(linia)
		if cerques is not None:
			text_grups = lambda grups: " ".join(["%s %d" % (assig, grup)
				for assig, grup in grups]) + "\n"
			text_cerca = lambda cerca: ";\n" + "".join([text_grups(grups)
				for grups in cerca])
			text_cerques = "".join([text_cerca(cerca) for cerca in cerques])
			fitxer.write(text_cerques)
			fitxer.write("\n")
		fitxer.close()
	except IOError:
		raise ErrorDades


def desa_cau(cerques=None):
	"""Desa les dades del quadrimestre a la cau de l'usuari."""

	try:
		directori_cau = os.path.join(os.environ['HOME'], '.gnank')
		if not os.path.exists(directori_cau):
			os.makedirs(directori_cau)
		cau = os.path.join(directori_cau, 'cau')
	except OSError:
		raise ErrorCau
		return
	try: desa(cau, cerques)
	except ErrorDades:
		raise ErrorCau


def obre_cau():
	"""Llegeix les dades de la cau."""

	cau = os.path.join(os.environ['HOME'], '.gnank', 'cau')
	if os.path.exists(cau):
		try: 
			return obre(cau)
		except ErrorDades:
			raise ErrorCau
