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
import dades
import os, _thread, http.server

FITXER_TMP = "test_dades.tmp"


class TestObre(unittest.TestCase):

	def tearDown(self):
		try: os.remove(FITXER_TMP)
		except OSError: pass

	def _comprova_classes(self, tuples, text):
		tuples = [tuple(t) for t in tuples]
		tuples_text = []
		for l in text.split("\n"):
			if l.strip() != "":
				tuples_text.append(tuple(l.split()))
		self.assertEqual(tuple(tuples), tuple(tuples_text))

	def _comprova_horaris(self, tuples, text):
		tuples_horari = lambda h: [tuple(g) for g in h]
		tuples = [tuple(tuples_horari(h)) for h in tuples]
		tuples_text = []
		tuples_horari = lambda h: list(zip(h.split()[::2], h.split()[1::2]))
		for l in text.split("\n"):
			if l.strip() != "":
				tuples_text.append(tuple(tuples_horari(l)))
		self.assertEqual(tuple(tuples), tuple(tuples_text))

	def test_obre_fitxer_buit(self):
		f = file(FITXER_TMP, "wb")
		f.close()
		classes, horaris = dades.obre(FITXER_TMP)
		self.assertEqual(tuple(classes), ())
		self.assertEqual(tuple(horaris), ())

	def test_obre_fitxer_buit_amb_separador(self):
		f = file(FITXER_TMP, "wb")
		f.write(";\n")
		f.close()
		classes, horaris = dades.obre(FITXER_TMP)
		self.assertEqual(tuple(classes), ())
		self.assertEqual(tuple(horaris), ())

	def test_obre_classes(self):
		text = """
			A 10 1 8 T A5001
			B M 3 12 P A6002
		"""
		f = file(FITXER_TMP, "wb")
		f.write(text)
		f.close()
		classes, horaris = dades.obre(FITXER_TMP)
		self._comprova_classes(classes, text)
		self.assertEqual(tuple(horaris), ())

	def test_obre_classes_amb_separador(self):
		text = """
			A 10 1 8 T A5001
			B M 3 12 P A6002
		"""
		f = file(FITXER_TMP, "wb")
		f.write(text)
		f.write(";\n")
		f.close()
		classes, horaris = dades.obre(FITXER_TMP)
		self._comprova_classes(classes, text)
		self.assertEqual(tuple(horaris), ())

	def test_obre_classes_i_horaris(self):
		text_classes = """
			A 10 1 8 T A5001
			B M 3 12 P A6002
		"""
		text_horaris = """
			A 10
			A 10 B 20
		"""
		f = file(FITXER_TMP, "wb")
		f.write(text_classes)
		f.write(";\n")
		f.write(text_horaris)
		f.close()
		classes, horaris = dades.obre(FITXER_TMP)
		self._comprova_classes(classes, text_classes)
		self._comprova_horaris(horaris, text_horaris)

	def test_obre_fitxer_inexistent(self):
		fitxer = FITXER_TMP + ".inexistent"
		self.assertRaises(dades.ErrorDades, dades.obre, fitxer)


