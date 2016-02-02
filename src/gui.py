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

import pygtk
pygtk.require('2.0')
import gtk
import gobject
import pango
import webbrowser
import logging
import config
import dades
import domini
from domini import Classe, Horari, Cerca, ErrorDades, ErrorOpcions
from thread import start_new_thread

gtk_versio_2_10 = gtk.check_version(2, 10, 0) is None


def inicia():
    if not gtk_versio_2_10:
        logging.warning("La versió de GTK és inferior a la 2.10.")
    gtk.gdk.threads_init()
    gtk.gdk.threads_enter()
    gtk.about_dialog_set_url_hook(obre_enllac_web)
    f = Finestra()
    f.show()
    try:
        gtk.main()
    except KeyboardInterrupt:
        pass
    gtk.gdk.threads_leave()


def obre_enllac_web(dialog, link):
    try:
        webbrowser.open(link)
    except webbrowser.Error:
        pass


class Finestra(gtk.Window):

    _xmlui = """<ui>
                <toolbar name="barra">
                    <toolitem action="actualitza"/>
                    <toolitem action="obre"/>
                    <toolitem action="desa"/>
                    <separator/>
                    <toolitem action="cerca"/>
                    <toolitem action="neteja"/>
                    <separator/>
                    <toolitem action="mostra-web"/>
                    <toolitem action="imprimeix"/>
                    <separator/>
                    <toolitem action="ajuda"/>
                    <toolitem action="quant_a"/>
                </toolbar>
                </ui>"""

    def __init__(self):
        gtk.Window.__init__(self)

        self.set_title("Gnank - Cercador d'horaris de la FIB")
        self.set_default_size(900, 600)
        icona = config.cami("gnank.png")
        if icona:
            gtk.window_set_default_icon_from_file(icona)

        icona = config.cami('web.png')
        if icona:
            pixbuf = gtk.gdk.pixbuf_new_from_file(icona)
            icon_set = gtk.IconSet(pixbuf)
            icon_factory = gtk.IconFactory()
            icon_factory.add('gnank-web', icon_set)
            icon_factory.add_default()

        area_finestra = gtk.VBox()

        accions = Accions(self)
        uimanager = gtk.UIManager()
        uimanager.insert_action_group(accions, 0)
        uimanager.add_ui_from_string(self._xmlui)
        self.add_accel_group(uimanager.get_accel_group())
        self._uimanager = uimanager

        barra = uimanager.get_widget('/barra')

        area_finestra.pack_start(barra, False)

        area_carrera_align = gtk.Alignment()
        area_carrera_align.set_padding(6, 0, 0, 0)
        area_finestra.pack_start(area_carrera_align, expand=False)

        area_carrera = gtk.HBox()
        area_carrera_align.add(area_carrera)

        carrera = TriaCarrera()
        area_carrera.pack_start(carrera, expand=True, fill=True)

        area_treball = gtk.HPaned()
        area_treball.set_border_width(6)
        area_finestra.pack_start(area_treball, expand=True, fill=True)

        arbre = ArbreGrups()
        area_treball.pack1(arbre, resize=False, shrink=False)

        llista = LlistaHoraris(accions)
        area_llista = gtk.ScrolledWindow()
        area_llista.add(llista)
        area_llista.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        area_llista.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        taula = TaulaHorari()
        area_taula = gtk.ScrolledWindow()
        area_taula.add(taula)
        area_taula.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        area_taula.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        taula.actualitza()

        area_horaris = gtk.VPaned()
        area_horaris.pack1(area_llista, resize=True)
        area_horaris.pack2(area_taula, resize=True)
        area_treball.pack2(area_horaris, resize=True)

        self.add(area_finestra)
        area_finestra.show_all()

        cerca = FinestraCerca(self, llista)

        self.connect('destroy', accions.surt)
        arbre.connect('grups-seleccionats',
            llista.actualitza_grups_seleccionats)
        arbre.connect('grups-seleccionats', cerca.actualitza_grups)
        llista.connect('horari-seleccionat', taula.actualitza)
        accions.connect('dades-actualitzades', carrera.actualitza)
        accions.connect('dades-actualitzades', arbre.actualitza)
        accions.connect('dades-actualitzades', llista.actualitza)
        accions.connect('cerca-horaris', cerca.mostra)
        accions.connect("neteja", llista.actualitza)

        try:
            domini.obre(config.HORARIS_USUARI)
            accions.emit('dades-actualitzades')
        except ErrorDades:
            pass


