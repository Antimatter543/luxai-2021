# We have clear ways to improve this. See sticky notes.
from lux.game import Game
from lux.game_map import Cell, RESOURCE_TYPES, Position
from lux.constants import Constants
from lux.game_objects import Unit
from lux.game_constants import GAME_CONSTANTS
from lux import annotate
import math
import sys





### Define helper functions
# Fix using A* so it works with this too


# this snippet finds all resources stored on the map and puts them into a list so we can search over them
def find_resources(game_state):
	resource_tiles: list[Cell] = []
	width, height = game_state.map_width, game_state.map_height
	for y in range(height):
		for x in range(width):
			cell = game_state.map.get_cell(x, y)
			if cell.has_resource():
				resource_tiles.append(cell)
	return resource_tiles

# the next snippet finds the closest resources that we can mine given position on a map
def find_closest_resource(pos, player, resource_tiles):
	closest_dist = math.inf
	closest_resource_tile = None
	for resource_tile in resource_tiles:
		# we skip over resources that we can't mine due to not having researched them
		if resource_tile.resource.type == Constants.RESOURCE_TYPES.COAL and not player.researched_coal(): continue
		if resource_tile.resource.type == Constants.RESOURCE_TYPES.URANIUM and not player.researched_uranium(): continue
		dist = resource_tile.pos.distance_to(pos)
		if dist < closest_dist:
			closest_dist = dist
			closest_resource_tile = resource_tile
	return closest_resource_tile

def find_closest_city_tile(pos, player):
	"""
	pos: Position Object
	player: Player object


	Returns 'closest_city_tile': CityTile Object 
	"""
	closest_city_tile = None
	if len(player.cities) > 0:
		closest_dist = math.inf
		# the cities are stored as a dictionary mapping city id to the city object, which has a citytiles field that
		# contains the information of all citytiles in that city
		for k, city in player.cities.items():
			for city_tile in city.citytiles:
				dist = city_tile.pos.distance_to(pos)
				if dist < closest_dist:
					closest_dist = dist
					closest_city_tile = city_tile
	return closest_city_tile

