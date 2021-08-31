# Development from solidbot1. Our develop branch.
# Currently does a bit worse than it, factors in night time + if city's too far away just fkin make a new one.
from lux.game import Game
from lux.game_map import Cell, RESOURCE_TYPES, Position
from lux.constants import Constants
from lux.game_objects import Unit
from lux.game_constants import GAME_CONSTANTS
from lux import annotate
import math
import sys

### Define helper functions

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
def find_closest_resources(pos, player, resource_tiles):
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



#### Agent 1 (pre-taking their code) 
game_state = None
def agent(observation, configuration):
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
        """

        direction = unit.pos.direction_to(position)
        target_tile = unit.pos.translate(direction, 1)

        # if target_tile is not being targeted already, move there
        if target_tile not in target_tiles or target_tile in [tile.pos for tile in citytile_cells]:
            target_tiles.append(target_tile)
            actions.append(unit.move(direction))
            actions.append(annotate.line(unit.pos.x, unit.pos.y, position.x, position.y))

        # else, if it is being targetted mark an X on the map
        else:
            actions.append(annotate.x(target_tile.x, target_tile.y))


    def go_home(unit, citytile_cells):
        """
        moves the given unit towards the nearest citytile
        """

        nearest_citytile_position = find_nearest_position(unit.pos, citytile_cells)
        move_unit(unit, nearest_citytile_position)

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

    ###############################################
    #################### Our Code  ################
    ###############################################

    
    #### Fucking ALGO CODE
    player = game_state.players[observation.player]
    opponent = game_state.players[(observation.player + 1) % 2]
    width, height = game_state.map.width, game_state.map.height

    # add debug statements like so!
    if game_state.turn == 0:
        print("Agent is running!", file=sys.stderr)

    resource_tiles = find_resources(game_state)
    citytile_cells = get_cells('player citytile')
    num_citytiles = len(citytile_cells)
#     num_units = len(player.units)
#     print("Num citytile or units", num_citytiles, num_units, file=sys.stderr)
    
    
    ### City actions / citybuilding (put this shit ijn functions later)
    
    cities_to_build = 0
    for k, city in player.cities.items():
        if (city.fuel > city.get_light_upkeep() * GAME_CONSTANTS["PARAMETERS"]["NIGHT_LENGTH"] + 500) or num_citytiles == 0:
            # if our city has enough fuel to survive the whole night and 1000 extra fuel, lets increment citiesToBuild and let our workers know we have room for more city tiles
            cities_to_build += 1
        
        ## Running through each citytile for logic
        for citytile in city.citytiles:
            if citytile.can_act():
                # Either make a new worker or just research.
                if len(citytile_cells) > len(player.units): #and len(player.cities) > len(player.units): # Adding the and kinda breaks it rn, not sure why.
                # you can use the following to get the citytile to research or build a worker
                # commands.push(citytile.research());
                    action = citytile.build_worker()
                    actions.append(action)

                else:
                    action = citytile.research()
                    actions.append(action)
                
    
    
    
    ### Unit Actions ####
    
    for unit in player.units:
        # if the unit is a worker (can mine resources) and can perform an action this turn
        if unit.is_worker() and unit.can_act():
            ## Code for Workers ##
            
            # Mining
            
            # Do we have space and is it day time?
            if unit.get_cargo_space_left() > 0 and not game_state.turn % 40 > 30:
                # IF WE CAN MINE
                # find the closest resource if it exists to this unit
                closest_resource_tile = find_closest_resources(unit.pos, player, resource_tiles)
                if closest_resource_tile is not None:
                    # create a move action to move this unit in the direction of the closest resource tile and add to our actions list
                    move_unit(unit, closest_resource_tile.pos)

            # Everything else (When to build, when to go home, etc.) -> when we are 'full' of cargo
            else:
                
                # Can we build a city right now?
                closest_city_tile = find_closest_city_tile(unit.pos, player)
                
                if cities_to_build > 0 and unit.can_build(game_state.map): #and unit.pos.is_adjacent(closest_city_tile.pos):
                    # BUILD A FUCKER ## IF WE NEAR A CITY (Not anymore, now we just build the fucker)}
                    # here we consider building city tiles provided we are adjacent to a city tile and we can build
                    actions.append(unit.build_city())   
                    
                
                # Go home and drop off resources
                elif closest_city_tile is not None:
                    if unit.pos.distance_to(closest_city_tile.pos) > 6 and unit.can_build(game_state.map):
                        actions.append(unit.build_city())   
                    
                    # WE FOUND THE CLOSEST CITY
                    
                    if cities_to_build > 0 and unit.can_build(game_state.map): #and unit.pos.is_adjacent(closest_city_tile.pos):
                        # BUILD A FUCKER ## IF WE NEAR A CITY (Not anymore, now we just build the fucker)}
                        # here we consider building city tiles provided we are adjacent to a city tile and we can build
                        actions.append(unit.build_city())   
                    
                    else:
                        # LET'S JUST GO HOME
                        # create a move action to move this unit in the direction of the closest resource tile and add to our actions list
                        go_home(unit, citytile_cells)

                    # Annotate where the worker wants to go because why not
                    th = annotate.circle(closest_city_tile.pos.x,  closest_city_tile.pos.y)
                    actions.append(th)
                else:
                    actions.append(unit.build_city())   
                    
                    
                    
    print("Super secret. Turn:", game_state.turn, "Action list:", actions, file=sys.stderr)
    
    return actions