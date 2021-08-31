# Completely new agent type from scratch. Seems promising and fun! We're not begrudged by the starter kit's doodoo logic (although the structure is still there).
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



############## END OF HELPER FUNCTIONS ###############
######################################################
######################################################
######################################################
######################################################



#### Agent 3 - Devastator (pre-taking their code) 
#Aim of the game: Fucking duplicate as fast as you can. Duplicate and eat the world.

game_state = None
def agent(observation, configuration):
	########### Code / Bot starts here ############
	###############################################

	global game_state

	### Do not edit ###
	if observation["step"] == 0:
		game_state = Game()
		game_state._initialize(observation["updates"])
		game_state._update(observation["updates"][2:])
		game_state.id = observation.player
	else:
		game_state._update(observation["updates"])
	
	actions = []
	## Helper functions
	### VOID FUNCTIONS BELOW
	def researched(resource):
		"""
		given a Resource object, return whether the player has researched the resource type
		"""
		if resource.type == Constants.RESOURCE_TYPES.WOOD:
			return True
		if resource.type == Constants.RESOURCE_TYPES.COAL \
			and player.research_points >= GAME_CONSTANTS['PARAMETERS']['RESEARCH_REQUIREMENTS']['COAL']:
				return True
		if resource.type == Constants.RESOURCE_TYPES.URANIUM \
			and player.research_points >= GAME_CONSTANTS['PARAMETERS']['RESEARCH_REQUIREMENTS']['URANIUM']:
				return True
		return False

	def get_cells(cell_type):  # resource, researched resource, player citytile, enemy citytile, empty
		"""
		Given a cell type, returns a list of Cell objects of the given type
		Options are: ['resource', 'researched resource', 'player citytile', 'enemy citytile', 'empty']
		"""
		cells_of_type = []
		for y in range(height):
			for x in range(width):
				cell = game_state.map.get_cell(x, y)
				if (
					   ( cell_type == 'resource' and cell.has_resource() ) \
					or ( cell_type == 'researched resource' and cell.has_resource() and researched(cell.resource) ) \
					or ( cell_type == 'player citytile' and cell.citytile is not None and cell.citytile.team == observation.player ) \
					or ( cell_type == 'enemy citytile' and cell.citytile is not None and cell.citytile.team != observation.player ) \
					or ( cell_type == 'empty' and cell.citytile is None and not cell.has_resource() )
				):
					cells_of_type.append(cell)

		return cells_of_type

	def find_nearest_position(target_position, option_positions):
		# Should we change to find nearest cell?
		"""
		target_position: Position object
		option_positions: list of Position, Cell, or Unit objects (must all be the same type)
		finds the closest option_position to the target_position
		
		Returns: Closest_position -> Position object
		"""

		# convert option_positions list to Position objects
		if type(option_positions[0]) in [Cell, Unit]:
			option_positions = [cell.pos for cell in option_positions]

		# find closest position
		closest_dist = math.inf
		closest_position = None
		for position in option_positions:
			dist = target_position.distance_to(position)
			if dist < closest_dist:
				closest_dist = dist
				closest_position = position

		return closest_position

	target_tiles = [] # to help avoid collisions. You'd want to put this somewhere inside the agent (so it can append target tiles over time and figure shit out)
	#That's our 2nd best alternative since we haven't done linear assignment problem thingy yet.
	def move_unit(unit, position):
		"""
		moves the given unit towards the given position
		also checks basic collision detection, and adds annotations for any movement
		
		Unit: Unit object
		position: Position object OR tuple (x,y). Both will work.
		"""

		# Convert tuple to position class
		if type(position) == tuple:
			pos = Position()
			pos.x = position[0]
			pos.y = position[1]

			position = pos # This just resets our tuple position into the new Position object one so we don't have to rename below.
		else:
			pass
		direction = unit.pos.direction_to(position)
		target_tile = unit.pos.translate(direction, 1)

		# if target_tile is not being targeted already, move there
		if target_tile not in target_tiles or target_tile in [tile.pos for tile in citytile_cells]:
			target_tiles.append(target_tile)
			actions.append(unit.move(direction))
			actions.append(annotate.line(unit.pos.x, unit.pos.y, position.x, position.y))

		# else, if it is being targetted mark an X on the map. Need to fix this to handle collision
		else:
			actions.append(annotate.x(target_tile.x, target_tile.y))


	def go_home(unit, citytile_cells):
		"""
		moves the given unit towards the nearest citytile
		"""

		nearest_citytile_position = find_nearest_position(unit.pos, citytile_cells)
		move_unit(unit, nearest_citytile_position)


	###############################################
	#################### Our Code  ################
	###############################################

	
	#### Fucking ALGO CODE
	player = game_state.players[observation.player]
	opponent = game_state.players[(observation.player + 1) % 2]
	width, height = game_state.map.width, game_state.map.height

	# add debug statements like so!
	if game_state.turn == 0:
		print("I am devastator agent!!", file=sys.stderr)

	resource_tiles = find_resources(game_state)
	citytile_cells = get_cells('player citytile')
	num_citytiles = len(citytile_cells)
	is_night = game_state.turn % 40 > 30 # Bool - True if it's night time