class Accions(gtk.ActionGroup):
    """Gestiona de les accions que pot fer l'usuari."""

    BASE_URL = "http://www.fib.upc.edu/fib/estudiar-enginyeria-informatica" \
            + "/horaris.html?accio=graella&"

    __gsignals__ = {
        'cerca-horaris': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'dades-actualitzades': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'neteja': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    }

    def __init__(self, finestra):
        """Inicialitza les accions."""

        gtk.ActionGroup.__init__(self, "gnank")

        self.finestra = finestra
        impressio = Impressio(finestra)
        self.ajuda = FinestraAjuda(finestra)
        self._avisar_cau_no_funciona = True

        self.add_actions([
            ('actualitza', gtk.STOCK_REFRESH, "_Actualitza", \
                None, "Actualitza els horaris des del servidor de la FIB",
                self._actualitza_dades),
            ('obre', gtk.STOCK_OPEN, "_Obre", None, \
                "Obre els horaris des d'un fitxer", self._obre_dades),
            ('desa', gtk.STOCK_SAVE, "_Desa", None, \
                "Desa els horaris en un fitxer", self._desa_dades),
            ('cerca', gtk.STOCK_FIND, "_Cerca", None,
                "Cerca combinacions d'horaris", self._cerca_horaris),
            ('neteja', gtk.STOCK_CLEAR, "_Neteja", None,
                "Neteja la llista d'horaris", self._neteja),
            ('imprimeix', gtk.STOCK_PRINT, "_Imprimeix", None,
                "Imprimeix els horaris preferits", impressio.imprimeix),
            ('mostra-web', 'gnank-web', "_Mostra al web", None,
                "Mostra els horaris preferits al web de la FIB",
                self._mostra_web),
        ])

        self.add_toggle_actions([
            ('ajuda', gtk.STOCK_HELP, "A_juda", None, None, self._activa_ajuda),
            ('quant_a', gtk.STOCK_ABOUT, "_Quant a", None, None,
                self._activa_quant_a),
        ])

        if not gtk_versio_2_10:
            self.get_action("imprimeix").set_sensitive(False)

        self.about = gtk.AboutDialog()
        self.about.set_name(config.NOM)
        self.about.set_version(config.VERSIO)
        self.about.set_copyright(config.COPYRIGHT)
        self.about.set_comments(config.DESCRIPCIO)
        self.about.set_license(config.INFO_LLICENCIA)
        self.about.set_authors(config.AUTORS)
        self.about.set_website(config.URL_WEB)
        self.about.connect('response', self._tanca_quant_a)
        self.about.connect('delete-event', self._tanca_quant_a)
        self.ajuda.connect('response', self._tanca_ajuda)
        self.ajuda.connect('delete-event', self._tanca_ajuda)

    def desa_cau_horaris(self):
        config.crea_dir_usuari()
        try:
            domini.desa(config.HORARIS_USUARI)
        except ErrorDades:
            if self._avisar_cau_no_funciona:
                self._avisar_cau_no_funciona = False
                d = gtk.MessageDialog(self.finestra, gtk.DIALOG_MODAL,
                    gtk.MESSAGE_WARNING, gtk.BUTTONS_OK, "No s'han pogut " \
                    "desar els horaris al vostre directori personal.")
                d.format_secondary_text("Si voleu conservar els horaris, " \
                    "haureu de desar-los manualment.")
                d.run()
                d.destroy()

    def surt(self, widget=None):
        gtk.main_quit()

    def _actualitza_dades(self, widget=None):
        FinestraActualitza(self)

    def _obre_dades(self, widget=None):
        title = "Obre des d'un fitxer..."
        action = gtk.FILE_CHOOSER_ACTION_OPEN
        buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN,
            gtk.RESPONSE_OK)
        dialog = gtk.FileChooserDialog(title, self.finestra, action, buttons)
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            try:
                domini.obre(dialog.get_filename())
                self.emit('dades-actualitzades')
            except ErrorDades:
                dialog.destroy()
                message = "No s'han pogut obtenir les dades dels horaris!"
                d = gtk.MessageDialog(self.finestra,  gtk.DIALOG_MODAL,
                        gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, message)
                d.run()
                d.destroy()
            else:
                dialog.destroy()
                self.desa_cau_horaris()
        else:
            dialog.destroy()

    def _desa_dades(self, widget=None):
        title = "Desa en un fitxer..."
        action = gtk.FILE_CHOOSER_ACTION_SAVE
        buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE,
            gtk.RESPONSE_OK)
        dialog = gtk.FileChooserDialog(title, self.finestra, action, buttons)
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            try:
                domini.desa(dialog.get_filename())
            except ErrorDades:
                dialog.destroy()
                message = "No s'han pogut desar les dades dels horaris!"
                d = gtk.MessageDialog(self.finestra, gtk.DIALOG_MODAL,
                        gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, message)
                d.run()
                d.destroy()
            else:
                dialog.destroy()
        else:
            dialog.destroy()

    def _cerca_horaris(self, widget=None):
        self.emit('cerca-horaris')

    def _neteja(self, widget=None):
        self.emit("neteja")

    def _activa_quant_a(self, widget=None):
        if self.get_action("quant_a").get_active():
            self.about.show_all()
        else:
            self.about.hide()

    def _tanca_quant_a(self, widget=None, response=None):
        self.get_action('quant_a').set_active(False)
        return True

    def _activa_ajuda(self, widget=None):
        if self.get_action("ajuda").get_active():
            self.ajuda.show_all()
        else:
            self.ajuda.hide()

    def _tanca_ajuda(self, widget=None, response=None):
        self.get_action('ajuda').set_active(False)
        return True

    def _mostra_web(self, widget=None):
        horaris = domini.horaris_preferits()
        if len(horaris) == 0:
            d = gtk.MessageDialog(self.finestra, gtk.DIALOG_MODAL,
                    gtk.MESSAGE_WARNING, gtk.BUTTONS_OK,
                    "No hi ha horaris preferits per mostrar!")
            d.run()
            d.destroy()
            return
        for horari in horaris:
            params = "&".join("a=%s%%23%s" % (a, g) for a, g in horari)
            obre_enllac_web(None, self.BASE_URL + params)


