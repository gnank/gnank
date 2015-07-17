Gnank - cercador d'horaris de la FIB
====================================

Creador: Albert Gasset Romo
Copyright © 2006 - 2007

Mantenidor actual: Marc Cornellà
Copyright © 2011 - 2015

Distribuït sota la llicència General Public License v3 (veure arxiu [LICENSE](LICENSE.txt)).


Presentació
-----------

El Gnank és un programa creat amb l'objectiu de facilitar la tria de l'horari
als alumnes de la FIB.

Característiques:

 * Interfície que permet seleccionar els grups i visualitzar els horaris de
   forma senzilla i ràpida.

 * Actualització de les dades dels horaris del servidor de la FIB.

 * Cerca d'horaris amb un nombre mínim d'assignatures i un nombre màxim de
   solapaments, a partir d'uns grups seleccionats.

 * Possibilitat d'indicar horaris preferits que es volen recordar, i opció
   per a imprimir-los.

 * Obre i desa els horaris automàticament al directori personal de l'usuari,
   però també és possible obrir i desar els horaris en un fitxer específic.


Requisits de programari
-----------------------

**Per a utilitzar sense instal·lació al Windows no hi ha cap requisit! Veure [Ús sense instal·lació](#windows)**

Per a poder instal·lar i executar el programa necessiteu tenir instal·lat el
següent programari:

 * Python2 >= 2.4 (www.python.org)
 * PyGTK >= 2.8 (www.pygtk.org), >= 2.10 per a imprimir horaris

En una instal·lació típica basada en Debian (com ara Ubuntu, Knoppix, etc.),
els noms dels paquets que s'han de tenir instal·lats són:

 * python
 * python-gtk2

Opcionalment, si està instal·lat el Psyco, una extensió que millorar el rendiment
d'execució de codi Python, el Gnank l'utilitzarà.

 * python-psyco


Instruccions d'ús
------------------------------

### Linux:

Es pot executar el programa sense haver d'instal·lar-lo. Només cal executar el
fitxer [src/gnank](src/gnank), que es troba al directori arrel de la distribució:

`src/gnank` (o des de nautilus o qualsevol altre explorador: doble clic > executar)


### Windows:

Es pot executar mitjançant l'executable inclòs al zip, `gnank.exe`. Es tracta
d'un auto-extraïble generat amb WinRAR (no en sé més :P).
Descarrega directament [l'última versió](https://github.com/mcornella/gnank/releases).


### Mac OS X:

No s'ha pogut provar per falta de maquinari compatible. S'agrairà qualsevol
feedback, però en principi hauria de funcionar correctament seguint les
instruccions per Linux (amb els requisits de Python instal·lats).
