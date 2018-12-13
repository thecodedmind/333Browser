import requests
import json

class InvalidListArgument(Exception):
	pass

def motd(game:str):
	url = f"http://333networks.com/json/{game}/motd"
	resp = requests.get(url)
	return json.loads(resp.text)

def get_server_info(server_address, *, game="333networks"):
	url = f"http://333networks.com/json/{game}/{server_address}"
	resp = requests.get(url)
	return json.loads(resp.text)

def get_server_list(game:str, *, s:str="numplayers", o:str="d", r:int=50, p:int=1, q:str=""):
	"""
	game: Required ID of a game that's valid on 333networks list
	startswith: Optional string, only show servers starting with this string
	s: [Sort] How the server list should be sorted, must be one of 'country', 'hostname', 'gametype', 'ip', 'hostport', 'numplayers', 'mapname'
	o: [Order] Must be either a for Ascending order, or d for Descending order
	r: [Results] Max number of servers to show
	p: [Page] Page number to show from the results
	q: [Query] Search term for the servers.
	"""
	valid_sorts = ['country', 'hostname', 'gametype', 'ip', 'hostport', 'numplayers', 'mapname']
	valid_sort_order = ['a', 'd']
	
	if s not in valid_sorts:
		raise InvalidListArgument(f"Sort must be a valid option from {valid_sorts}")
	
	if o not in valid_sort_order:
		raise InvalidListArgument(f"Sort order must be `a` or `d`.")
	
	if r <= 0 or  r > 1000:
		print(f"ERROR: Invalid result integer {r}, must be in range of 1-1000, defaulted to 50.")
		r = 50
		
	query_options = {}	
	url = "http://333networks.com/json"
	url = url+"/"+game
		
	if s != "":
		query_options['s'] = s
		
	if o != "":
		query_options['o'] = o
		
	if q != "":
		query_options['q'] = q
		
	query_options['r'] = r
	query_options['p'] = p	
	response = requests.request("GET", url, params=query_options)
	#print(response.text)
	return json.loads(response.text)