class TriaCarrera(gtk.HBox):

    __gsignals__ = {
      'canvi-carrera': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
    }

    DESC, CODI = range(0, 2)

    _codiscarrera = dades.CARRERES

    def __init__(self):
        gtk.HBox.__init__(self)
        self._label = gtk.Label("Pla d'estudis:")
        self.pack_start(self._label, expand=False, padding=6)

        self._select = gtk.combo_box_new_text()
        self._select.append_text("Selecciona un pla d'estudis")
        for carrera in self._codiscarrera:
            self._select.append_text(carrera[0])
        self._select.set_active(0)
        self._select.connect("changed", self._actualitza_carrera)
        self.pack_start(self._select, expand=False)

    def _actualitza_carrera(self, widget=None):
        index = self._select.get_active() - 1
        if index in range(0, len(self._codiscarrera)):
            carrera = self._codiscarrera[index][1]
        else:
            carrera = ""
        domini.actualitza_carrera(carrera)

    def actualitza(self, widget=None, grups=None):
        carrera = domini.obte_carrera()
        index = [i for i, v in enumerate(self._codiscarrera) if v[1] == carrera]
        if len(index) > 0:
            self._select.set_active(index[0] + 1)
        else:
            self._select.set_active(0)


class ArbreGrups(gtk.VBox):

    __gsignals__ = {
        'grups-seleccionats': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
            [gobject.TYPE_PYOBJECT]),
    }

    OPCIO_TOTS, OPCIO_MATI, OPCIO_TARDA = range(0, 3)

    def __init__(self):
        gtk.VBox.__init__(self, spacing=6)
        self._inicialitza_opcions()
        self._inicialitza_treeview()
        self._grups_seleccionats = set()
        self.actualitza()

    def _inicialitza_opcions(self):
        self._opcions = gtk.combo_box_new_text()
        self._opcions.append_text("Tots els grups")
        self._opcions.append_text("Grups de matí")
        self._opcions.append_text("Grups de tarda")
        self._opcions.set_active(0)
        self._opcions.connect("changed", self.actualitza)
        self.pack_start(self._opcions, expand=False)

    def _inicialitza_treeview(self):
        model = gtk.TreeStore(str, int)
        self._treeview = gtk.TreeView(model)
        self._treeview.set_headers_visible(False)
        self._treeview.get_selection().set_mode(gtk.SELECTION_NONE)
        if gtk_versio_2_10:
            self._treeview.set_enable_tree_lines(True)
        self._treeview.set_enable_search(True)
        self._treeview.connect("row-activated", self._expandeix)

        renderer = gtk.CellRendererText()
        col = gtk.TreeViewColumn('', renderer, text=0)
        col.set_expand(True)
        self._treeview.append_column(col)

        renderer = gtk.CellRendererToggle()
        renderer.set_property('indicator-size', 14)
        renderer.set_property('activatable', True)
        renderer.connect('toggled', self._commuta_grup_cb)
        col = gtk.TreeViewColumn('', renderer)
        col.set_cell_data_func(renderer, self._mostra_commutador_cb)
        self._treeview.append_column(col)

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        sw.add(self._treeview)
        self.pack_start(sw)

    def actualitza(self, widget=None, grups=None):
        opcio = self._opcions.get_active()
        if opcio == self.OPCIO_TOTS:
            grups_disponibles = domini.grups_disponibles()
        elif opcio == self.OPCIO_MATI:
            grups_disponibles = domini.grups_disponibles_mati()
        elif opcio == self.OPCIO_TARDA:
            grups_disponibles = domini.grups_disponibles_tarda()

        model = self._treeview.get_model()

        assig_expandides = set(it[0] for it in model
            if self._treeview.row_expanded(it.path))

        if grups is None:
            grups_a_seleccionar = self._grups_seleccionats
        else:
            grups_a_seleccionar = grups

        self._grups_seleccionats = set()

        model.clear()
        for assig, grups_assig in grups_disponibles:
            if len(grups_assig) > 0:
                it = model.append(None, [assig, 0])
            for grup in grups_assig:
                fill = model.append(it, [grup, 0])
                if (assig, grup) in grups_a_seleccionar:
                    self._selecciona_grup(fill, 1)
                    self._grups_seleccionats.add((assig, grup))

        for it in model:
            if it[0] in assig_expandides:
                self._treeview.expand_row(it.path, False)

        self.emit('grups-seleccionats', self._grups_seleccionats)

    def _commuta_grup_cb(self, renderer, path):
        model = self._treeview.get_model()
        it = model.get_iter(path)
        sel = 0
        if model.get_value(it, 1) == 0:
            sel = 1
        n_fills = model.iter_n_children(it)
        if n_fills == 0:
            self._selecciona_grup(it, sel)
        else:
            for n in range(n_fills):
                fill = model.iter_nth_child(it, n)
                self._selecciona_grup(fill, sel)
        self.emit('grups-seleccionats', self._grups_seleccionats)

    def _selecciona_grup(self, it, nou_sel):
        model = self._treeview.get_model()
        sel = model.get_value(it, 1)
        if nou_sel != sel:
            model.set_value(it, 1, nou_sel)
            pare = model.iter_parent(it)
            sel_pare = model.get_value(pare, 1)
            assig = model.get_value(pare, 0)
            grup = model.get_value(it, 0)
            if nou_sel == 0:
                sel_pare -= 1
                self._grups_seleccionats.discard((assig, grup))
            else:
                sel_pare += 1
                self._grups_seleccionats.add((assig, grup))
            model.set_value(pare, 1, sel_pare)

    def _mostra_commutador_cb(self, column, renderer, model, it):
        sel = model.get_value(it, 1)
        renderer.set_active(sel > 0)
        n_fills = model.iter_n_children(it)
        renderer.set_property('inconsistent', sel > 0 and sel < n_fills)

    def _expandeix(self, treeview, path, view_column):
        if self._treeview.row_expanded(path):
            self._treeview.collapse_row(path)
        else:
            self._treeview.expand_row(path, False)


