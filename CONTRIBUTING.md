GUIA DE CONTRIBUCIÓ
===================

Compilació per a Windows
------------------------

### Requisits:

 * Instal·lar [Python 2.7](https://www.python.org/downloads/release/python-2710/) (versió x86).

 * Instal·lar [PyGTK (all-in-one)](http://ftp.gnome.org/pub/GNOME/binaries/win32/pygtk/2.24/) (versió x86).

 * Instal·lar [py2exe](http://sourceforge.net/projects/py2exe/files/py2exe/).

 * Descarregar i extreure [GTK+ (all-in-one bundle)](http://www.gtk.org/download/win32.php).

### Procés de compilació:

> **ATENCIÓ:** assegurar-se que python.exe és al PATH (l'instal·lador de python ofereix

1. Amb el mòdul py2exe es crea un executable del programa i tots els fitxers
   necessaris per executar-lo. Per fer-ho, des de la carpeta principal del projecte,
   executem la comanda:
   `python .\setup.py py2exe`

   Això crearà dues carpetes, `build` i `dist`. **build** és una carpeta
   temporal que es pot esborrar un cop compilat, **dist** és la carpeta on
   deixarà tots els fitxers compilats, inclós l'executable **gnank.exe**.

2. Afegim a la carpeta `dist` les biblioteques i dependències de GTK+. Per
   fer-ho, anirem a la carpeta on hem extret GTK+ i copiarem les següents
   carpetes a `dist`:

   - bin/
   - etc/
   - lib/gtk-2.0/
   - share/locale/{ca,en,es}
   - share/themes/

   **El _contingut_ de la carpeta `bin/` s'ha de copiar directament a `dist`.**

3. Si tot ha anat bé, podrem executar el gnank des de l'executable **gnank.exe**
   contingut a la carpeta `dist`.

4. Empaquetar la carpeta `dist` en un sol executable mitjançant NSIS i l'script
   de configuració `gnank.nsi` de la carpeta [paquets/win32](paquets/win32).
