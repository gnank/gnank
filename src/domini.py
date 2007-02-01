# -*- coding: UTF-8 -*-

# Gnank - cercador d'horaris de la FIB
# Copyright (C) 2006, 2007  Albert Gasset Romo
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


import dades
from dades import ErrorDades
from itertools import chain

_assigs = {}
_horaris = set()

def obre(fitxer):
	classes, horaris = dades.obre(fitxer)
	_assigs.clear()
	_afegeix_classes(classes)
	_horaris.clear()
	for horari in horaris:
		afegeix_horari_preferit(horari)

def desa(fitxer):
	iters = [assig.tuples_classes() for assig in _assigs.itervalues()]
	tuples = chain(*iters)
	dades.desa(fitxer, sorted(tuples), sorted(_horaris))

def actualitza():
	global _horaris
	classes = dades.obre_http()
	_assigs.clear()
	_afegeix_classes(classes)
	horaris_valids = set()
	for horari in _horaris:
		horaris_valids.add(_horari_valid(horari))
	horaris_valids.discard(tuple())
	_horaris = horaris_valids

def grups_disponibles():
	grups_a = lambda a: [(g.nom) for g in sorted(a.grups_disponibles())]
	return [(a.nom, grups_a(a)) for a in sorted(_assigs.itervalues())]

def grups_disponibles_mati():
	grups_a = lambda a: [(g.nom) for g in sorted(a.grups_disponibles_mati())]
	return [(a.nom, grups_a(a)) for a in sorted(_assigs.itervalues())]

def grups_disponibles_tarda():
	grups_a = lambda a: [(g.nom) for g in sorted(a.grups_disponibles_tarda())]
	return [(a.nom, grups_a(a)) for a in sorted(_assigs.itervalues())]

def horaris_preferits():
	return [Horari(g) for g in _horaris]

def es_horari_preferit(horari):
	return tuple(sorted(horari)) in _horaris

def afegeix_horari_preferit(horari):
	_horaris.add(tuple(sorted(horari)))

def elimina_horari_preferit(horari):
	_horaris.discard(tuple(sorted(horari)))

def _afegeix_classes(classes):
	for assig, grup, dia, hora, tipus, aula in classes:
		classe = Classe(assig, grup, dia, hora, tipus, aula)
		_assigs.setdefault(assig, Assig(assig)).afegeix_classe(classe)

def _hores_classes(assig, grup):
	return  _assigs[assig].grup(grup).hores_classes()

def _classes_dia_hora(assig, grup, dia, hora):
	return _assigs[assig].grup(grup).classes(dia, hora)

def _horari_valid(horari):
	horari_valid = []
	for nom_assig, grup in horari:
		assig = _assigs.get(nom_assig)
		if assig and assig.te_grup(grup):
			horari_valid.append((nom_assig, grup))
	return tuple(horari_valid)


class Classe(object):

	valors_dia = range(1, 6)
	valors_hora = range(8, 21)
	valors_tipus = ['T', 'P', 'L']
	hora_inici_tarda = 15

	def __init__(self, assig, grup, dia, hora, tipus, aula):
		if int(dia) not in self.valors_dia: raise ValueError
		if int(hora) not in self.valors_hora: raise ValueError
		if tipus not in self.valors_tipus: raise ValueError
		self.assig = assig
		self.grup = grup
		self.dia = int(dia)
		self.hora = int(hora)
		self.tipus = tipus
		self.aula = aula

	def tupla(self):
		return (self.assig, self.grup, str(self.dia), str(self.hora),
			self.tipus,	self.aula)

	def _cmp_tipus(self, other):
		index_self = Classe.valors_tipus.index(self.tipus)
		index_other = Classe.valors_tipus.index(other.tipus)
		return cmp(index_self, index_other)

	def __cmp__(self, other):
		c = cmp(self.assig, other.assig)
		if c != 0: return c
		c = Grup.cmp_noms(self.grup, other.grup)
		if c != 0: return c
		c = cmp(self.dia, other.dia)
		if c != 0: return c
		c = cmp(self.hora, other.hora)
		if c != 0: return c
		c = self._cmp_tipus(other)
		if c != 0: return c
		return cmp(self.aula, other.aula)

	def __hash__(self):
		return hash(self.assig + self.grup + self.tipus + self.aula)


