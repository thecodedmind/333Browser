import tkinter
from tkinter import ttk, messagebox
import json
from functools import partial
import dataclasses
import os
from contextlib import suppress
from triple import get_server_list, get_server_info

server_cache = {}
cur_selection = {}
cur_selection_id = ""
scriptdir = os.path.dirname(os.path.abspath(__file__))+"/"
tgui = None
autorefresh = False

def getConfig(parent="", key="", *, filename="config"):
	with open(scriptdir+filename+".json") as f:
		data = json.load(f)
		
		if parent == "" and key == "":
			return data
		else:
			try:
				if key == "":
					return data[parent]
				else:
					return data[parent][key]
			except:
				return "NO_CONFIG_KEY"

def setConfig(parent:str, key:str, value, *, filename="config", logging=False):
	if logging:
		AddLog(f"{parent} : {key} : {value}")
	data = getConfig(filename=filename)
	try:
		data[parent][key] = value
	except:
		data[parent] = {}
		data[parent][key] = value
	with open(scriptdir+filename+'.json', "w") as s:
		json.dump(data, s, indent=4)

def dumpConfig(data, filename="config"):
	with open(scriptdir+filename+'.json', "w") as s:
		json.dump(data, s, indent=4)

def touchConfig(parent:str, key:str, default, *, filename="config"):
	with open(scriptdir+filename+".json") as f:
		data = json.load(f)
		try:
			return data[parent][key]
		except:
			setConfig(parent, key, default, filename=filename)
			return default
		
def onselect(evt):
	cur = tgui.servers.focus()
	if cur == "":
		return
	#print(tgui.servers.item(cur))
	cur_selection = tgui.servers.item(cur)
	cur_selection_id = cur
	if touchConfig('core', 'autorefresh', False):
		tgui.server_info.delete(0, 'end')	
		try:
			cached = server_cache[cur]
			print("In cache")
			#print(server_cache)
		except KeyError:
			data = get_server_info(cur)
			print(data)
			print("caching")
			server = {}
			with suppress(KeyError):
				server['name'] = data['hostname']
				server['maptitle'] = data['maptitle']
				server['mapname'] = data['mapname']
				server['maxplayers'] = data['maxplayers']
				server['mutators'] = data['mutators']
				server['numplayers'] = data['numplayers']
				server['country'] = data['country']
				server['gametype'] = data['gametype']
				server['adminname'] = data['adminname']
				server['adminemail'] = data['adminemail']
				server['password'] = data['password']
				
				server['players'] = []
				if data['numplayers'] > 0:
					for item in data.keys():
						if item.startswith('player_'):
							player = {}
							player['name'] = data[item]['player']
							player['ping'] = data[item]['ping']
							player['mesh'] = data[item]['mesh']
							player['team'] = data[item]['team']
							player['frags'] = data[item]['frags']
							server['players'].append(player)
							print(data[item])
				server_cache[cur] = server
				cached = server
		
		print(cached)
		if cached:
			tgui.server_info.delete(0, "end")
			tgui.players.delete(0, "end")
			tgui.server_info.insert('end', '[MUTATORS]')
			tgui.server_info.insert('end', cached['mutators'])
			tgui.server_info.insert('end', '[ADMIN]')
			tgui.server_info.insert('end', cached['adminname'] or "None")
			tgui.server_info.insert('end', '[EMAIL]')
			tgui.server_info.insert('end', cached['adminemail'] or "None")
			tgui.server_info.insert('end', '[PASSWORDED]')
			tgui.server_info.insert('end', cached['password'] or "False")
			tgui.server_info.insert('end', '[COUNTRY]')
			tgui.server_info.insert('end', cached['country'] or "N/A")
			if len(cached['players']) > 0:
				for item in cached['players']:
					tgui.players.insert('end', f"Name: {item['name']}")
					tgui.players.insert('end', f"Ping: {item['ping']}")
					tgui.players.insert('end', f"Class: {item['mesh']}")
					tgui.players.insert('end', f"Team: {item['team']}")
					tgui.players.insert('end', f"Frags: {item['frags']}")
					tgui.players.insert('end', "")
