#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Gnank - cercador d'horaris de la FIB
# Copyright (C) 2006, 2007  Albert Gasset Romo
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

import unittest

import domini
from domini import Classe

class TestClasse(unittest.TestCase):

	def test_crea_correcte(self):
		for dia in range(1, 6):
			for hora in range(8, 21):
				for tipus in ('T', 'P', 'L'):
					Classe("assig", "grup", dia, hora, tipus, "aula")

	def test_crea_incorrecte(self):
		self.assertRaises(ValueError, Classe, "A", "G", 0, 8, "L", "aula")
		self.assertRaises(ValueError, Classe, "A", "G", 6, 8, "L", "aula")
		self.assertRaises(ValueError, Classe, "A", "G", 1, 7, "L", "aula")
		self.assertRaises(ValueError, Classe, "A", "G", 1, 21, "L", "aula")
		self.assertRaises(ValueError, Classe, "A", "G", 1, 8, "H", "aula")

	def test_comparacio(self):
		classes = [
			Classe("A", "10", 1, 8, "T", "A5001"),
			Classe("A", "10", 1, 8, "T", "A5002"),
			Classe("A", "10", 1, 8, "P", "A5001"),
			Classe("A", "10", 1, 8, "L", "A5001"),
			Classe("A", "10", 1, 9, "T", "A5001"),
			Classe("A", "10", 2, 8, "T", "A5001"),
			Classe("A", "11", 1, 8, "T", "A5001"),
			Classe("A", "100", 1, 8, "T", "A5001"),
			Classe("A", "M", 1, 8, "T", "A5001"),
			Classe("B", "10", 1, 8, "T", "A5001"),
		]
		for index1, classe1 in enumerate(classes):
			for index2, classe2 in enumerate(classes):
				c = cmp(classe1, classe2)
				self.assertEqual(cmp(index1, index2), c,
					"cmp(index %d, index %d) != %d" % (index1, index2, c))


class TestGrup(unittest.TestCase):
	pass

class TestAssig(unittest.TestCase):
	pass

class TestHorari(unittest.TestCase):
	pass

class TestCerca(unittest.TestCase):
	pass

class TestDomini(unittest.TestCase):
	pass


if __name__ == '__main__':
	unittest.main()