class Grup(object):

	def __init__(self, nom, supergrup=None):
		self.nom = nom
		self._supergrup = supergrup
		self._classes = {} # { (dia, hora): classes }
		self._mati = True
		self._tarda = True

	def afegeix_classe(self, classe):
		self._classes.setdefault((classe.dia, classe.hora), set()).add(classe)
		if classe.hora < Classe.hora_inici_tarda:
			self._tarda = False
		else:
			self._mati = False

	def nomes_mati(self):
		return self._mati and (not self._supergrup or self._supergrup._mati)

	def nomes_tarda(self):
		return self._tarda and (not self._supergrup or self._supergrup._tarda)

	def __cmp__(self, other):
		return Grup.cmp_noms(self.nom, other.nom)

	def __hash__(self):
		return hash(self.nom)

	def tuples_classes(self):
		for classe in chain(*self._classes.itervalues()):
			yield classe.tupla()

	def hores_classes(self):
		hores = set(self._classes.iterkeys())
		if self._supergrup:
			hores.update(self._supergrup.hores_classes())
		return hores

	def classes(self, dia, hora):
		classes_grup = self._classes.get((dia, hora), [])
		classes_supergrup = self._supergrup and \
			self._supergrup.classes(dia, hora) or []
		return chain(classes_grup, classes_supergrup)

	@classmethod
	def cmp_noms(cls, nom1, nom2):
		if nom1.isdigit() and nom2.isdigit():
			return cmp(int(nom1), int(nom2))
		else:
			return cmp(nom1, nom2)


class Assig(object):

	def __init__(self, nom):
		self.nom = nom
		self._grups = {}
		self._supergrups = {}

	def afegeix_classe(self, classe):
		grup = self._grups.get(classe.grup) \
			or self._supergrups.get(classe.grup) \
			or self._crea_grup(classe.grup)
		grup.afegeix_classe(classe)

	def _crea_grup(self, nom):
		if nom.isdigit() and int(nom) % 10 != 0:
			nom_s = str(int(nom) - int(nom) % 10)
			if nom_s in self._grups:
				sgrup = self._grups.pop(nom_s)
				self._supergrups[nom_s] = sgrup
			else:
				sgrup = self._supergrups.setdefault(nom_s, Grup(nom_s))
			grup = Grup(nom, sgrup)
		else:
			grup = Grup(nom)

		self._grups[nom] = grup
		return grup

	def grups_disponibles(self):
		return self._grups.itervalues()

	def grups_disponibles_mati(self):
		return [g for g in self._grups.itervalues() if g.nomes_mati()]

	def grups_disponibles_tarda(self):
		return [g for g in self._grups.itervalues() if g.nomes_tarda()]

	def tuples_classes(self):
		grups = chain(self._grups.itervalues(), self._supergrups.itervalues())
		iters_classes = [grup.tuples_classes() for grup in grups]
		return chain(*iters_classes)

	def grup(self, nom):
		return self._grups[nom]

	def __cmp__(self, other):
		return cmp(self.nom, other.nom)

	def te_grup(self, nom_grup):
		return nom_grup in self._grups


