# -*- coding: utf-8 -*-

# Gnank - cercador d'horaris de la FIB
# Copyright (C) 2006 - 2007  Albert Gasset Romo
#               2011 - 2016  Marc Cornellà
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


import sys
import os
from os.path import dirname, join
import logging
from traceback import format_exception


FORMAT_REGISTRE = '%(asctime)s %(levelname)-8s %(message)s'


def configura_registre():
    logger = logging.getLogger("")
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.WARNING)
    handler.setFormatter(logging.Formatter(FORMAT_REGISTRE))
    logger.addHandler(handler)


def configura_registre_fitxer(fitxer):
    try:
        handler = logging.FileHandler(fitxer)
    except IOError as e:
        logging.warning("Error en obrir el registre: %s", e)
    else:
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter(FORMAT_REGISTRE))
        logging.getLogger("").addHandler(handler)


def registra_excepcio(type, value, tb):
    text = "".join(format_exception(type, value, tb))
    logging.error("S'ha produït una excepció.\n%s", text)


def main(gnank_dir):
    configura_registre()
    sys.excepthook = registra_excepcio

    import config
    config.gnank_dir = gnank_dir
    config.crea_dir_usuari()
    configura_registre_fitxer(config.REGISTRE_USUARI)

    logging.info("S'iniciarà l'aplicació.")
    import gui
    gui.inicia()
    logging.info("Es tancarà l'aplicació.")

    logging.shutdown()
