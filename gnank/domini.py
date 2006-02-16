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

"""Mòdul per a la gestió dels horaris i la realització de cerques."""

from itertools import chain


class ErrorClasse(Exception):
	"""Indica que els paràmetres de creació d'una classe no són vàlids."""
	pass


class Classe(object):
	"""Informació d'una classe.

	Emmagatzema la informació d'una classe: nom d'assignatura, número de grup,
	dia de la setmana, hora del dia, tipus i aula."""

	# Valors possibles per al dia de la setmana.
	_valors_dia = range(1, 6)
	# Valors possibles per a l'hora del dia.
	_valors_hora = range(8, 21)
	# Hora en que comencen les classes de la tarda.
	_hora_tarda = 15
	# Valors possibles per al tipus de classe.
	_valors_tipus = ['T', 'P', 'L']

	@classmethod
	def valors_dia(cls):
		return iter(cls._valors_dia)

	@classmethod	
	def valors_hora(cls):
		return iter(cls._valors_hora)

	@classmethod
	def valors_tipus(cls):
		return iter(cls._valors_tipus)

	@classmethod
	def hora_tarda(cls):
		return cls._hora_tarda

	def __init__(self, assig, grup, dia, hora, tipus, aula):
		"""Crea una classe.

		Llança una excepció ErrorClasse si els parànetres sno són vàlids."""

		if dia not in self._valors_dia: raise ErrorClasse
		if hora not in self._valors_hora: raise ErrorClasse
		if tipus not in self._valors_tipus: raise ErrorClasse

		self._assig = assig
		self._grup = grup
		self._dia = dia
		self._hora = hora
		self._tipus = tipus
		self._aula = aula

	def assig(self):
		return self._assig

	def grup(self):
		return self._grup

	def dia(self):
		return self._dia

	def hora(self):
		return self._hora

	def tipus(self):
		return self._tipus

	def aula(self):
		return self._aula

	def __cmp__(self, other):
		c = cmp(self._assig, other._assig)
		if c != 0: return c
		c = cmp(self._grup, other._grup)
		if c != 0: return c
		c = cmp(self._dia, other._dia)
		if c != 0: return c
		c = cmp(self._hora, other._hora)
		if c != 0: return c
		self_i = Classe._valors_tipus.index(self._tipus)
		other_i = Classe._valors_tipus.index(other._tipus)
		c = cmp(self_i, other_i)
		if c != 0: return c
		return cmp(self._aula, other._aula)


class Singleton(object):
	"""Implementació del patró de disseny Singleton.

	Les subclasses han de definir el mètode 'init' en lloc de '__init__'."""

	def __new__(klass, *args, **kwds):
		"""Crea unoa instància de la classe si encara no se n'ha creat cap."""

		instance = klass.__dict__.get("__instance__")
		if instance is not None: return instance
		instance = object.__new__(klass)
		instance.init(*args, **kwds)
		klass.__instance__ = instance
		return instance

	def init(self, *args, **kwds):
		"""Mètode d'inicialització a definir en lloc de '__init__'."""
		pass