class Horari(object):

	def __init__(self, grups=[]):
		self._tupla = tuple(sorted(grups))
		self._grups = {} # { assig: grups }
		for assig, grup in grups:
			self._grups.setdefault(assig, set()).add(grup)
		self._calcula_estadistiques()

	def grups(self):
		return self._tupla

	def classes(self, dia, hora):
		classes = set()
		for assig, grups_assig in self._grups.iteritems():
			for grup in grups_assig:
				for c in _classes_dia_hora(assig, grup, dia, hora):
					classes.add(c)
		return sorted(classes)

	def assignatures(self):
		return sorted(self._grups.iterkeys())

	def __cmp__(self, other):
		for (assig1, grup1), (assig2, grup2) in zip(self._tupla, other._tupla):
			c = cmp(assig1, assig2)
			if c != 0: return c
			c = Grup.cmp_noms(grup1, grup2)
			if c != 0: return c
		return cmp(len(self._tupla), len(self._tupla))

	def __hash__(self):
		return hash(self._tupla)

	def __iter__(self):
		return iter(self._tupla)

	def _calcula_estadistiques(self):
		assigs_dh = {} # { (dia, hora) : assig }

		for assig, grup in self._tupla:
			for dh in _hores_classes(assig, grup):
				assigs_dh.setdefault(dh, set()).add(assig)

		self.hores = len(assigs_dh)
		self.hores_mati = 0
		self.hores_tarda = 0
		self.solapaments = 0
		self.fragments = 0
		self.primera_hora = Classe.valors_hora[-1]
		self.ultima_hora = Classe.valors_hora[0]
		for (dia, hora), assigs in assigs_dh.iteritems():
			if hora < Classe.hora_inici_tarda:
				self.hores_mati += 1
			else:
				self.hores_tarda += 1
			self.solapaments += len(assigs) - 1
			if (dia, hora - 1) not in assigs_dh:
				self.fragments += 1
			if hora < self.primera_hora:
				self.primera_hora = hora
			if hora > self.ultima_hora:
				self.ultima_hora = hora