def taula_horari(horari):
    colors_disponibles = ['#600', '#060', '#006', '#440', '#044', '#404']
    taula = [["", "<b>Dilluns</b>", "<b>Dimarts</b>", "<b>Dimecres</b>",
        "<b>Dijous</b>", "<b>Divendres</b>"]]

    colors = {}
    for assig in horari.assignatures():
        if not colors_disponibles:
            break
        colors[assig] = colors_disponibles.pop(0)

    for hora in range(horari.primera_hora, horari.ultima_hora + 1):
        fila = ["<b>%02d:00</b>" % hora]
        for dia in Classe.valors_dia:
            text_classes = []
            for c in horari.classes(dia, hora):
                color = colors.get(c.assig, '#022')
                text = '<span foreground="%s">' % color
                if c.tipus == 'T':
                    text += "%s" % c.assig
                else:
                    text += "%s %s" % (c.tipus.lower(), c.assig.lower())
                text += " %s (%s)</span>" % (c.grup, c.aula)
                text_classes.append(text)
            fila.append("\n".join(text_classes))
        taula.append(fila)

    return taula


class TaulaHorari(gtk.TreeView):

    _nom_col = ["", "Dilluns", "Dimarts", "Dimecres", "Dijous", "Divendres"]

    def __init__(self):
        model = gtk.ListStore(str, str, str, str, str, str)

        gtk.TreeView.__init__(self, model)
        self.get_selection().set_mode(gtk.SELECTION_NONE)
        self.set_rules_hint(True)

        for i in range(6):
            render = gtk.CellRendererText()
            render.set_property('xpad', 10)
            render.set_property('ypad', 5)
            col = gtk.TreeViewColumn(self._nom_col[i], render, markup=i)
            col.set_alignment(0.5)
            self.append_column(col)

        col = gtk.TreeViewColumn("", gtk.CellRendererText())
        self.append_column(col)
        self.set_enable_search(False)

    def actualitza(self, llista=None, horari=Horari()):
        model = self.get_model()
        model.clear()
        for fila in taula_horari(horari)[1:]:
            model.append(fila)
        self.columns_autosize()


