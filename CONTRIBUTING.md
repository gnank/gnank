GUIA DE CONTRIBUCIÓ
===================

Aquesta guia inclou certs aspectes del projecte una mica difícils d'entendre
si tot just comences a remenar amb el Gnank.
Alguns d'aquests aspectes són l'estructura de classes, compilació per a Windows,
i més específics de Git, com ara com fer un _pull request_.

Compilació per a Windows amb py2exe
------------------------------------

### Requisits:

 * Instal·lar Python (recomanat [2.7](http://www.python.org/download/releases/2.7.3/), versió x86)

 * Instal·lar PyGTK:

    - [PyGTK all-in-one](http://ftp.gnome.org/pub/GNOME/binaries/win32/pygtk/2.24/) (inclou PyCairo i PyGObject),

    o

    - [PyGTK](http://ftp.gnome.org/pub/GNOME/binaries/win32/pygtk/2.24/),
    - [PyCairo](http://ftp.gnome.org/pub/GNOME/binaries/win32/pycairo/1.8/),
    - [PyGObject](http://ftp.gnome.org/pub/GNOME/binaries/win32/pygobject/2.28/)

 * Instal·lar [GTK+ all-in-one bundle](http://www.gtk.org/download/win32.php)

 * Instal·lar [py2exe](http://sourceforge.net/projects/py2exe/files/py2exe/)


### Procés de compilació:

> NOTA: assegurar-se que python.exe és al PATH

1. Amb el mòdul py2exe es crea un executable del programa i tots els fitxers
   necessaris per executar-lo.
   Des de la carpeta principal del projecte **gnank**, executem la comanda:
   `python .\setup.py py2exe`

   > Això crearà dues carpetes, `build` i `dist`. **build** és una carpeta
   > temporal que es pot esborrar un cop compilat, **dist** és la carpeta on
   > deixarà tots els fitxers compilats, inclós l'executable **gnank.exe**.

2. Afegim a la carpeta `dist` les biblioteques i dependències de GTK+. Per
   fer-ho, anirem a la carpeta on hem instal·lat GTK+ (per defecte, c:\GTK+),
   i copiarem les següents carpetes a `dist`:

   - bin/
   - etc/
   - lib/gtk-2.0/
   - share/locale/ca/
   - share/themes/

   > El **contingut** de la carpeta **bin/** s'ha de copiar directament a `dist`.
   > La resta de carpetes es copien tal qual deixant la mateixa estructura de
   > carpetes: **dist/etc**, **dist/lib/gtk-2.0**, **dist/share/...**, etc.

   > El paquet GTK+ inclou molts fitxers que no són necessaris i ocupen molt
   > espai, com ara includes, traduccions, etc. Per això només necessitem els
   > especificats més amunt.

3. Si tot ha anat bé, podrem executar el gnank des de l'executable **gnank.exe**
   contingut a la carpeta `dist`.

4. (Opcional) Empaquetar la carpeta `dist` en un sol executable:

   - Mitjançant [NSIS](http://nsis.sourceforge.net/) i l'script de configuració
     `gnank.nsi`
   - Utilitzant un auto-extraïble fet amb WinRAR


Altres instruccions
--------------------

Aquestes són les instruccions originals que em va passar l'Albert Gasset:

 * Amb el mòdul py2exe (http://www.py2exe.org/) creava un executable del
programa i tots els fitxers necessaris de Python. Ho deixa tot al
directori "dist".

 * Després afegia les biblioteques i dependències del GTK+ per a Windows
(http://www.gtk.org/download-windows.html#StableRelease). Aquest paquet
inclou molts fitxers que no són necessaris i que ocupen molt espai
(includes, traduccions, etc.). Crec que els directoris realment
necessaris són: bin, etc, lib/gtk-2.0, share/locale/ca i share/themes.
El contingut del directori bin va directament al directori "dist".

 * Amb això ja hauries de poder executar el gnank.exe del directori
dist.

 * Per empaquetar-ho tot en un sol exe, feia servir l'eina NSIS
(http://nsis.sourceforge.net/). L'script de configuració és gnank.nsi,
que està al SVN del gnank.
