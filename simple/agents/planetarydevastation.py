"""
Started 29/8/21. We will try to push this bot to 1100. If not, we're gonna push this bot to eat everything on the map a high % of the time.

Planetary Devastation - Instead of eaching all of a cluster first then moving on, *spread your cancer* (i.e send 1 worker) to a different cluster and make them do their own devastation. So we just devastate  the world as fast as we can. ---> Floodfill.

Maybe figure out better boilerplate?
https://www.kaggle.com/superant/halite-boilerbot
"""
from lux import game
from lux.game import Game
from lux.game_map import Cell, RESOURCE_TYPES, Position
from lux.constants import Constants
from lux.game_constants import GAME_CONSTANTS
from lux import annotate
import math
import sys

from scipy.ndimage import measurements
import numpy as np
"""
Planetary Devastation, Funny Agent:
Destroy the environment as fast as possible...

> Collect resources
> Build city ASAP
> When you have enough workers, identify resource clusters. Send workers to different resource clusters.
---> Make sure they can live by the time they get there?

"""


"""Cluster identification:
First. 
Get researched resource cells.

Loop through them -> Check if 

I want a dictionary:
Trees: {'1': [(cluster1 trees so Tree1), (Tree2), ...], '2': (cluster2 trees so Tree1, Tree2,...), 'n': ...} # Dictionary of trees and their clusters.

for tree in trees (get_cell'd):
	if tree.pos.adjacent_to							

/// After identifyng:
Then, I  basically want to assign an agent to move to a cluster '1', or '2', etc.


Check notebook!!! "# Then, for each agent, we want to find the closest non_zero cluster THAT HASN'T BEEN PICKED YET. HOLY SHIT THAT'S IT. THIS IS THE MOST IMPORTANT FUCKING LINE IN THIS WHOLE NTOEBOOK
""

"""
# Global helper functions
def manhattan_distance(x1, x2, y1, y2):
	return abs(x1-x2) + abs(y1-y2)