class LlistaHoraris(gtk.TreeView):
    ''' TODO refactoritzar interaccions amb el model (gtk.ListStore) '''

    _nom_col = ["Horari", "Preferit", "Hores", "Hores matí", "Hores tarda",
        "Solapaments", "Fragments"]

    __gsignals__ = {
        'horari-seleccionat': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
            [gobject.TYPE_PYOBJECT]),
    }

    def __init__(self, accions):
        gtk.TreeView.__init__(self)
        self._accions = accions
        self._mantenir_sel = False

        # Afegeix la columna 0 ('Horari')
        renderer = gtk.CellRendererText()
        renderer.set_property('xpad', 10)
        col = gtk.TreeViewColumn(self._nom_col[0], renderer)
        col.set_cell_data_func(renderer, self._mostra_grups_cb)
        col.set_sort_column_id(0)
        self.append_column(col)

        # Afegeix la columna 1 ('Preferit')
        renderer = gtk.CellRendererToggle()
        renderer.set_property('xpad', 10)
        renderer.set_property('xalign', 0.5)
        renderer.connect("toggled", self._commuta_preferit_cb, 1)
        col = gtk.TreeViewColumn(self._nom_col[1], renderer)
        col.set_cell_data_func(renderer, self._mostra_preferit_cb)
        col.set_sort_column_id(1)
        self.append_column(col)

        # Afegeix la resta de columnes
        for i in range(2, 7):
            renderer = gtk.CellRendererText()
            renderer.set_property('xpad', 10)
            renderer.set_property('xalign', 0.5)
            col = gtk.TreeViewColumn(self._nom_col[i], renderer, text=i)
            col.set_sort_column_id(i)
            self.append_column(col)

        # Afegeix una columna buida al final
        col = gtk.TreeViewColumn("", gtk.CellRendererText())
        self.append_column(col)

        self.connect('cursor-changed', self._horari_seleccionat_cb)

        # Afegir fila 'grups seleccionats'
        # L'última columna del model indica si és la fila 'grups seleccionats'
        model = gtk.ListStore(object, bool, int, int, int, int, int, bool)
        h = Horari()
        model.append([h.grups(), False, h.hores, h.hores_mati, h.hores_tarda,
            h.solapaments, h.fragments, True])

        model.set_sort_func(0, self._cmp_horaris_cb)
        self.set_model(model)
        self._fila_grups_sel = gtk.TreeRowReference(model, (0,))
        self.set_cursor((0,))

        # Opcions TreeView
        self.set_enable_search(False)
        self.set_rules_hint(True)

    def actualitza_grups_seleccionats(self, widget, grups):
        model = self.get_model()

        path_sel = self._fila_grups_sel.get_path()
        if self._mantenir_sel:
            model[path_sel][0] = model[path_sel][0]
        else:
            del model[path_sel]

        path_sel = None
        h = Horari(grups)
        for fila in model:
            if h.grups() == fila[0]:
                path_sel = fila.path
                self._mantenir_sel = True
                break
        else:
            it = model.insert(0, [h.grups(), False, h.hores, h.hores_mati,
                h.hores_tarda, h.solapaments, h.fragments, True])
            path_sel = model.get_path(it)
            self._mantenir_sel = False

        self._fila_grups_sel = gtk.TreeRowReference(model, path_sel)
        self.set_cursor(path_sel)
        self.columns_autosize()

    def actualitza(self, widget=None, horaris=[]):
        grups_seleccionats = self.get_model()[self._fila_grups_sel.get_path()][0]

        # ¿¿ redefineix model en comptes d'obtenir-lo amb self.get_model() ??
        model = gtk.ListStore(object, bool, int, int, int, int, int, bool)
        # utilitzem una funcio de comparació per a ordenar cada columna
        for i in range(0, 7):
            model.set_sort_func(i, self._cmp_horaris_cb, i)

        path_sel = None

        for h in domini.horaris_preferits():
            it = model.append([h.grups(), True, h.hores, h.hores_mati,
                h.hores_tarda, h.solapaments, h.fragments, False])
            if not path_sel and h.grups() == grups_seleccionats:
                path_sel = model.get_path(it)

        for h in horaris:
            if not domini.es_horari_preferit(h.grups()):
                it = model.append([h.grups(), False, h.hores, h.hores_mati,
                    h.hores_tarda, h.solapaments, h.fragments, False])
                if not path_sel and h.grups() == grups_seleccionats:
                    path_sel = model.get_path(it)
                    model.set_value(it, 7, True)

        self._mantenir_sel = path_sel is not None

        if not path_sel:
            h = Horari(grups_seleccionats)
            it = model.insert(0, [h.grups(), False, h.hores, h.hores_mati,
                h.hores_tarda, h.solapaments, h.fragments, True])
            path_sel = model.get_path(it)

        self.set_model(model)
        self._fila_grups_sel = gtk.TreeRowReference(model, path_sel)
        self.set_cursor(path_sel)
        self.columns_autosize()

    def es_fila_grups_seleccionats(self, it):
        model = self.get_model()
        return model.get_value(it, 7)

    def _horari_seleccionat_cb(self, treeview=None):
        (model, it) = self.get_selection().get_selected()
        self.emit('horari-seleccionat', Horari(model.get_value(it, 0)))

    def _mostra_grups_cb(self, column, renderer, model, it):
        path = model.get_path(it)
        horari = model.get_value(it, 0)
        if self._fila_grups_sel and self._fila_grups_sel.get_path() == path:
            text = "Grups seleccionats"
        else:
            text = ",  ".join(["%s %s" % (a, g) for a, g in horari])
        renderer.set_property('text', text)

    def _cmp_horaris_cb(self, model, it1, it2, id):
        # la fila de grups seleccionats ha d'anar a la posició 0, per tant,
        # ens assegurem que vagi sempre abans de l'altra fila comparada

        # en funció de la direcció d'ordenació, hem de posar la fila de grups
        # seleccionats 'al principi' (SORT_ASCENDING) o 'al final' (SORT_DESCENDING)
        sorting = model.get_sort_column_id()[1]

        if self.es_fila_grups_seleccionats(it1):
            result = -1 if sorting == gtk.SORT_ASCENDING else +1
        elif self.es_fila_grups_seleccionats(it2):
            result = +1 if sorting == gtk.SORT_ASCENDING else -1
        else:
            result = cmp(model.get_value(it1, id), model.get_value(it2, id))
        return result

    def _mostra_preferit_cb(self, column, renderer, model, it):
        # la fila de grups seleccionats no es pot marcar com a preferida
        fixed = self.es_fila_grups_seleccionats(it)
        horari = model.get_value(it, 0)
        renderer.set_property('active', not fixed and domini.es_horari_preferit(horari))
        renderer.set_property('activatable', not fixed)
        renderer.set_property('sensitive', not fixed)

    def _commuta_preferit_cb(self, cell, path, col):
        model = self.get_model()
        horari = model[path][0]
        preferit = not model[path][col]
        model[path][col] = preferit
        if preferit:
            domini.afegeix_horari_preferit(horari)
        else:
            domini.elimina_horari_preferit(horari)
        self._accions.desa_cau_horaris()


