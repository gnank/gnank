Gnank - cercador d'horaris de la FIB
====================================

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


Instruccions d'ús
-----------------

### Windows:

Descarrega [l'última versió](https://github.com/mcornella/gnank/releases) i
executa sense haver d'instal·lar cap requisit.

### Linux:

Un cop [instal·lats els requisits](#requisits-de-software), executar el fitxer [src/gnank](src/gnank):

 - Des del terminal: `src/gnank`

 - Des de l'explorador de fitxers: _doble clic_ > _executar_

### Mac OSX:

No s'ha pogut provar per falta de maquinari compatible. En principi hauria de
funcionar correctament seguint les instruccions per Linux.


Requisits de software
---------------------

Gnank requereix el següent software:

 * Python 2 >= 2.4 (www.python.org)
 * PyGTK >= 2.8 (www.pygtk.org), >= 2.10 per a imprimir horaris

En una instal·lació típica basada en Debian (com ara Ubuntu, Knoppix, etc.),
els noms dels paquets que s'han de tenir instal·lats són:

 * python2
 * python-gtk2


Crèdits
-------

Creador: Albert Gasset Romo
Copyright © 2006 - 2007

Mantenidor actual: Marc Cornellà
Copyright © 2011 - 2015

Distribuït sota la llicència General Public License v3 (veure arxiu [LICENSE](LICENSE.txt)).
