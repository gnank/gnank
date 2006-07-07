# -*- coding: UTF-8 -*-

# Gnank - cercador d'horaris de la FIB
# Copyright (C) 2006  Albert Gasset Romo
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# ERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA


import gtk, gobject, pango
import dades, domini, config
from domini import Quadri, Classe, Horari, Cerca
from string import lower
from time import clock
from thread import start_new_thread

class Finestra(gtk.Window):

	_xmlui = """<ui>
				<menubar name="menu">
					<menu action="menu_horaris">
						<menuitem action="actualitza"/>
						<menuitem action="obre"/>
						<separator/>
						<menuitem action="desa"/>
						<separator/>
						<menuitem action="surt"/>
					</menu>
					<menu action="menu_cerca">
						<menuitem action="min_assig_2"/>
						<menuitem action="min_assig_3"/>
						<menuitem action="min_assig_4"/>
						<menuitem action="min_assig_5"/>
						<separator/>
						<menuitem action="max_solap_0"/>
						<menuitem action="max_solap_1"/>
						<menuitem action="max_solap_2"/>
						<menuitem action="max_solap_3"/>
						<menuitem action="max_solap_4"/>
						<separator/>
						<menuitem action="cerca"/>
						<menuitem action="atura"/>
					</menu>
					<menu action="menu_pestanyes">
						<menuitem action="nova_pestanya"/>
						<menuitem action="tanca_pestanya"/>
					</menu>
					<menu action="menu_ajuda">
						<menuitem action="ajuda"/>
						<separator/>
						<menuitem action="quant_a"/>
					</menu>
				</menubar>
				<toolbar name="barra">
					<toolitem action="actualitza"/>
					<toolitem action="obre"/>
					<separator/>
					<toolitem action="cerca"/>
					<toolitem action="atura"/>
					<separator/>
					<toolitem action="nova_pestanya"/>
					<separator/>
					<toolitem action="ajuda"/>
				</toolbar>
				</ui>"""

	def __init__(self):
		gtk.Window.__init__(self)

		self.set_title("Gnank - Cercador d'horaris de la FIB")
		self.set_default_size(800,600)
		icona = config.cami(config.PIXMAPS, config.ICONA)
		if icona: gtk.window_set_default_icon_from_file(icona)

		area_finestra = gtk.VBox()

		accions = Accions(self)
		uimanager = gtk.UIManager()
		uimanager.insert_action_group(accions, 0)
		uimanager.add_ui_from_string(self._xmlui)
		self.add_accel_group(uimanager.get_accel_group())
		menu = uimanager.get_widget('/menu')
		barra = uimanager.get_widget('/barra')
		area_finestra.pack_start(menu, False)
		area_finestra.pack_start(barra, False)

		area_treball = AreaTreball()
		area_finestra.pack_start(area_treball, expand=True, fill=True)

		area_estat = AreaEstat(self)
		area_finestra.pack_start(area_estat, expand=False)

		self.add(area_finestra)

		self.connect('destroy', accions.surt)

		accions.connect('actualitzant-dades', area_estat.actualitzant_dades)
		accions.connect_object('actualitzant-dades',
			area_treball.set_sensitive, False)

		accions.connect('dades-actualitzades', area_treball.actualitza)
		accions.connect('dades-actualitzades', area_estat.dades_actualitzades)
		accions.connect_object('dades-actualitzades',
			area_treball.set_sensitive,	True)

		accions.connect('dades-no-obtingudes', area_estat.dades_no_obtingudes)
		accions.connect_object('dades-no-obtingudes',
			area_treball.set_sensitive,	True)

		accions.connect('dades-desades', area_estat.dades_desades)
		accions.connect('dades-no-desades', area_estat.dades_no_desades)

		accions.connect('cercant-horaris', area_estat.cercant_horaris)
		accions.connect_object('cercant-horaris',
			area_treball.set_sensitive, False)

		accions.connect('cerca-finalitzada', area_treball.actualitza_horaris)
		accions.connect('cerca-finalitzada', area_estat.cerca_finalitzada)
		accions.connect_object('cerca-finalitzada',
			area_treball.set_sensitive,	True)

		accions.connect('nova-pestanya', area_treball.nova_pestanya)
		accions.connect('tanca-pestanya', area_treball.tanca_pestanya)

		area_treball.connect('grups-seleccionats', accions.especifica_grups)
		area_treball.connect('grups-seleccionats', area_estat.grups_seleccionats)
		area_treball.connect('horari-seleccionat', area_estat.horari_seleccionat)
		area_treball.connect('nombre-pestanyes', accions.nombre_pestanyes)

		try:
			dades.obre_cau()
			accions.emit('dades-actualitzades')
		except dades.ErrorCau:
			pass