class TestDesa(unittest.TestCase):

	def tearDown(self):
		try: os.remove(FITXER_TMP)
		except OSError: pass

	def test_desa_fitxer_buit(self):
		dades.desa(FITXER_TMP, ())
		f = file(FITXER_TMP, "r")
		text = f.read()
		f.close()
		self.assertEqual(text, "")

	def test_desa_fitxer_buit_amb_separador(self):
		dades.desa(FITXER_TMP, (), ())
		f = file(FITXER_TMP, "r")
		text = f.read()
		f.close()
		self.assertEqual(text, ";\n")

	def test_desa_classes(self):
		text = "A 10 1 8 T A5001\nB M 3 12 P A6002\n"
		classes = (("A", "10", "1", "8", "T", "A5001"),
			("B", "M", "3", "12", "P", "A6002"))
		dades.desa(FITXER_TMP, classes)
		f = file(FITXER_TMP, "r")
		text_fitxer = f.read()
		f.close()
		self.assertEqual(text, text_fitxer)

	def test_desa_classes_amb_separador(self):
		text = "A 10 1 8 T A5001\nB M 3 12 P A6002\n;\n"
		classes = (("A", "10", "1", "8", "T", "A5001"),
			("B", "M", "3", "12", "P", "A6002"))
		dades.desa(FITXER_TMP, classes, ())
		f = file(FITXER_TMP, "r")
		text_fitxer = f.read()
		f.close()
		self.assertEqual(text, text_fitxer)

	def test_desa_classes_i_horaris(self):
		text = "A 10 1 8 T A5001\nB M 3 12 P A6002\n;\nA 10\nA 10 B 20\n"
		classes = (("A", "10", "1", "8", "T", "A5001"),
			("B", "M", "3", "12", "P", "A6002"))
		horaris = ((("A", "10"),), (("A", "10"), ("B", "20")))
		dades.desa(FITXER_TMP, classes, horaris)
		f = file(FITXER_TMP, "r")
		text_fitxer = f.read()
		f.close()
		self.assertEqual(text, text_fitxer)

	def test_desa_fitxer_incorrecte(self):
		fitxer = FITXER_TMP + "/incorrecte"
		self.assertRaises(dades.ErrorDades, dades.desa, fitxer, ())


class TestObreHttp(unittest.TestCase):

	class Servidor(object):

		URL_ASSIGS="http://localhost:10080/assignatures"
		URL_CLASSES="http://localhost:10080/classes"

		def __init__(self, classes, n_req):
			self.httpd = http.server.HTTPServer(("", 10080), self.RequestHandler)
			self.httpd.classes = classes
			self.httpd.assigs = set([c[0] for c in classes])
			self.lock_aturada = _thread.allocate_lock()
			self.lock_aturada.acquire()
			_thread.start_new_thread(self.serveix, (n_req,))

		def serveix(self, n_req):
			while n_req > 0:
				self.httpd.handle_request()
				n_req -= 1
			self.lock_aturada.release()

		def espera_aturada(self):
			self.lock_aturada.acquire()

		class RequestHandler(http.server.BaseHTTPRequestHandler):
			def do_GET(self):
				error = False
				assigs = self.server.assigs

				if self.path == "/assignatures":
					text = "".join([a + "\n" for a in assigs])
				elif self.path.find("/classes") == 0:
					path = self.path.split("/classes")[1]
					if not path or path[0] != '?': error = True
					r_assigs = set()
					for a in path[1:].split("&"):
						a = a.split("assignatures=")
						if a[0] or a[1] not in assigs: error = True
						r_assigs.add(a[1])
					text = "".join(["\t".join(c) + "\n"
						for c in self.server.classes if c[0] in r_assigs])
				else:
					error=True

				if error:
					self.wfile.write("HTTP/1.0 404 Not Found\n\n")
				else:
					self.wfile.write("HTTP/1.0 200 OK\n\n")
					self.wfile.write(text)


	def _comprova_classes(self, classes1, classes2):
		for c1, c2 in zip(classes1, classes2):
			self.assertEqual(tuple(c1), tuple(c2))

	def setUp(self):
		dades.URL_ASSIGS = self.Servidor.URL_ASSIGS
		dades.URL_CLASSES = self.Servidor.URL_CLASSES

	def test_obre_cap_classe(self):
		servidor = self.Servidor((), 1)
		self._comprova_classes(dades.obre_http(), ())
		servidor.espera_aturada()

	def test_obre_una_classe(self):
		classes = (("A", "10", "1", "8", "T", "A5001"),)
		servidor = self.Servidor(classes, 2)
		self._comprova_classes(dades.obre_http(), classes)
		servidor.espera_aturada()

	def test_obre_diverses_classes(self):
		classes = (("A", "10", "1", "8", "T", "A5001"),
			("A", "11", "3", "12", "P", "A6002"),
			("B", "M", "3", "12", "P", "A6002"))
		servidor = self.Servidor(classes, 2)
		self._comprova_classes(dades.obre_http(), classes)
		servidor.espera_aturada()

	def test_servidor_no_disponible(self):
		self.assertRaises(dades.ErrorDades, dades.obre_http)


if __name__ == '__main__':
	unittest.main()