class Quadri(Singleton):
	"""Informació del quadrimestre.

	Emmagatzema la informació dels horaris del quadrimestre. N'hi ha una única
	instància."""

	def init(self):
		"""Inicialitza la instància de Quadri."""

		# Diccionari amb les classes del quadrimestre. Les claus són noms
		# d'assignatura i els valors són diccionaris. Les claus d'aquests 
		# diccionaris són números de grup i els valors són diccionaris. Les
		# claus d'aquests diccionaris són tuples (dia, hora) i els valors
		# són conjunts de classes.
		# Resumint: { assig -> { grup -> { dia, hora -> classes } } } 
		self._classes = {}

	def afegeix(self, classe):
		"""Afegeix una classe al quadrimestre."""

		classes_a = self._classes.setdefault(classe.assig(), {})
		classes_g = classes_a.setdefault(classe.grup(), {})
		dia_hora = (classe.dia(), classe.hora())
		classes_dh = classes_g.setdefault(dia_hora, set())
		classes_dh.add(classe)

	def assignatures(self):
		"""Iterador sobre els noms de les assigantures del quadrimestre."""

		return self._classes.iterkeys()

	def grups(self, assig):
		"""Iterador sobre els números de grup de l'assignatura.

		Els grups són grups escollibes, és a dir, no inclou els supergrups si
		tenen subgrups."""

		classes_g = self._classes.get(assig, {})
		grups = set(classes_g.iterkeys())
		for g in classes_g.iterkeys():
			if g % 10 != 0:
				grups.remove(g)
				grups.discard(g - g % 10)
				yield g

		for g in grups: yield g

	def hores_classe(self, assig, grup):
		"""Iterador sobre tuples (dia, hora) de les classes del grup."""

		classes_a = self._classes.get(assig, {})
		classes_g = classes_a.get(grup, {})
		if grup % 10 == 0:
			return classes_g.iterkeys()
		else:
			classes_sg = classes_a.get(grup - grup % 10, {})
			return chain(classes_sg.iterkeys(), classes_g.iterkeys())

	def classes(self, assig, grup, dia_hora):
		"""Iterador sobre les classes grup a l'hora especificada."""

		classes_a = self._classes.get(assig, {})
		classes_g = classes_a.get(grup, {})
		classes_dh_g = classes_g.get(dia_hora, [])
		if grup % 10 == 0:
			return iter(classes_dh_g)
		else:
			classes_sg = classes_a.get(grup - grup % 10, {})
			classes_dh_sg = classes_sg.get(dia_hora, [])
			return chain(iter(classes_dh_sg), iter(classes_dh_g))

	def totes_les_classes(self):
		"""Iterador sobre totes leses classes del quadrimestre."""

		for classes_a in self._classes.itervalues():
			for classes_g in classes_a.itervalues():
				for classes_dh in classes_g.itervalues():
					for classe in classes_dh:
						yield classe


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
					yield Horari(self._solucio())
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
		grup[nivell] += 1
		self._nivell += 1

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
		if nivell >= 0:
			grup[nivell] += 1

	def _afegeix_grup(self):
		"""S'afegeixen les classes del grup del nivell actual."""

		nivell = self._nivell
		assig = self._assigs[nivell]
		index_grup = self._grup[nivell]
		grup = self._grups[nivell][index_grup]
		classes = self._classes
		n_solap = self._n_solap
		for c in Quadri().hores_classe(assig, grup):
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
		for c in Quadri().hores_classe(assig, grup):
			s = classes[c] - 1
			if (s >= 1):
				n_solap -= 1
			classes[c] = s
		self._n_solap = n_solap


class Horari(object):
	"""Ofereix les dades de l'horari resultant d'un conjunt de grups."""

	def __init__(self, grups=[]):
		"""Crea un horari.

		'grups' és una seqüència de tuples (assignatura, grup)."""

		# Sseqüència de tuples (assig, grup).
		self._grups = [g for g in grups]

		# Diccionari on s'emmagatzemen, per cada dia i hora, les assignatures
		# que hi tenen classe. Les claus són tuples (dia, hora) i els valors
		# conjunts d'assignatures.
		classes = {}

		for assig, grup in grups:
			for dh in Quadri().hores_classe(assig, grup):
				assigs = classes.setdefault(dh, set())
				assigs.add(assig)

		self._hores = len(classes)
		self._hores_mati = 0
		self._solapaments = 0
		self._fragments = 0
		tarda = Classe.hora_tarda()
		for (dia, hora), assigs in classes.iteritems():
			if hora < tarda: self._hores_mati += 1
			self._solapaments += len(assigs) - 1
			if (dia, hora - 1) not in classes: self._fragments += 1

	def classes(self, dia_hora):
		"""Iterador sobre les classes del dia i hora indicats."""

		classes = set()
		for assig, grup in self._grups:
			for c in Quadri().classes(assig, grup, dia_hora):
				classes.add(c)
		return iter(classes)

	def grups(self):
		"""Iterador sobre tuples (assignatura, grup)."""
		return iter(self._grups)

	def hores(self):
		"""Nombre d'hores de l'horari."""
		return self._hores

	def hores_mati(self):
		"""Nombre d'hores de mati de l'horari."""
		return self._hores_mati

	def hores_tarda(self):
		"""Nombre d'hores de tarda de l'horari."""
		return self._hores - self._hores_mati

	def solapaments(self):
		"""Nombre de solapaments de l'horari."""
		return self._solapaments

	def fragments(self):
		"""Nombre de fragments de l'horari."""
		return self._fragments

