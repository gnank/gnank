Gnank - cercador d'horaris de la FIB
====================================

Creador: Albert Gasset Romo (albert.gasset@gmail.com)
Copyright © 2006, 2007

Adaptació al Grau i plans d'estudis recents amb l'autorització del creador:
Marc Cornellà (marc.cornella@est.fib.upc.edu) 2011-2013

Distribuït sota la llicència General Public License, veure el fitxer [GPL.txt](blob/master/GPL.txt)

Pàgina web del projecte: http://lafarga.cpl.upc.edu/projectes/gnank-reloaded


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


Utilització sense instal·lació
------------------------------

### Linux:

Es pot executar el programa sense haver d'instal·lar-lo. Només cal executar el
fitxer [gnank.sh](blob/master/gnank.sh), que es troba al directori arrel de la distribució:

`./gnank.sh` (o des de nautilus o qualsevol altre explorador: doble clic > executar)


### Windows:

Es pot executar mitjançant l'executable inclòs al zip, `gnank.exe`. Es tracta
d'un auto-extraïble generat amb WinRAR (no en sé més :P)


### Mac OS X:

No s'ha pogut provar per falta de maquinari compatible. S'agrairà qualsevol
feedback, però en principi hauria de funcionar correctament seguint les
instruccions per Linux (amb els requisits de Python instal·lats).


Instal·lació (Linux)
--------------------

El programa utilitza les eines _Python Distutils_ per a instal·lar-se. Simplement
cal executar la següent ordre des de la carpeta arrel de la distribució de Gnank
amb privilegis d'administrador:

`./setup.py install`

Un cop instal·lat, podeu executar-lo des del menú del vostre escriptori o amb
l'ordre `gnank`.

Si voleu més informació de com instal·lar programes amb Distutils mireu a
http://www.python.org/doc/current/inst/.


Desinstal·lació (Linux)
-----------------------

Actualment "Distutils" no permet desinstal·lar programes, si voleu desinstal·lar
el Gnank heu de fer-ho manualment. Només cal que elimineu els següents fitxers
i directoris:

```
/usr/bin/gnank
/usr/share/applications/gnank.desktop
/usr/share/doc/gnank/
/usr/share/gnank/
/usr/share/pixmaps/gnank.png
```


Referència de codis de pla d'estudis
------------------------------------

Aquests codis s'utilitzen per consultar a la API del Racó les assignatures d'un
pla d'estudis. Exemple: https://raco.fib.upc.edu/api/horaris/assignatures-titulacio.txt?codi=GRAU

De la documentació de la API del Racó:

> Retorna les sigles de les assignatures d'una titulació que tenen horari. Els
> possibles codis son: MTI GRAU EI03 ETG03 ETS03 MC MIA CANS EMDC

Aquests són els codis que utilitza el Gnank, i per tant els plans d'estudis suportats:

- **_GRAU_**
  Grau en Enginyeria Informàtica

**Pla 2003**

- **_EI03_**
  Eng. Informàtica Superior
- **_ETS03_**
  Eng. Tècnica de Sistemes
- **_ETG03_**
  Eng. Tècnica de Gestió

### Màsters

- **_MEI_**
  Màster en Enginyeria Informàtica
- **_EMDC_**
  Erasmus Mundus in Distributed Computing

**Pla 2006**

- **_MTI_**
  Màster en Tecnologies de la Informació
- **_CANS_**
  Computer Architecture, Networks and Systems
- **_MC_**
  Màster en Computació
- **_MIA_**
  Màster en Intel·ligència Artifical

Suposadament hi ha més codis disponibles, com ara **MEI** que correspon al _Màster
en Enginyeria Informàtica_. Si es dóna el cas i no està incorporat al Gnank,
feu-m'ho saber afegint un ticket (apart [Issues](issues)); també podeu fer el canvi vosaltres
mateixos i fer un _pull request_.