class Accions(gtk.ActionGroup):
	"""Gestiona de les accions que pot fer l'usuari."""

	_valors_min_assig = range(2, 6)
	_valors_max_solap = range(0, 5)

	@staticmethod
	def _text_min_assig(n):
		return "%d assignatures com a mínim" % n

	@staticmethod
	def _text_max_solap(n):
		if n == 0: return "Sense solapaments"
		if n == 1: return "1 solapament com a màxim"
		if n > 1: return "%d solapaments com a màxim" % n

	__gsignals__ = {
		# Indica l'inici d'una cerca.
		'cercant-horaris': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
		# Indica que la cerca ha finaliitzat.
		'cerca-finalitzada': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
		# Indica l'inici de l'actualització de les dades.
		'actualitzant-dades': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
		# Indica que l'obtenció de dades ha finalitzat.
		'dades-actualitzades': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
		# Indica que l'obtenció de dades ha fallat.
		'dades-no-obtingudes': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
		# Indica que s'han desat les dades.
		'dades-desades': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
		# Indica que no s'han pogut desar les dades.
		'dades-no-desades': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
		# Indica que s'ha de crear una nova pestanya.
		'nova-pestanya': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
		# Indica que s'ha de tanca la pestanya actual.
		'tanca-pestanya': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())

	}

	_ajuda = [ ("Obtenció de les dades",
		"""Es poden obtenir les dades dels horaris des del servidor de la FIB,
		amb l'acció "Actualitza"; o des d'un fitxer, amb l'acció "Obre".
		Podeu desar les dades en un fitxer per poder-les recuperar després,
		en cas que no tingueu accés a Internet, per exemple."""),
		("Selecció de grups",
		"""Seleccioneu els grups dels quals voleu veure l'horari o inclou-re en
		la cerca. No cal que limiteu la selecció al nombre d'assignatures que
		volgeu que tinguin els horaris, la cerca també es realitza amb
		subconjunts de les assignatures triades."""),
		("Cerca d'horaris",
		"""Al menú "Cerca" podeu triar el nombre mínim d'assignatues i el
		nombre màxim de solapaments que volgueu que tinguin el horaris.	Si
		atureu la cerca, es mostraran els horaris trobats fins al moment.
		Si la cerca tarda més de pocs segons, és recomenable que l'atureu
		i seleccioneu uns paràmetres de cerca més restrictius, ja que
		probablement sigui degut a la gran quantitat de solucions que
		s'estan trobant."""),
		("Resultats",
		"""A la llista d'horaris podeu veure i ordenar els horaris segons
		algunes estadístiques, i seleccionar l'horari que volgeu visualitzar
		a la part inferior. Els solapaments són el nombre de classes que us
		perdríeu si triéssiu l'horari. Els fragments són el nombre de blocs
		de classes seguides, són útils per veure quin són els horaris més
		compactats de la llista.""")
	]
		

	def __init__(self, finestra):
		"""Inicialitza les accions."""

		super(Accions, self).__init__("gnank")

		self._finestra = finestra
		self._horaris = []
		self._min_assig = self._valors_min_assig[0]
		self._max_solap = self._valors_max_solap[0]

		self.add_actions([ \
			('menu_horaris', None, "_Horaris", None, None, None),
			('actualitza', gtk.STOCK_REFRESH, "_Actualitza des d'Internet", \
				None, "Actualitza els horaris des del servidor de la FIB",
				self._actualitza_dades),
			('obre', gtk.STOCK_OPEN, "_Obre des d'un fitxer...", None, \
				"Obre els horaris des d'un fitxer", self._obre_dades),
			('desa', gtk.STOCK_SAVE, "_Desa en un fitxer...", None, \
				"Desa els horaris en un fitxer", self._desa_dades),
			('surt', gtk.STOCK_QUIT, None, None, None, self.surt),
			('menu_cerca', None, "_Cerca", None, None, None),
			('cerca', gtk.STOCK_FIND, None, None, None, self._cerca_horaris),
			('atura', gtk.STOCK_STOP, None, None, None, self._atura_cerca),
			('menu_pestanyes', None, "_Pestanyes", None, None, None),
			('nova_pestanya', gtk.STOCK_NEW, "_Nova pestanya", None, None, \
				self._nova_pestanya),
			('tanca_pestanya', gtk.STOCK_CLOSE, "_Tanca la pestanya actual", \
				None, None, self._tanca_pestanya),
			('menu_ajuda', None, "_Ajuda", None, None, None),
			('ajuda', gtk.STOCK_HELP, None, None, None, self._mostra_ajuda),
			('quant_a', gtk.STOCK_ABOUT, None, None, None,
				self._mostra_quant_a) \
		])

		self.get_action('actualitza').set_property('short-label', "Actualitza")
		self.get_action('obre').set_property('short-label', "Obre")
		self.get_action('cerca').set_property('sensitive', False)
		self.get_action('atura').set_property('sensitive', False)
		self.get_action('tanca_pestanya').set_property('sensitive', False)

		accions_min_assig = []
		for i in self._valors_min_assig:
			accions_min_assig.append(('min_assig_%d' % i, None,
				self._text_min_assig(i), None, None, i))
		self.add_radio_actions(accions_min_assig, value=self._min_assig,
			on_change=self._canvi_min_assig)

		accions_max_solap = []
		for i in self._valors_max_solap:
			accions_max_solap.append(('max_solap_%d' % i, None,
				self._text_max_solap(i), None, None, i))
		self.add_radio_actions(accions_max_solap, value=self._max_solap,
			on_change=self._canvi_max_solap)

		self.especifica_grups()

	def especifica_grups(self, arbre=None):
		"""Especifica una seqüència de grups per a les cerques.

		'grups' és una seqüència de tuples (assignatura, grup)."""

		self._grups = []

		if arbre is not None: self._grups = [g for g in arbre.grups()]

		n_assig = len(set([a for a, g in self._grups]))

		accio = self.get_action('cerca')
		accio.set_property('sensitive', n_assig >= self._valors_min_assig[0])

		for i in self._valors_min_assig:
			accio = self.get_action('min_assig_%d' % i)
			accio.set_property('sensitive', i <= n_assig)
	
		n = min(n_assig, self._valors_min_assig[-1])
		n = max(n, self._valors_min_assig[0])
		self.get_action('min_assig_%d' % n).activate()

	def horaris(self):
		"""Iterador sobre els horaris solució."""
		return iter(self._horaris)

	def n_horaris(self):
		"""Nombre d'horaris trobats."""
		return len(self._horaris)

	def surt(self, widget=None):
		"""Surt de l'aplicació."""
		self._atura = True
		gtk.main_quit()	

	def _actualitza_dades(self, widget=None):
		self.get_action('actualitza').set_property('sensitive', False)
		self.get_action('obre').set_property('sensitive', False)
		self.get_action('cerca').set_property('sensitive', False)
		self.emit('actualitzant-dades')
		start_new_thread(self._fil_actualitza_dades, ())

	def _fil_actualitza_dades(self):
		try:
			dades.actualitza()
		except dades.ErrorDades:
			gtk.threads_enter()
			self.emit('dades-no-obtingudes')
		else:
			gtk.threads_enter()
			try: dades.desa_cau()
			except dades.ErrorCau: pass
			self.emit('dades-actualitzades')
		self.get_action('actualitza').set_property('sensitive', True)
		self.get_action('obre').set_property('sensitive', True)
		gtk.threads_leave()

	def _obre_dades(self, widget=None):
		title = "Obre des d'un fitxer..."
		action = gtk.FILE_CHOOSER_ACTION_OPEN
		buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, 
			gtk.RESPONSE_OK)
		dialog = gtk.FileChooserDialog(title, self._finestra, action, buttons)
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			try:
				dades.obre(dialog.get_filename())
				try: dades.desa_cau()
				except dades.ErrorCau: pass
			except dades.ErrorDades:
				dialog.destroy()
				self.emit('dades-no-obtingudes')
			else:
				dialog.destroy()
				self.emit('dades-actualitzades')
		else:
			dialog.destroy()

	def _desa_dades(self, widget=None):
		title = "Desa en un fitxer..."
		action = gtk.FILE_CHOOSER_ACTION_SAVE
		buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, 
			gtk.RESPONSE_OK)
		dialog = gtk.FileChooserDialog(title, self._finestra, action, buttons)
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			try:
				dades.desa(dialog.get_filename())
			except dades.ErrorDades:
				dialog.destroy()
				self.emit('dades-no-desades')
			else:
				dialog.destroy()
				self.emit('dades-desades')
		else:
			dialog.destroy()

	def _cerca_horaris(self, widget=None):
		self.get_action('actualitza').set_property('sensitive', False)
		self.get_action('obre').set_property('sensitive', False)
		self.get_action('cerca').set_property('sensitive', False)
		self.get_action('atura').set_property('sensitive', True)
		self.emit('cercant-horaris')
		cerca = Cerca(self._grups, self._min_assig, self._max_solap)
		self._atura = False
		start_new_thread(self._fil_cerca_horaris, (cerca,))

	def _fil_cerca_horaris(self, cerca):
		self._horaris = []
		for h in cerca.horaris():
			if self._atura: break
			self._horaris.append(h)
		gtk.threads_enter()
		self.get_action('atura').set_property('sensitive', False)
		self.get_action('cerca').set_property('sensitive', True)
		self.get_action('obre').set_property('sensitive', True)
		self.get_action('actualitza').set_property('sensitive', True)	
		self.emit('cerca-finalitzada')
		gtk.threads_leave()

	def _atura_cerca(self, widget=None):
			self._atura = True

	def _mostra_ajuda(self, widget=None):
		title = "Ajuda del Gnank"
		flags = gtk.DIALOG_MODAL
		buttons = (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)
		d = gtk.Dialog(title, self._finestra, flags, buttons)
		d.set_default_size(600,400)
		d.set_icon_name(gtk.STOCK_HELP)
		tb = gtk.TextBuffer()
		tb.create_tag("titol", weight=pango.WEIGHT_BOLD,
			scale=pango.SCALE_LARGE)
		for titol, text in self._ajuda:
			it = tb.get_end_iter()
			tb.insert_with_tags_by_name(it, titol + "\n\n", "titol")
			it = tb.get_end_iter()
			tb.insert(it, " ".join(text.split()) + "\n\n")
		t = gtk.TextView(tb)
		t.set_editable(False)
		t.set_cursor_visible(False)
		t.set_wrap_mode(gtk.WRAP_WORD)
		sw = gtk.ScrolledWindow()
		sw.set_border_width(10)
		sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		sw.add(t)
		sw.show_all()
		d.vbox.pack_start(sw, expand=True, fill=True)
		d.run()
		d.destroy()

	def _mostra_quant_a(self, widget=None):
		d = gtk.AboutDialog()
		d.set_name(config.NOM)
		versio = config.VERSIO
		if not config.LLANCAMENT: versio += "+svn" + config.REVISIO
		d.set_version(versio)
		d.set_copyright(config.COPYRIGHT)
		d.set_comments(config.DESCRIPCIO)
		d.set_license(config.INFO_LLICENCIA)
		d.set_authors(config.AUTORS)
		d.run()
		d.destroy()

	def _canvi_min_assig(self, action, data=None):
		self._min_assig = action.get_current_value()

	def _canvi_max_solap(self, action, data=None):
		self._max_solap = action.get_current_value()

	def _nova_pestanya(self, action, data=None):
		self.emit('nova-pestanya')

	def _tanca_pestanya(self, action, data=None):
		self.emit('tanca-pestanya')

	def nombre_pestanyes(self, area_treball):
		actiu = area_treball.nombre_pestanyes() > 1
		self.get_action('tanca_pestanya').set_property('sensitive', actiu)


