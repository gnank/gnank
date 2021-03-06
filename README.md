Gnank
=====

<a href="https://cloud.githubusercontent.com/assets/1441704/8757859/5c21fc16-2cde-11e5-8718-d0b9daaeecce.png"><img src="https://cloud.githubusercontent.com/assets/1441704/8757859/5c21fc16-2cde-11e5-8718-d0b9daaeecce.png" width="430" height="300"></a>
<a href="https://cloud.githubusercontent.com/assets/1441704/8761748/afa1389c-2d61-11e5-9f73-ad480367c77b.png"><img src="https://cloud.githubusercontent.com/assets/1441704/8761748/afa1389c-2d61-11e5-9f73-ad480367c77b.png" width="430" height="300"></a>

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

Descarrega i executa [l'última versió](https://github.com/mcornella/gnank/releases/latest)
sense necessitat d'instal·lar cap requisit.

### Linux:

Un cop [instal·lats els requisits](#requisits-de-programari), es pot utilitzar de dues formes:

- Mitjançant l'executable:

  1. Descarrega [`gnank.sh`](https://github.com/mcornella/gnank/releases/latest).

  2. Activa el permís d'execució del fitxer: `chmod +x gnank.sh`

  3. Executa mitjançant la comanda `./gnank.sh`.

  4. (Opcional) Recomano moure l'arxiu en una carpeta del `$PATH` per poder executar
     el Gnank amb `ALT`+`F2` > `gnank.sh` directament.

- Mitjançant la distribució sencera:

  1. Descarrega i descomprimeix el `tar.gz` de [l'última versió](https://github.com/mcornella/gnank/releases/latest).

  2. Des del terminal, navega a l'arrel del projecte i executa `src/main.py`.

### Mac OSX:

No s'ha pogut provar per falta de maquinari compatible. En principi hauria de
funcionar correctament seguint les instruccions per Linux.


Requisits de programari
-----------------------

El Gnank requereix el següent programari:

 * Python 3 (https://www.python.org/)
 * PyGObject (https://pygobject.readthedocs.io/en/latest/getting_started.html)

En una instal·lació típica basada en Debian (com ara Ubuntu, Knoppix, etc.),
els noms dels paquets que s'han de tenir instal·lats són:

 * gtk3
 * python3
 * python3-gi (o python3-gobject)


Crèdits
-------

- **Creador:** Albert Gasset Romo
  Copyright © 2006 - 2007

- **Paquet Debian i pedaços:** Jordà Polo
  Copyright © 2006 - 2007

- **Programador actual:** Marc Cornellà
  Copyright © 2011 - 2019

Distribuït sota la llicència General Public License v3 (veure arxiu [LICENSE](LICENSE.txt)).