class ClusterTracker():
	"""
	Anything to do with cluster creation / tracking / identification 
	"""
	def __init__(self, game_state):
		# Initialise 0 matrix to width, height of map.
		width, height = game_state.map_width, game_state.map_height
		self.empty_matrix = np.zeros([width, height])

		# Initialise clsuter matrices for each different resource.
		self.tree_matrix = self.empty_matrix
		self.coal_matrix = self.empty_matrix
		self.uranium_matrix = self.empty_matrix
		
		
	def create_cluster_matrix(self, game_state, resource_type):
		""" Creates tree matrix 
		Updates the tree matrix aswell btw.
		Args:
		game_state -> game_state
		resource_type: "wood", "coal", "uranium"
		Returns: Tree matrix
		Example:
		[[0. 1. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 1. 0.]
		[1. 0. 1. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 1. 0. 1.]
		[0. 1. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 1. 0.]
		[0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
		[0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
		[0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
		[0. 0. 0. 1. 0. 1. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
		[0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
		[0. 0. 1. 1. 1. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
		[0. 0. 1. 1. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
		[0. 1. 0. 1. 1. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
		[0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
		[0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
		[0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
		[0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
		[0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]]
		Note that to get a (x,y) value of a matrix you must go matrix[y][x]"""

		# Resets cluster matrix based on what resource we're getting so old resources don't stay in there.
		resource_matrix = self.empty_matrix
		if resource_type == 'wood':
			self.tree_matrix = self.empty_matrix 
		elif resource_type == 'coal':
			self.coal_matrix = self.empty_matrix 
		else:
			self.uranium_matrix = self.empty_matrix 

		## The stuff.
		width, height = game_state.map_width, game_state.map_height

		for y in range(height):
			for x in range(width):
				cell = game_state.map.get_cell(x, y)
				# Debugging, just to see what resources it 'sees'.
				# try:
				# 	print(cell.resource.type)
				# except:
				# 	pass
				# Sets any position where there's a tree to 1 in the tree_matrix
				if resource_type == 'wood' and cell.has_resource() and cell.resource.type == Constants.RESOURCE_TYPES.WOOD: # If it's a tree add it to the matrix.
					self.tree_matrix[y][x] = 1
					resource_matrix[y][x] = 1 
				# The =1 / 2 / 3 is arbitrary. It's just so we can differentiate better if we have to debug.
				elif resource_type == 'coal' and cell.has_resource() and cell.resource.type == Constants.RESOURCE_TYPES.COAL: # If it's a coal add it to the matrix.
					self.coal_matrix[y][x] = 2
					resource_matrix[y][x] = 2 
				elif resource_type == 'uranium' and cell.has_resource() and cell.resource.type == Constants.RESOURCE_TYPES.URANIUM: # If it's a coal add it to the self.coal_matrix.
					self.uranium_matrix[y][x] = 3
					resource_matrix[y][x] = 3
					
		# Return cluster matrix of resource we were looking for.
		return resource_matrix
	
	def convert_to_cluster(self, resource_matrix):
		"""Get cluster information -> cluster matrix and position of the clustered resources
		 Resource matrix: The returned matrix of create_cluster_matrix. This is a matrix of the resources in the map
		 """
		cluster_matrix, num_clusters = measurements.label(resource_matrix) 
		""" Cluster matrix looks like
		 [[ 0  1  0  0  0  0  0  0  0  0  0  0  0  0  2  0]
		[ 3  0  4  0  0  0  0  0  0  0  0  0  0  5  0  6]
		[ 0  7  0  0  0  0  0  0  0  0  0  0  0  0  8  0]
		[ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
		[ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
		[ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
		[ 0  0  0  9  0 10  0  0  0  0  0  0  0  0  0  0]
		[ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
		[ 0  0 11 11 11  0  0  0  0  0  0  0  0  0  0  0]
		[ 0  0 11 11  0  0  0  0  0  0  0  0  0  0  0  0]
		[ 0 12  0 11 11  0  0  0  0  0  0  0  0  0  0  0]
		[ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
		[ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
		[ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
		[ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
		[ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]]"""
		# Cluster_matrix = matrix of all clusters IDENTIFIED (i.e each individual cluster is called '1', '2', etc... Like, each tree in cluster 1 is called '1' in the matrix.)
		# num_clusters is the number of clusters lol (for this resource).
		# See the jupyter notebook for cluster info.

		resource_positions = cluster_matrix.nonzero() # Gets a list of [[y],[x]] coordinates of the positions of trees, etc.
		return cluster_matrix, resource_positions


	def closest_cluster(self, unit, resource_positions, cluster_matrix):
		"""Returns the number of the closest non-zero cluster and its position as a TUPLE
		so
		Args:
		Unit
		non_zero_pos - A list of 2 arrays [[y], [x]] coordinates of the positions of clusters 
		matrix - Matrix of unique cluster locations
		Returns: [11, Pos(10, 9)] or some shit -> cluster_id 11 at Position Object (10, 9)"""
		start = unit.pos
		
		y_list = resource_positions[0] # A list
		x_list= resource_positions[1] # A list
		
		closest_dist = math.inf
		for i in range(len(y_list)): # Both x,y same length:
			y= y_list[i]
			x = x_list[i]
		
			dist = manhattan_distance(start.x, x, start.y, y)
			# dist = manhattan_distance(10, x, 2, y) # test
			
			if dist < closest_dist:
				closest_dist = dist
				closest_cluster_id = cluster_matrix[y][x]
				# So we can return it later for other functions
				bestx = x
				besty = y
		
		position = Position(bestx,besty) # Transform it into luxai's Position object just so it's more compatible and thematic.
				
		return [closest_cluster_id, position]  # E.g [4, (3,10)] -> Unique cluster 4 @ Position (3,10).