class AreaTreball(gtk.Notebook):

	__gsignals__ = {
		# Informa dels grups seleccionats.
		'grups-seleccionats': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
		'horari-seleccionat': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
		'nombre-pestanyes' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
	}

	def __init__(self):
		gtk.Notebook.__init__(self)
		self.set_scrollable(True)
		self.set_show_border(False)
		self._arbres = {}
		self._llistes = {}
		self._num_pestanya = 1
		self.nova_pestanya()

	def nombre_pestanyes(self):
		return self.get_n_pages()

	def nova_pestanya(self, widget=None):
		pestanya = gtk.HBox(spacing=5)
		pestanya.set_border_width(5)

		arbre = ArbreGrups()
		area_arbre = gtk.ScrolledWindow()
		area_arbre.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		area_arbre.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
		area_arbre.add(arbre)
		pestanya.pack_start(area_arbre, expand=False)

		llista = LlistaHoraris()
		area_llista = gtk.ScrolledWindow()
		area_llista.add(llista)
		area_llista.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		area_llista.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

		taula = TaulaHorari()
		area_taula = gtk.ScrolledWindow()
		area_taula.add(taula)
		area_taula.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		area_taula.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

		area_horaris = gtk.VPaned()
		area_horaris.pack1(area_llista, resize=True)
		area_horaris.pack2(area_taula, resize=True)
		pestanya.pack_start(area_horaris, expand=True)

		arbre.connect('grups-seleccionats', self._grups_seleccionats)
		arbre.connect('grups-seleccionats', llista.actualitza_grups)
		llista.connect('horari-seleccionat', self._horari_seleccionat)
		llista.connect('horari-seleccionat', taula.actualitza)

		pestanya.arbre = arbre
		pestanya.llista = llista

		pestanya.show_all()
		num = self.append_page(pestanya)
		self.set_current_page(num)

		etiq_pestanya = gtk.HBox()
		text_pestanya = gtk.Label("Cerca %d " % self._num_pestanya)
		self._num_pestanya += 1
		text_pestanya.show()
		etiq_pestanya.pack_start(text_pestanya)
		boto_pestanya = gtk.Button()
		boto_pestanya.set_relief(gtk.RELIEF_NONE)
		boto_pestanya.set_focus_on_click(False)
		imatge_boto = gtk.Image()
		imatge_boto.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
		imatge_boto.set_size_request(16,16)
		boto_pestanya.set_size_request(20, 20)
		boto_pestanya.add(imatge_boto)
		boto_pestanya.show_all()
		boto_pestanya.connect('clicked', self.tanca_pestanya, pestanya)
		etiq_pestanya.pack_end(boto_pestanya)
		self.set_tab_label(pestanya, etiq_pestanya)

		self.set_show_tabs(self.get_n_pages() > 1)
		self.emit('nombre-pestanyes')

	def tanca_pestanya(self, widget=None, pestanya=None):
		if pestanya is None:
			num = self.get_current_page()
			pestanya = self.get_nth_page(num)
		else:
			num = self.page_num(pestanya)
		self.remove_page(num)
		self.set_show_tabs(self.get_n_pages() > 1)
		self.emit('nombre-pestanyes')

	def actualitza(self, widget=None):
		for num in range(self.get_n_pages()):
			pestanya = self.get_nth_page(num)
			pestanya.arbre.actualitza(widget=widget)

	def actualitza_horaris(self, accions):
		num = self.get_current_page()
		pestanya = self.get_nth_page(num)
		pestanya.llista.actualitza_horaris(accions)

	def grups(self):
		num = self.get_current_page()
		pestanya = self.get_nth_page(num)
		return pestanya.arbre.grups()

	def _grups_seleccionats(self, arbre):
		num = self.get_current_page()
		pestanya = self.get_nth_page(num)
		self.emit('grups-seleccionats')

	def _horari_seleccionat(self, widget=None):
		self.emit('horari-seleccionat')