class FinestraCerca(gtk.Dialog):

    RESPONSE_CERCA = 1
    RESPONSE_ATURA = 2

    def __init__(self, finestra, llista):
        self._finestra = finestra
        self._grups = ()
        self._assigs = ()
        self._llista = llista
        flags = gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT
        buttons = (gtk.STOCK_FIND, self.RESPONSE_CERCA,
            gtk.STOCK_STOP, self.RESPONSE_ATURA,
            gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)
        gtk.Dialog.__init__(self, "Cerca", finestra, flags, buttons)
        self.set_icon_name(gtk.STOCK_FIND)
        self.set_response_sensitive(self.RESPONSE_ATURA, False)
        self.connect('response', self._accio)
        self.connect("delete_event", lambda widget, event: True)
        self.set_has_separator(False)
        self.set_border_width(6)
        self.vbox.set_spacing(12)
        self._prepara_parametres()
        self._prepara_progres()
        self.set_resizable(False)
        self.vbox.show_all()

    def actualitza_grups(self, widget, grups):
        self._grups = tuple(grups)
        self._assigs = tuple(set(assig for assig, grup in grups))
        self._min_assig.set_range(2, len(self._assigs))
        self._min_assig.set_value(len(self._assigs))

    def mostra(self, widget=None):
        if len(self._assigs) < 2:
            d = gtk.MessageDialog(self._finestra, gtk.DIALOG_MODAL,
                    gtk.MESSAGE_WARNING, gtk.BUTTONS_OK,
                    "Heu de seleccionar grups de dues o més assignatures!")
            d.run()
            d.destroy()
            return
        self.show()

    def _prepara_parametres(self):
        l = gtk.Label(u"<big>Paràmetres de cerca</big>")
        l.set_use_markup(True)
        l.set_alignment(0, 0)
        self.vbox.pack_start(l, expand=False)

        table = gtk.Table(2, 2)
        table.set_row_spacings(12)
        table.set_col_spacings(12)

        self._min_assig = gtk.SpinButton()
        self._min_assig.set_increments(1, 1)
        self._min_assig.set_alignment(1.0)
        table.attach(self._min_assig, 1, 2, 0, 1, 0, 0)
        label = gtk.Label("Mínim nombre d'_assignatures:")
        label.set_use_underline(True)
        label.set_alignment(0, 0.5)
        label.set_mnemonic_widget(self._min_assig)
        table.attach(label, 0, 1, 0, 1, gtk.FILL, 0)

        self._max_solap = gtk.SpinButton()
        self._max_solap.set_range(0, 60)
        self._max_solap.set_increments(1, 1)
        self._max_solap.set_value(0)
        self._max_solap.set_alignment(1.0)
        table.attach(self._max_solap, 1, 2, 1, 2, 0, 0)
        label = gtk.Label("Màxim nombre de _solapaments:")
        label.set_use_underline(True)
        label.set_alignment(0, 0.5)
        label.set_mnemonic_widget(self._max_solap)
        table.attach(label, 0, 1, 1, 2, gtk.FILL, 0)

        self.vbox.pack_start(table)

    def _prepara_progres(self):
        self._progres = gtk.ProgressBar()
        self._progres.set_text("Cap cerca realitzada")
        self.vbox.pack_start(self._progres, expand=False)

    def _accio(self, widget, response_id):
        if response_id == self.RESPONSE_CERCA:
            self._inicia_cerca()
        if response_id == self.RESPONSE_ATURA:
            self._atura = True
        if response_id in (gtk.RESPONSE_CLOSE, gtk.RESPONSE_DELETE_EVENT):
            self._atura = True
            self.hide()

    def _inicia_cerca(self):
            self.set_response_sensitive(self.RESPONSE_ATURA, True)
            self.set_response_sensitive(self.RESPONSE_CERCA, False)
            self._min_assig.set_sensitive(False)
            self._max_solap.set_sensitive(False)
            self._cerca = Cerca(self._grups, self._min_assig.get_value(),
                self._max_solap.get_value())
            self._n_horaris = 0
            self._combinacio = 0
            self._n_combinacions = self._cerca.n_combinacions()
            self._atura = False
            gobject.timeout_add(100, self._actualitza_barra_cb)
            self._llista.actualitza(horaris=self._cerca_horaris())
            self.set_response_sensitive(self.RESPONSE_ATURA, False)
            self.set_response_sensitive(self.RESPONSE_CERCA, True)
            self._min_assig.set_sensitive(True)
            self._max_solap.set_sensitive(True)

    def _cerca_horaris(self):
        for h, self._combinacio in self._cerca.horaris():
            self._n_horaris += 1
            if gtk.events_pending():
                gtk.main_iteration(False)
            yield h
            if self._atura:
                break
        else:
            self._atura = True

    def _actualitza_barra_cb(self):
        self._progres.set_text(u"%d horaris trobats" % self._n_horaris)
        if not self._atura:
            f = float(self._combinacio) / self._n_combinacions
            self._progres.set_fraction(f)
            return True
        else:
            self._progres.set_fraction(0.0)
            return False


class FinestraActualitza(gtk.Dialog):

    def __init__(self, accions):
        self._accions = accions
        flags = gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT
        gtk.Dialog.__init__(self, "Actualització", accions.finestra, flags, ())
        self.set_icon_name(gtk.STOCK_REFRESH)
        self.set_has_separator(False)
        self.set_border_width(6)
        self.vbox.set_spacing(12)
        l = gtk.Label(u"<big>S'estan actualitzant les dades...</big>")
        l.set_use_markup(True)
        l.set_alignment(0, 0)
        self.vbox.pack_start(l, expand=False)
        self._progres = gtk.ProgressBar()
        self.vbox.pack_start(self._progres, expand=False)
        self.show_all()
        self._tanca = False
        start_new_thread(self._fil_actualitza_dades, ())

    def _fil_actualitza_dades(self):
        gtk.gdk.threads_enter()
        gobject.timeout_add(100, self._mou_barra)
        gtk.gdk.threads_leave()
        try:
            domini.actualitza()
        except ErrorDades:
            gtk.gdk.threads_enter()
            self.destroy()
            message = "No s'han pogut actualitzar les dades dels horaris!"
            d = gtk.MessageDialog(self._accions.finestra, gtk.DIALOG_MODAL,
                    gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, message)
            d.run()
            d.destroy()
            gtk.gdk.threads_leave()
        except ErrorOpcions:
            gtk.gdk.threads_enter()
            self.destroy()
            message = "Has de seleccionar un pla d'estudis primer!"
            d = gtk.MessageDialog(self._accions.finestra,  gtk.DIALOG_MODAL,
                    gtk.MESSAGE_WARNING, gtk.BUTTONS_OK, message)
            d.run()
            d.destroy()
            gtk.gdk.threads_leave()
        else:
            gtk.gdk.threads_enter()
            self._tanca = True
            self._accions.desa_cau_horaris()
            self._accions.emit("dades-actualitzades")
            gtk.gdk.threads_leave()

    def _mou_barra(self):
        if not self._tanca:
            self._progres.pulse()
            return True
        else:
            self.destroy()
            return False


