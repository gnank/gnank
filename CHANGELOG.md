Gnank 3.3.2 (2018-02-12)
------------------------

* Afegit hack a la crida a l'API d'horaris per evitar errors 404.
* Exclusió d'algunes DLLs de Windows 10 per arreglar la compilació.

Gnank 3.3.1 (2016-02-03)
------------------------

 * Incorporats màsters nous i en procés d'extinció:
   - Master in Data Mining and Knowledge Management (DKDM).
   - Màster en Computació (2006 i 2009).
   - Màster en Intel·ligència Artificial (2006 i 2009).
   - Màster en Tecnologies de la Informació (2006 i 2009).
 * Afegeix un marge a la barra de tasques per mantenir la simetria.
 * Deixa d'utilitzar el mòdul `psyco`. No tenia un guany perceptible.
 * Corregit el fitxer de compilació per a Windows 7.
 * Automatització total de la creació de l'executable per Linux.
 * Simplificació de la documentació.

Gnank 3.3 (2015-07-17)
------------------------

 * Utilitza la nova API del Racó.
 * Incorporats els màsters:
   - Master in Artificial Intelligence (MAI).
   - Master in Innovation and Research in Informatics (MIRI).
   - Master in Information Technology for Business Intelligence (IT4BI).
 * La fila 'grups seleccionats' ja no es mou en ordenar els horaris.
 * Simplificació de l'estructura del projecte.
 * Simplificació de la compilació per a Windows.

Gnank 3.2.2 (2012-09-01)
------------------------

 * Incorporat el Màster en Enginyeria Informàtica (MEI).

Gnank 3.2.1 (2012-07-10)
------------------------

 * Solucionat error en la tria de grups de tarda.

Gnank 3.2 (2012-02-22)
------------------------

 * Inclosa la opció per seleccionar la Carrera.
 * La carrera seleccionada també es guarda a la configuració del Gnank.
 * Testejada la compatibilitat amb configuracions de versions anteriors.
 * El tamany de la barra lateral de les assignatures es pot canviar.
 * Fitxer de relació Pla d'estudis - Codi canviat a codis.txt.

Gnank 3.1 (2011-07-08)
------------------------

 * Adaptació al nou sistema de consulta amb codis per Carrera
   (veure CodiAssigs.txt).
 * En properes versions s'inclourà la opció a la GUI.
 * Corregit error en obrir el fitxer de log.

Gnank 3.0.1 (2011-02-02)
------------------------

 * Adaptació als horaris de les assignatures de Grau.

Gnank 2.0.1 (2007-07-12)
------------------------

 * Corregits errors ortogràfics de la interfície gràfica.
 * Corregit error d'actualització d'horaris.
 * Corregit error en les proves d'actualització d'horaris.
 * Distribuït sota la llicència GPL versió 3.

Gnank 2.0 (2007-02-05)
----------------------

 * Interfície simplificada i amb millores d'usabilitat.
 * Horaris preferits. Es poden indicar quins horaris són preferits, per tal
   que es mantinguin a la llista d'horaris i es desin amb les dades.
 * Selector de tots els grups, grups de matí o grups de tarda.
 * Impressió dels horaris preferits.
 * Suport per a Windows.

Gnank 1.1 (2006-07-12)
----------------------

 * Es pot treballar amb diverses cerques a la vegada amb l'ús de pestanyes.
 * Les cerques realitzades es desen juntament amb els horaris en obrir/desar.
 * Manté una cau al directori personal de l'usuairi amb els horaris i les
   cerques realitzades, que es recuperen automàticament en iniciar l'aplicació.
 * Suport per a grups de Màster.


Gnank 1.0 (2006-02-13)
----------------------

Característiques:
 * Obtenció de les dades dels horaris del servidor de la FIB.
 * Permet obrir i desar les dades dels horaris en un fitxer (per poder
   utilitzar el programa sense connexió a Internet).
 * Cerca d'horaris amb un nombre mínim d'assignatures i un nombre màxim de
   solapaments, a partir d'uns grups seleccionats.
 * Interfície que permet seleccionar els grups i visualitzar els horaris de
   forma senzilla i ràpida.