class ArbreGrups(gtk.TreeView):

	__gsignals__ = {
		# Informa dels grups seleccionats.
		'grups-seleccionats': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
	}

	def __init__(self):
		model = gtk.TreeStore(str, int)
		super(ArbreGrups, self).__init__(model)

		self.set_headers_visible(False)
		self.get_selection().set_mode(gtk.SELECTION_NONE)

		renderer = gtk.CellRendererToggle()
		renderer.set_property('activatable', True)
		renderer.connect('toggled', self._commuta_grup)
		col = gtk.TreeViewColumn('', renderer)
		col.set_cell_data_func(renderer, self._mostra_commutador)
		self.append_column(col)

		renderer = gtk.CellRendererText()
		col = gtk.TreeViewColumn('', renderer, text=0)
		self.append_column(col)

		self._grups = set()
		self.actualitza()

	def actualitza(self, widget=None):
		model = self.get_model()
		model.clear()
		for assig in sorted(Quadri().assignatures()):
			it = model.append(None, [assig, 0])
			for grup in sorted(Quadri().grups(assig)):
				fill = model.append(it, [str(grup), 0])
				if (assig, grup) in self._grups:
					self._selecciona_grup(fill, 1) 
		self.emit('grups-seleccionats')

	def grups(self):
		return iter(self._grups)

	def _commuta_grup(self, renderer, path):
		model = self.get_model()
		it = model.get_iter(path)
		sel = 0
		if model.get_value(it, 1) == 0: sel = 1
		n_fills = model.iter_n_children(it)
		if n_fills == 0:
			self._selecciona_grup(it, sel)
		else:
			for n in range(n_fills):
				fill = model.iter_nth_child(it, n)
				self._selecciona_grup(fill, sel)
		self.emit('grups-seleccionats')

	def _selecciona_grup(self, it, nou_sel):
		model = self.get_model()
		sel = model.get_value(it, 1)
		if nou_sel != sel:
			model.set_value(it, 1, nou_sel)
			pare = model.iter_parent(it)
			sel_pare = model.get_value(pare, 1)
			assig = model.get_value(pare, 0)
			grup = int(model.get_value(it, 0))
			if nou_sel == 0:
				sel_pare -= 1
				self._grups.remove((assig, grup))
			else:
				sel_pare += 1
				self._grups.add((assig, grup))
			model.set_value(pare, 1, sel_pare)

	def _mostra_commutador(self, column, renderer, model, it):
		sel = model.get_value(it, 1)
		renderer.set_active(sel > 0)
		n_fills = model.iter_n_children(it)
		renderer.set_property('inconsistent', sel > 0 and sel < n_fills)


