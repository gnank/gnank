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

import re
from urllib import urlopen

URL_ASSIGS = "https://raco.fib.upc.edu/api/horaris/assignatures-titulacio.txt?codi="
URL_CLASSES = "https://raco.fib.upc.edu/api/horaris/horari-assignatures.txt"

_ER_CLASSE = re.compile("[^\s]+\s+[^\s]+\s+[0-9]+\s+[0-9]+(:00)?\s+[^\s]+\s+[^\s]+")
_ER_HORARI = re.compile("[^\s]+\s+[^\s]+(\s+[^\s]+\s+[^\s]+)*")

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
        for linia in file(fitxer, "rb"):
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
                horaris.append(zip(linia[::2],linia[1::2]))
            else:
                if not _ER_CLASSE.match(linia):
                    raise ErrorDades
                linia = linia.split()
                linia[3] = linia[3].split(":")[0]
                classes.append(linia)
    except IOError:
        raise ErrorDades

    return carrera, classes, horaris


def desa(fitxer, carrera, classes, horaris = None):
    try:
        f = file(fitxer, "wb")
        f.write(carrera)
        f.write("\n")
        for classe in classes:
            f.write(" ".join(classe))
            f.write("\n")
        if horaris is not None:
            f.write(";\n")
            for horari in horaris:
                f.write(" ".join([a+" "+g for a,g in horari]))
                f.write("\n")
    except IOError:
        raise ErrorDades


def obre_http(carrera):
    classes = []
    try:
        if carrera == "": raise ErrorOpcions

        # obtenim les assignatures
        assigs = [a.strip() for a in urlopen(URL_ASSIGS + carrera)]

        # borrem l'assignatura GRAU-EXAMENS en cas que hi sigui
        assigs = filter (lambda a: a != "GRAU-EXAMENS", assigs)

        if assigs:
            params = "?assignatures=" + "&assignatures=".join(assigs)
            for linia in urlopen(URL_CLASSES + params):
                if not _ER_CLASSE.match(linia):
                    raise ErrorDades
                linia = linia.split()
                linia[3] = linia[3].split(":")[0]
                classes.append(linia)
    except IOError:
        raise ErrorDades
    return classes