def config_window():
	w = tkinter.Tk()
	w.title(f"Config ({tgui.mainwin.winfo_width()}x{tgui.mainwin.winfo_height()})")
	
	label_size = tkinter.Label(w, text="Window Size: ").grid(row=0, column=0)
	entry_size = tkinter.Entry(w)
	entry_size.grid(row=0, column=1)
	entry_size.insert(0, touchConfig('core', 'geometry', '850x360'))
	label_game = tkinter.Label(w, text="Default Game: ").grid(row=1, column=0)
	entry_game = tkinter.Entry(w)
	entry_game.grid(row=1, column=1)
	entry_game.insert(0, touchConfig('core', 'game', 'all'))
	label_launcher = tkinter.Label(w, text="Game Directory: ").grid(row=2, column=0)
	entry_launcher = tkinter.Entry(w)
	entry_launcher.grid(row=2, column=1)
	entry_launcher.insert(0, touchConfig('core', 'launcher', ''))
	cfgsave = partial(push_cfg, entry_size, entry_game, entry_launcher)
	tkinter.Button(w, text="Save", command=cfgsave).grid(row=99, column=0, sticky="w")
	tkinter.Button(w, text="Clear Game History", command=clrhist).grid(row=99, column=1, sticky="w")

def clrhist():
	if not tkinter.messagebox.askokcancel(message=f"Delete games history?"):
		return
	
	setConfig('core', 'history', [])
	tgui.games_history['menu'].delete(0, 'end')
	
def push_cfg(size, game, launcher):
	print(size.get())
	touchConfig('core', 'geometry', '850x360')
	setConfig('core', 'geometry', size.get())
	print(game.get())
	touchConfig('core', 'game', 'all')
	setConfig('core', 'game', game.get())
	print(launcher.get())
	touchConfig('core', 'launcher', '')
	setConfig('core', 'launcher', launcher.get())
	
def refresh_list():
	print(tgui.entry_game.get())
	print(tgui.entry_search.get())
	print(tgui.selected_game_history.get())
	
	hist = touchConfig('core', 'history', [])
	if tgui.entry_game.get() not in hist:
		hist.append(tgui.entry_game.get())
		setConfig('core', 'history', hist)
		#tgui.games_history['menu'].add_command(label=tgui.entry_game.get(), command=lambda: tgui.selected_game_history.set(tgui.entry_game.get()))
		hsc = partial(set_history, tgui.entry_game.get())
		tgui.games_history['menu'].add_command(label=tgui.entry_game.get(), command=hsc)	
		
	tgui.servers.delete(*tgui.servers.get_children())
	data = get_server_list(tgui.entry_game.get(), q=tgui.entry_search.get())
	print(data)
	if len(data[0]) >= 1:
		for item in data[0]:
			add_server(f"{item['ip']}:{item['hostport']}", item['hostname'], f"{item['ip']}:{item['hostport']}", f"{item['numplayers']}/{item['maxplayers']}", f"{item['mapname']} ({item['maptitle']})", item['gametype'])
			
def add_server(sid, name, host, players, mapname, game):
	tgui.servers.insert("", "end", sid, text=name, values=[host, players, mapname, game])

def command_server_query():
	autorefresh = getConfig()['core']['autorefresh']
	if autorefresh:
		setConfig('core', 'autorefresh', False)
	else:
		setConfig('core', 'autorefresh', True)

def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    l.sort(reverse=reverse)

    # rearrange items in sorted positions
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    # reverse sort next time
    tv.heading(col, command=lambda: \
               treeview_sort_column(tv, col, not reverse))

def set_history(game):
	tgui.entry_game.delete(0, 'end')
	tgui.entry_game.insert(0, game)
	