class Agent():
	def __init__(self):
		self.memory={}
		# self.trees = .. etc so OP OP and you can access/update them only when required. I mean this is more optimisation stuff ut stilkl cool.
		# Trackers

	def process_observation(self, observation):
		# updates gamestate and initializes at step zero
		if observation["step"] == 0:
			self.game_state = Game()
			self.game_state._initialize(observation["updates"])
			self.game_state._update(observation["updates"][2:])
			self.game_state.id = observation.player
		else:
			self.game_state._update(observation["updates"])
		return self.game_state



	# Now we just go to it (if another agent hasn't called dibs on it already).
	def move_to_cluster(self, unit, closest_cluster):
		"""
		Args:
		Unit - Unit object
		closest_cluster: List of cluster ID and closest tuple to a worker, as [11, (10,9)] example.
		
		Returns: NA, moves unit to fkin closest resource in that cluster ID"""
		cluster_id, cluster_resource_pos = closest_cluster
		self.move_unit(unit, cluster_resource_pos) # Might have to change move unit so we can accept tuple inputs / change cluster-pos to a Pos object.
		
	def move_unit(unit, position, target_tiles, actions, citytile_cells):
		""" Moves a unit to a target position. Avoids tiles already targeted (unless it's in a city). Doesn't explicitly fix collisions though.

		Args:
		unit : Unit object
		position : Position object (where do you want to go)
		target_tiles : List[Position] (list of position objects)
		actions : actions list
		citytile_cells : List[Cell] (from get_cells() method).
		"""
		# This works btw. Appending over here will actully append to the real action outside this method/class thing.
		# This works btw. Appending over here will actully append to the real action outside this method/class thing.
		# This works btw. Appending over here will actully append to the real action outside this method/class thing.
		direction = unit.pos.direction_to(position)
		target_tile = unit.pos.translate(direction, 1)

		# if target_tile is not being targeted already, move there
		if target_tile not in target_tiles or target_tile in [tile.pos for tile in citytile_cells]: # If we're not already moving there/ if it's a city (since no stacking limit in city)
			target_tiles.append(target_tile)
			actions.append(unit.move(direction)) # This works btw. Appending over here will actully append to the real action outside this method/class thing.
			actions.append(annotate.line(unit.pos.x, unit.pos.y, position.x, position.y))

		# else, if it is being targetted mark an X on the map. Need to fix this to handle collision
		else:
			actions.append(annotate.x(target_tile.x, target_tile.y))

	def __call__(self, observation, configuration):
		# What happens every time the agent is called.
		game_state = self.process_observation(observation)

		actions = []
		player = game_state.players[observation.player]
		opponent = game_state.players[(observation.player + 1) % 2]
		width, height = game_state.map.width, game_state.map.height

		## Clusters
		cluster_tracker = ClusterTracker(game_state)
		tree_matrix = cluster_tracker.create_cluster_matrix(game_state, "wood") # Don't use this anywhere but convert_to_cluster. In fact, this should probably just be an inside step for convert to cluster lol.
		tree_cluster_matrix, tree_positions = cluster_tracker.convert_to_cluster(tree_matrix) # Tree cluster matrix is a relabled tree matrix where each cluster has its own unique id (e.g all trees in cluster 1 relabled to '1'.)


	# add debug statements like so!
		if game_state.turn == 0:
			print("{Planetary Devastation is running!", file=sys.stderr)
			actions.append(annotate.circle(0, 0))


		for unit in player.units:
			cluster_id, cluster_pos = cluster_tracker.closest_cluster(unit, tree_positions, tree_cluster_matrix) # [11, (2,3)]
			# tree_cluster_matrix[unit.pos.y][unit.pos.x] = 69
			# print(tree_cluster_matrix, cluster_id, file=sys.stderr)
			print("Closest cluster id is: {} at position {} at turn {}".format(cluster_id, cluster_pos, game_state.turn), file=sys.stderr)
			actions.append(annotate.line(unit.pos.x, unit.pos.y, cluster_pos.x, cluster_pos.y))

		return actions
	


# the rest only to make it work for Kaggle submission
agent = Agent()
def call_agent(obs, conf):
	return agent(obs,conf)