class TaulaHorari(gtk.TreeView):

	_nom_col = ["", "Dilluns", "Dimarts", "Dimecres", "Dijous", "Divendres"]
	_color = ['#822', '#282', '#228', '#882', '#288', '#828']

	def __init__(self):

		model = gtk.ListStore(str, str, str, str, str, str)
		for h in Classe.valors_hora():
			model.append(["%02d:00" % h, "", "", "", "", ""])

		super(TaulaHorari, self).__init__(model)
		self.get_selection().set_mode(gtk.SELECTION_NONE)
		self.set_rules_hint(True)

		for i in range(6):
			render = gtk.CellRendererText()
			render.set_property('xpad', 10)
			render.set_property('ypad', 5)
			render.set_property('xalign', 0.5)
			col = gtk.TreeViewColumn(self._nom_col[i], render, markup=i)
			col.set_alignment(0.5)
			self.append_column(col)

		col = gtk.TreeViewColumn("", gtk.CellRendererText())
		self.append_column(col)

	def actualitza(self, llista):
		model = self.get_model()
		model.clear()
		horari = Horari(llista.grups_horari())
		colors = self._assigna_colors(llista.grups_horari())
		for hora in Classe.valors_hora():
			fila = ["%02d:00" % hora]
			for dia in Classe.valors_dia():
				text_classes = []
				for c in sorted(horari.classes((dia, hora))):
					color = colors.get(c.assig(), "black")
					text = '<span foreground="%s">' % color
					if c.tipus() == 'T':
						text += "%s" % c.assig()
					else:
						text += "%s %s" % (c.tipus().lower(), c.assig().lower())
					text += " %d (%s)</span>" % (c.grup(), c.aula())
					text_classes.append(text)
				fila.append("\n".join(text_classes))
			model.append(fila)

	@classmethod
	def _assigna_colors(cls, grups):
		color = {}
		n = 0
		for a, g in sorted(grups):
			if a not in color and n < len(cls._color):
				color[a] = cls._color[n]
				n += 1
		return color