#     num_units = len(player.units)
#     print("Num citytile or units", num_citytiles, num_units, file=sys.stderr)
	
	
	### City actions / citybuilding (put this shit ijn functions later)
	"""Priority list for cities:
	Worker
	Research"""
	for k, city in player.cities.items():
		## Running through each citytile for logic
		for citytile in city.citytiles:
			if citytile.can_act():
				# Either make a new worker or just research.
				if len(citytile_cells) > len(player.units): 
					action = citytile.build_worker()
					actions.append(action)

				else:
					action = citytile.research()
					actions.append(action)

	### Unit Actions ####
	
	for unit in player.units:
		"""
		Priority list for units:
		Place a city if possible (should we put a weight on adjacent cities?)
		
		else;
			Mine
			If cargo full and you don't wanna place;
				Return to city

		"""
		# TODO - We could have the bot find the closest empty cell to place a city too. Actually, let's do that now.
		closest_city_tile = find_closest_city_tile(unit.pos, player) 
		## Code for Workers ##
		if unit.is_worker() and unit.can_act():

			# Check if it has no cargo space
			if unit.get_cargo_space_left() == 0 and unit.can_build(game_state.map): #I.e it's at 100 cargo space (the amt required to build a city):
				print("I'm gonna build a city because I have full inventory + I can build!", file=sys.stderr)
				actions.append(unit.build_city())
			
			# We're full but unbuildable rn, find the closest place to build to. THis might go horribly wroong lol
			elif unit.get_cargo_space_left() == 0:
				empty_cells = get_cells('empty')
				closest_empty_cell_pos = find_nearest_position(unit.pos, empty_cells)
				move_unit(unit, closest_empty_cell_pos)
			
			else: #I.e you might have 0 cargo but can't build
				# Mine if you have cargo space  
				# Else go home
				if unit.get_cargo_space_left() > 0:
					closest_resource_tile = find_closest_resource(unit.pos, player, resource_tiles)
					if closest_resource_tile is not None and not is_night:
						# Move to closest resource if it's day time OR we don't have enough fuel
						move_unit(unit, closest_resource_tile.pos)
					else:
						print("Well.. Shit. I'm unit,", unit.id ,"Apparently I can't find any resources. Or it's nighttime", file=sys.stderr)

					# go_mine(unit, resources) -> Make this void function sometime? (i.e function that does stuff)

				else:
					# If we have no cargo space & can't build.
					go_home(unit, citytile_cells)
				#  Go home 
					
					
	print("Super secret. Turn:", game_state.turn, "Action list:", actions, file=sys.stderr)
	
	return actions