class server_gui:
	def __init__(self):
		self.mainwin = tkinter.Tk()
		self.mainwin.geometry(touchConfig('core', 'geometry', '850x360'))
		self.mainwin.title("333networks Browser")
		
		self.frame1 = tkinter.Frame(self.mainwin)
		self.frame1.pack(fill="both")
		refresh_button = tkinter.Button(self.frame1, text="Refresh", command=refresh_list)
		refresh_button.pack(side="right", fill="x", expand=True)
		config_button = tkinter.Button(self.frame1, text="Config", command=config_window)
		config_button.pack(side="right", fill="x", expand=True)
		config_button = tkinter.Button(self.frame1, text="Join", state="disabled")
		config_button.pack(side="right", fill="x", expand=True)
		
		self.frame2 = tkinter.Frame(self.mainwin)
		self.frame2.pack(fill="both")
		label_game = tkinter.Label(self.frame2, text="Game: ").grid(row=0, column=0)
		self.entry_game = tkinter.Entry(self.frame2)
		self.entry_game.grid(row=0, column=1)
		self.entry_game.insert('0', touchConfig('core', 'game', 'all'))
		
		self.games_history_list = [""]
		self.selected_game_history = tkinter.StringVar(self.frame2)
		self.games_history = tkinter.OptionMenu(self.frame2, self.selected_game_history, *self.games_history_list)
		self.games_history.grid(row=0, column=2)
		self.games_history['menu'].delete(0)
		hsc = partial(set_history, "")
		self.games_history['menu'].add_command(label="[CLEAR]", command=hsc)
		
		hist = touchConfig('core', 'history', [])
		if len(hist) > 0:
			for item in hist:
				#self.games_history['menu'].add_command(label=item, command=lambda: self.selected_game_history.set(item))
				hsc = partial(set_history, item)
				self.games_history['menu'].add_command(label=item, command=hsc)
		label_search = tkinter.Label(self.frame2, text="Search: ").grid(row=0, column=3)
		self.entry_search = tkinter.Entry(self.frame2)
		self.entry_search.grid(row=0, column=4)
		self.entry_search.insert('0', touchConfig('core', 'search', ''))
		
		self.check_server_query = tkinter.Checkbutton(self.frame2, text="Auto-load Server details on click", command=command_server_query)
		self.check_server_query.grid(row=0, column=5)
		autorefresh = touchConfig('core', 'autorefresh', False)
		if autorefresh:
			self.check_server_query.select()
		
		self.frame3 = tkinter.Frame(self.mainwin)
		self.frame3.pack(fill="both", side="left")	
		self.server_info = tkinter.Listbox(self.frame3)
		self.server_info.grid(row=0, column=0)
		self.frame3.columnconfigure(0, weight=1)
		self.frame3.rowconfigure(2, weight=1)
		self.server_info_scroll = tkinter.Scrollbar(self.frame3, orient=tkinter.HORIZONTAL)
		self.server_info_scroll.grid(row=1, column=0, sticky="ew")
		self.server_info_scroll.config(command=self.server_info.xview)
		self.server_info.config(xscrollcommand=self.server_info_scroll.set)	
		self.server_info_scroll = tkinter.Scrollbar(self.frame3)
		self.server_info_scroll.grid(row=0, column=1, sticky="ns")
		self.server_info_scroll.config(command=self.server_info.yview)
		self.server_info.config(yscrollcommand=self.server_info_scroll.set)	
		self.server_info.columnconfigure(0, weight=1)
		
		self.players = tkinter.Listbox(self.frame3)
		self.players.grid(row=2, column=0, sticky="ns")
		self.players_info_scroll = tkinter.Scrollbar(self.frame3)
		self.players_info_scroll.grid(row=2, column=1, sticky="ns")
		self.players_info_scroll.config(command=self.players.yview)
		self.players.config(yscrollcommand=self.players_info_scroll.set)	
		self.players.columnconfigure(0, weight=1)
		self.players_info_scroll.columnconfigure(1, weight=1)
		self.players.rowconfigure(2, weight=1)
		self.players_info_scroll.rowconfigure(2, weight=1)
		
		self.servers = ttk.Treeview(self.mainwin, columns=('host', 'players', 'map', 'game'))
		self.servers.pack(expand=True, fill="both", side="left")
		
		
		self.servers['columns'] = ['host', 'players', 'map', 'game']
		self.servers.column('host', width=30)
		self.servers.heading('host', text='Host')
		self.servers.column('players', width=2)
		self.servers.heading('players', text='Players')
		self.servers.column('map', width=20)
		self.servers.heading('map', text='Map')
		self.servers.column('game', width=20)
		self.servers.heading('game', text='Game')
		
		for col in self.servers['columns']:
			self.servers.heading(col, text=col, command=lambda _col=col: \
							treeview_sort_column(self.servers, _col, False))
	
		self.servers_scroll = tkinter.Scrollbar(self.mainwin)
		self.servers_scroll.pack(side="right", fill="y")
		self.servers_scroll.config(command=self.servers.yview)
		self.servers.config(yscrollcommand=self.servers_scroll.set)	
		
		
		#self.servers.insert("", "end", "item2", text="Test2")
		self.servers.bind('<ButtonRelease-1>', onselect)
		
def begin():
	global tgui
	tgui = server_gui()	
	tgui.mainwin.mainloop()
	
if __name__ == "__main__":	
	begin()
	print("Closing.")