class LlistaHoraris(gtk.TreeView):

	_nom_col = ["Horari", "", "Hores", "Hores matí", "Hores tarda",
		"Solapaments", "Fragments"]

	__gsignals__ = {
		'horari-seleccionat': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
	}

	def __init__(self):
		super(LlistaHoraris, self).__init__()
		self._grups_arbre = []
		self._grups_horari = []

		renderer = gtk.CellRendererText()
		renderer.set_property('xpad', 10)
		col = gtk.TreeViewColumn(self._nom_col[0], renderer)
		col.set_cell_data_func(renderer, self._mostra_grups)
		col.set_sort_column_id(0)
		self.append_column(col)

		for i in range(2, 7):
			renderer = gtk.CellRendererText()
			renderer.set_property('xpad', 10)
			renderer.set_property('xalign', 0.5)
			col = gtk.TreeViewColumn(self._nom_col[i], renderer, text=i)
			col.set_sort_column_id(i)
			self.append_column(col)

		col = gtk.TreeViewColumn("", gtk.CellRendererText())
		self.append_column(col)
		self.connect('cursor-changed', self._horari_seleccionat)

		self._actualitza_model()

	def actualitza_horaris(self, accions):
		horaris = accions.horaris()
		self._actualitza_model(horaris)

	def actualitza_grups(self, area_treball):
		self._grups_arbre = [g for g in sorted(area_treball.grups())]
		self._actualitza_model()

	def grups_horari(self):
		return iter(self._grups_horari)

	def _actualitza_model(self, horaris=[]):
		model = self.get_model()
		if model is not None: model.clear()
		model = gtk.ListStore(object, bool, int, int, int, int, int)
		model.set_sort_func(0, self._cmp_grups)
		h = Horari(self._grups_arbre)
		model.append([self._grups_arbre, True, h.hores(), h.hores_mati(),
			h.hores_tarda(), h.solapaments(), h.fragments()])
		for h in horaris:
			grups = [g for g in sorted(h.grups())]
			model.append([grups, False, h.hores(), h.hores_mati(),
				h.hores_tarda(), h.solapaments(), h.fragments()])
		self.set_model(model)
		self.set_cursor("0")

	def _horari_seleccionat(self, treeview=None):
		(model, it) = self.get_selection().get_selected()
		self._grups_horari = model.get_value(it, 0)
		self.emit('horari-seleccionat')

	def _mostra_grups(self, column, renderer, model, it):
		grups = model.get_value(it, 0)
		if model.get_value(it, 1) == True: text = "Grups seleccionats"
		else: text = ",  ".join(["%s %d" % (a, g) for a, g in grups])
		renderer.set_property('text', text)

	def _cmp_grups(self, model, it1, it2):
		if model.get_value(it1, 1) == True: return -1
		if model.get_value(it2, 1) == True: return 1
		grups1 = model.get_value(it1, 0)
		grups2 = model.get_value(it2, 0)
		return cmp(grups1, grups2)