class Cerca(object):
	"""Realitza cerques de combinacions d'horaris.

	Emmagatzema els grups candidats, el mínim nombre d'assignatures i el
	nombre màxim de solapaments."""

	def __init__(self, grups, min_assig, max_solap):
		"""Inicializa els paràmetres de cerca.

		'grups' és una seqüència de tuples (assignatura, grup), 'min_assig' és
		el nombre mínim d'assignatures i 'max_solap' el nombre màxim de
		solapaments de les solucions."""

		# Llista dels noms de les assignatures.
		self._assigs = []

		# Vector de grups per assignatura. Cada element de posició 'i' és un
		# vector dels números de grup de l'assignatura self._assigs[i].
		self._grups = []

		grups_per_assig = {}
		for assig, grup in grups:
			grups_assig = grups_per_assig.setdefault(assig, [])
			grups_assig.append(grup)

		for assig, grups in grups_per_assig.iteritems():
			self._assigs.append(assig)
			self._grups.append(grups)

		self._min_assig = min_assig
		self._max_solap = max_solap

	def n_combinacions(self):
		n = 1
		for grups in self._grups:
			n *= len(grups) + 1
		return n

	def horaris(self):
		"""Iterador sobre els horaris solució.

		Generador que cerca tots els horaris solució."""

		# Vector d'enters de la mateixa mida que self._grups. Cada element de
		# posició i indica la posició del grup seleccionat de self._grups[i].
		# Si l'element de posició 'i' és igual a len(self._grups[i]) vol dir
		# que no se selecciona cap grup per aquella assignatura.
		# Cada element representa una decisió, un nivell en l'arbre de cerca.
		self._grup = [0] * len(self._grups)
		
		# Indica el nombre de classes per cada dia i hora. Les claus són tuples
		# (dia, hora) i els valors són enters.
		self._classes = {}

		# Nombre de solapaments de la combinació actual.
		self._n_solap = 0

		# Nombre d'assignatures de la combinació actual.
		self._n_assig = 0

		# Nivell de l'arbre de cerca en la situació actual. Nivell 0 indica
		# que no hi ha cap decisió presa. Nivell len(self._grup) indica que
		# la combinació és completa i candidata a solució. Quan és negatiu
		# indica que ja s'ha acabat la cerca.
		self._nivell = 0

		# L'arbre de cerca es recorre recursivament, saltant els nodes que
		# condueixen a combinacions no solucionables.
		while self._nivell >= 0:

			# Si el node és fulla, només cal mirar si la combinació és
			# solució i tornar cap al pare.
			if self._es_fulla():
				if self._es_solucio():
					yield Horari(self._solucio()), self._combinacio()
				self._torna_cap_al_pare()

			# Es mira si el node ja s'ha explorat anteriorment, és a dir, si
			# s'hi ha arribat retornant des d'un fill enlloc d'anant des del
			# pare.
			elif self._ja_explorat():
				if self._queden_fills():
					self._explora_el_fill_seguent()
				else:
					self._torna_cap_al_pare()

			# Si amb els grups seleccionats fins al  moment és impossible
			# trobar noves solucions es torna cap al pare.
			elif self._no_solucionable():
				self._torna_cap_al_pare()

			# És possible trobar noves solucions, per tant s'exploren els
			# fills del node.
			else:
				self._explora_el_fill_seguent()

	def _es_fulla(self):
		"""Indica si el node actual és fulla de l'arbre."""

		return self._nivell == len(self._grup)

	def _es_solucio(self):
		"""Indica si la combinació actual és solució."""

		return self._n_solap <= self._max_solap \
				and self._n_assig >= self._min_assig

	def _solucio(self):
		"""Llista de grups de la combinació solució."""

		grup = self._grup
		solucio = []
		for n in range(len(grup)):
			if grup[n] < len(self._grups[n]):
				solucio.append((self._assigs[n], self._grups[n][grup[n]]))
		return solucio

	def _combinacio(self):
		grup = self._grup
		c = 0
		n = 1
		for i in range(len(self._grup) - 1, -1, -1):
			c += self._grup[i] * n
			n *= len(self._grups[i]) + 1
		return c

	def _ja_explorat(self):
		"""Cert si el node actual ja s'ha explorat anteriorment.

		Retorna un booleà indicant si el node actual s'hi ha arribat des del
		pare o des d'un fill."""
		
		return self._grup[self._nivell] > 0

	def _queden_fills(self):
		"""Cert si quden fills del node actual per explorar."""
		
		nivell = self._nivell
		return self._grup[nivell] <= len(self._grups[nivell])


	def _no_solucionable(self):
		"""Indica si és impossible trobar noves solucions des del node."""

		return self._n_solap > self._max_solap \
			or self._min_assig - self._n_assig > len(self._grup) - self._nivell

	def _explora_el_fill_seguent(self):
		"""Explora el següent fill del node."""

		nivell = self._nivell
		grup = self._grup
		grups = self._grups
		# Es comprova si s'està seleccionant un grup
		if grup[nivell] < len(grups[nivell]):
			self._afegeix_grup()
			self._n_assig += 1
		self._nivell += 1

	def _torna_cap_al_pare(self):
		"""Situa la cerca al node pare."""

		nivell = self._nivell
		grup = self._grup
		grups = self._grups
		# Si no és fulla posa el nivell actual a 0 perquè després es comenci
		# amb el primer fill.
		if nivell < len(grup):
			grup[nivell] = 0
		nivell -= 1
		self._nivell = nivell
		if nivell < 0: return
		# Es comprova si s'està desseleccionant un grup
		if grup[nivell] < len(grups[nivell]):
			self._treu_grup()
			self._n_assig -= 1
		grup[nivell] += 1

	def _afegeix_grup(self):
		"""S'afegeixen les classes del grup del nivell actual."""

		nivell = self._nivell
		assig = self._assigs[nivell]
		index_grup = self._grup[nivell]
		grup = self._grups[nivell][index_grup]
		classes = self._classes
		n_solap = self._n_solap
		for c in _hores_classes(assig, grup):
			s = classes.get(c, 0)
			if (s >= 1):
				n_solap += 1
			classes[c] = s + 1
		self._n_solap = n_solap

	def _treu_grup(self):
		"""Es treuen les classes del grup del nivell actual."""

		nivell = self._nivell
		assig = self._assigs[nivell]
		index_grup = self._grup[nivell]
		grup = self._grups[nivell][index_grup]
		classes = self._classes
		n_solap = self._n_solap
		for c in _hores_classes(assig, grup):
			s = classes[c] - 1
			if (s >= 1):
				n_solap -= 1
			classes[c] = s
		self._n_solap = n_solap