class ParametresImpressio(object):

    MIDA_FONT = 1.5
    MIDA_MARGE = 0.012
    GRUIX_LINIA = 0.0005

    def __init__(self, ctx):
        self.mida_font = self.MIDA_FONT * ctx.get_width() / ctx.get_dpi_x()
        self.font = pango.FontDescription("sans %d" % int(self.mida_font))
        self.mida_marge = self.MIDA_MARGE * ctx.get_width()
        self.gruix_linia = self.GRUIX_LINIA * ctx.get_width()
        self.amplada_horari = ctx.get_width() - self.mida_marge * 2
        self.amplada_hores = self.amplada_horari / 11
        self.amplada_dies = self.amplada_hores * 2


class HorariImpressio(object):

    def __init__(self, context, taula, capcalera=None):
        self._context = context
        self._params = ParametresImpressio(context)
        self._taula = taula
        self._capcalera = capcalera

    def alcada(self):
        return self._alcada_capcalera() + self._alcada_taula() \
            + self._params.mida_marge * 2

    def _alcada_capcalera(self):
        if not self._capcalera:
            return 0
        return self._alcada_text(self._capcalera, self._params.amplada_horari)

    def _alcada_taula(self):
        if not self._taula:
            return 0
        alcada = 0
        for fila in self._taula:
            alcada += self._alcada_fila(fila)
        return alcada

    def _alcada_fila(self, fila):
        alcada = self._alcada_text(fila[0], self._params.amplada_hores)
        for col in fila[1:]:
            alcada = max(alcada, self._alcada_text(col,
                self._params.amplada_dies))
        return alcada

    def _alcada_text(self, text, amplada):
        amplada -= self._params.mida_marge * 2
        layout = self._crea_pango_layout(text, amplada)
        alcada = float(layout.get_size()[1]) / pango.SCALE
        return alcada + self._params.mida_marge * 2

    def _crea_pango_layout(self, text, amplada):
        layout = self._context.create_pango_layout()
        layout.set_markup(text)
        layout.set_width(int(amplada * pango.SCALE))
        layout.set_font_description(self._params.font)
        layout.set_alignment(pango.ALIGN_CENTER)
        return layout

    def divideix(self, alcada):
        if not self._taula:
            return None

        alcada_div = self.alcada()
        files1 = list(self._taula)
        files2 = []
        while alcada_div > alcada and len(files1) > 0:
            fila = files1.pop()
            files2.insert(0, fila)
            alcada_div -= self._alcada_fila(fila)

        if len(files1) == 0:
            return None

        if len(files2) == 0:
            return (self, None)

        return (HorariImpressio(self._context, files1, self._capcalera),
            HorariImpressio(self._context, files2))

    def dibuixa(self, despl_y):
        x = self._params.mida_marge
        y = despl_y + self._params.mida_marge
        if self._capcalera is not None:
            self._dibuixa_capcalera(x, y)
        self._dibuixa_taula(x, y + self._alcada_capcalera())

    def _dibuixa_capcalera(self, x, y):
        self._dibuixa_linia(x, y, self._params.amplada_horari, 0)
        self._dibuixa_text(self._capcalera, x, y, self._params.amplada_horari)
        alcada = self._alcada_capcalera()
        self._dibuixa_linia(x, y, 0, alcada)
        self._dibuixa_linia(x + self._params.amplada_horari, y, 0, alcada)

    def _dibuixa_taula(self, x, y):
        self._dibuixa_linia(x, y, self._params.amplada_horari, 0)
        z = y
        for fila in self._taula:
            self._dibuixa_fila(fila, x, z)
            z += self._alcada_fila(fila)
        self._dibuixa_linia(x, z, self._params.amplada_horari, 0)

        self._dibuixa_linia(x, y, 0, z - y)
        x += self._params.amplada_hores
        for i in range(0, 5):
            self._dibuixa_linia(x, y, 0, z - y)
            x += self._params.amplada_dies
        self._dibuixa_linia(x, y, 0, z - y)

    def _dibuixa_fila(self, fila, x, y):
        self._dibuixa_linia(x, y, self._params.amplada_horari, 0)
        alcada = self._alcada_fila(fila)
        self._dibuixa_text(fila[0], x, y, self._params.amplada_hores, alcada)
        x += self._params.amplada_hores
        for col in fila[1:]:
            self._dibuixa_text(col, x, y, self._params.amplada_dies, alcada)
            x += self._params.amplada_dies

    def _dibuixa_text(self, text, x, y, amplada, alcada=None):
        amplada -= self._params.mida_marge * 2
        layout = self._crea_pango_layout(text, amplada)
        x += self._params.mida_marge
        if alcada is None:
            y += self._params.mida_marge
        else:
            y += (alcada - float(layout.get_size()[1]) / pango.SCALE) / 2
        cr = self._context.get_cairo_context()
        cr.move_to(x, y)
        cr.show_layout(layout)

    def _dibuixa_linia(self, x, y, amplada, alcada):
        cr = self._context.get_cairo_context()
        cr.set_line_width(self._params.gruix_linia)
        cr.move_to(x, y)
        cr.line_to(x + amplada, y + alcada)
        cr.stroke()