class AreaEstat(gtk.HBox):
	def __init__(self, finestra):
		gtk.HBox.__init__(self, spacing=5)
		self._finestra = finestra
		self._estat = gtk.Statusbar()
		self._barra = gtk.ProgressBar()
		self.pack_start(self._barra, expand=False)
		self.pack_start(self._estat, expand=True, fill=True)
		self._cron_barra = None
		self._context_estat = self._estat.get_context_id("Gnank")
		self._temps = 0
		self._atura = True
		self._mostra("Feu clic a \"Actualitza\" per obtenir les dades dels "\
			"horaris d'Internet.")

	def _mou_barra(self):
		self._atura = False
		self._cron_barra = gobject.timeout_add(100, self._cron_barra_cb)

	def _atura_barra(self):
		self._atura = True

	def _cron_barra_cb(self):
		if self._atura:
			self._barra.set_fraction(0.0)
			return False
		self._barra.pulse()
		return True

	def _mostra(self, text=""):
		self._estat.pop(self._context_estat)
		self._estat.push(self._context_estat, text)

	def cercant_horaris(self, widget):
		self._temps = clock()
		self._mostra("S'estan cercant horaris...")
		self._mou_barra()

	def actualitzant_dades(self, widget):
		self._mostra("S'estan obtenint les dades dels horaris...")
		self._mou_barra()

	def dades_actualitzades(self, widget):
		self._mostra("S'han actualitzat les dades dels horaris.")
		self._atura_barra()

	def dades_no_obtingudes(self, widget):
		flags = gtk.DIALOG_MODAL
		dtype = gtk.MESSAGE_ERROR
		buttons = gtk.BUTTONS_OK
		message = "No s'han pogut obtenir les dades dels horaris!"
		d = gtk.MessageDialog(self._finestra, flags, dtype, buttons, message)
		d.run()
		d.destroy()
		self._mostra(message)
		self._atura_barra()

	def dades_desades(self, widget):
		self._mostra("S'han desat les dades dels horaris.")

	def dades_no_desades(self, widget):
		flags = gtk.DIALOG_MODAL
		dtype = gtk.MESSAGE_ERROR
		buttons = gtk.BUTTONS_OK
		message = "No s'han pogut desar les dades dels horaris!"
		d = gtk.MessageDialog(self._finestra, flags, dtype, buttons, message)
		d.run()
		d.destroy()
		self._mostra(message)

	def cerca_finalitzada(self, accions):
		temps = clock() - self._temps
		n_horaris = accions.n_horaris()
		if n_horaris == 0:
			self._mostra("No s'ha trobat cap horari.")
		elif n_horaris == 1:
			self._mostra("S'ha trobat un sol horari.")
		else:
			self._mostra("S'han trobat %d horaris en %1.1f segons." \
				% (n_horaris, temps))
		self._atura_barra()

	def horari_seleccionat(self, widget):
		self._mostra("")

	def grups_seleccionats(self, widget):
		self._mostra("")


if gtk.pygtk_version < (2, 8, 0):
	gobject.type_register(Finestra)
	gobject.type_register(Accions)
	gobject.type_register(AreaTreball)
	gobject.type_register(ArbreGrups)
	gobject.type_register(TaulaHorari)
	gobject.type_register(LlistaHoraris)
	gobject.type_register(AreaEstat)