class Impressio(object):

    def __init__(self, finestra):
        self._finestra = finestra
        self._settings = None
        self._page_setup = None
        self._horaris = []
        self._pagines = []

    def imprimeix(self, widget=None):
        if not gtk_versio_2_10:
            return

        if len(domini.horaris_preferits()) == 0:
            d = gtk.MessageDialog(self._finestra, gtk.DIALOG_MODAL,
                    gtk.MESSAGE_WARNING, gtk.BUTTONS_OK,
                    "No hi ha horaris preferits per imprimir!")
            d.run()
            d.destroy()
            return

        po = gtk.PrintOperation()

        if self._settings != None:
            po.set_print_settings(self._settings)

        if self._page_setup != None:
            po.set_default_page_setup(self._page_setup)

        po.connect("begin-print", self._begin_print_cb)
        po.connect("draw-page", self._draw_page_cb)

        res = po.run(gtk.PRINT_OPERATION_ACTION_PRINT_DIALOG, self._finestra)

        if res == gtk.PRINT_OPERATION_RESULT_ERROR:
            d = gtk.MessageDialog(self._finestra, gtk.DIALOG_MODAL,
                    gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                    "S'ha produït un error en imprimir.")
            d.run()
            d.destroy()
        elif res == gtk.PRINT_OPERATION_RESULT_APPLY:
            self._settings = po.get_print_settings()
            self._page_setup = po.get_default_page_setup()

    def _begin_print_cb(self, operation, context):
        alcada_pagina = context.get_height()
        self._pagines = []
        pagina = []
        y = 0
        horaris = [self._horari_impressio(context, h) for h in
            sorted(domini.horaris_preferits(), reverse=True)]

        while len(horaris) > 0:
            horari = horaris.pop()
            alcada_horari = horari.alcada()
            if y + alcada_horari <= alcada_pagina:
                pagina.append(horari)
                y += alcada_horari
            else:
                horari_div = horari.divideix(alcada_pagina)
                if horari_div is None:
                    continue
                self._pagines.append(pagina)
                pagina = [horari_div[0]]
                y = horari_div[0].alcada()
                if horari_div[1]:
                    horaris.append(horari_div[1])

        self._pagines.append(pagina)
        operation.set_n_pages(len(self._pagines))

    def _draw_page_cb(self, operation, context, page_nr):
        y = 0
        for horari in self._pagines[page_nr]:
            horari.dibuixa(y)
            y += horari.alcada()

    def _horari_impressio(self, context, horari):
        taula = taula_horari(horari)
        text = "<big><b>%s</b></big>\n<span size=\"xx-small\">\n</span>" % \
            ",   ".join(["%s %s" % (a, g) for a, g in horari])
        text += "Hores:  %d      " % horari.hores
        text += "Hores matí:  %d      " % horari.hores_mati
        text += "Hores tarda:  %d      " % horari.hores_tarda
        text += "Solapaments:  %d      " % horari.solapaments
        text += "Fragments:  %d" % horari.fragments
        return HorariImpressio(context, taula, text)


class FinestraAjuda(gtk.Dialog):

    def __init__(self, finestra):
        buttons = (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)
        gtk.Dialog.__init__(self, "Ajuda del Gnank", finestra, buttons=buttons)
        self.set_default_size(600, 400)
        self.set_icon_name(gtk.STOCK_HELP)
        self.set_has_separator(False)
        tb = self._prepara_text_buffer()
        t = gtk.TextView(tb)
        t.set_editable(False)
        t.set_cursor_visible(False)
        t.set_wrap_mode(gtk.WRAP_WORD)
        sw = gtk.ScrolledWindow()
        sw.set_border_width(10)
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(t)
        self.vbox.pack_start(sw, expand=True, fill=True)
        self.vbox.show_all()

    def _prepara_text_buffer(self):
        cami = config.cami("ajuda.txt")
        if not cami:
            return
        fitxer = file(cami, "rb")
        tb = gtk.TextBuffer()
        tb.create_tag("titol", weight=pango.WEIGHT_BOLD,
            scale=pango.SCALE_LARGE)

        for linia in fitxer:
            linia = linia.strip()
            if not linia:
                continue
            it = tb.get_end_iter()
            if linia.startswith("*"):
                text = linia[1:].lstrip() + "\n"
                if tb.get_char_count() > 0:
                    text = "\n\n" + text
                tb.insert_with_tags_by_name(it, text, "titol")
            else:
                tb.insert(it, " ".join(linia.split()) + " ")

        fitxer.close()
        it = tb.get_end_iter()
        tb.insert(it, "\n")
        return tb
