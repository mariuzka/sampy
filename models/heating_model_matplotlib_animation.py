# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 23:10:54 2020

@author: ac135963
"""

import os

os.chdir("C:/Users/ac135963/Nextcloud/Projekte/sampy")

from Helper import *
from World import *
from Visualizer import *
from Agent import *
from Cell import *

import statistics
import random

class Heating_Agent(Agent):
    desire = 0
    loss_rate = 0.125
    tolerance = 0.1
    adjustment_size = 1

    def __init__(self,
                 desire,
                 output,
                 worldstate,
                 input,
                 loss_rate,
                 ):

        Agent.__init__(self)

        # desired worldstate value / input value
        self.desire = desire

        # value of performed action
        self.output = output

        # worldstate in the world of this agent
        self.worldstate = worldstate

        # subjectively perceived world state
        self.input = input

        # result of last evaluation
        self.evaluation_result = str

        # dict of lists with neighbor-groups
        self.neighbors = {}

        # number
        self.n_borders = int

        # loss rate per border
        #self.loss_rate = loss_rate

        self.data = {
            "tick": [],
            "desire": [],
            "worldstate": [],
            "input": [],
            "output": [],
            "evaluation_result": [],
            "n_borders": [],
            "n_neighbors": [],
            "x_pos": [],
            "y_pos": []}

    
    def find_all_neighbors_on_neighbor_cells(self):
        self.neighbors = []
        for cell in self.residence_cell.neighbor_cells:
            self.neighbors.extend(
                    list(
                            cell.dict_of_residents.values()
                            )
                    )
        
        
        #self.neighbors = [len(cell.residents) 
        #                  for cell in self.residence_cell.neighbor_cells]
        self.n_borders = len(self.neighbors)
    
    def random_move(self, world):
        if self.output - self.worldstate > 8:
            if random.random() < 0.1:
                #print("moved")
                self.move_to_this_cell(random.choice(world.get_empty_cells()))
                self.find_all_neighbors_on_neighbor_cells()
                for neighbor in self.neighbors:
                    neighbor.find_all_neighbors_on_neighbor_cells()
            
            


    def evaluate_input(self):
        """
        evaluates the perceived worldstate/input value
        changes Agent.evaluation_result to either "too high", "too low" or "perfect"
        Input: Agent.input; Agent.desire
        Output: Agent.evaluation_result
        """

        if self.input > self.desire + self.tolerance:
            self.evaluation_result = "too high"

        elif self.input < self.desire - self.tolerance:
            self.evaluation_result = "too low"

        else:
            self.evaluation_result = "perfect"


    def set_output(self, output_min=None, output_max=None):
        """
        sets/adjusts the output depending on the evaluation of the input
        Input: Agent.evaluation_result
        Output: Agent.output
        """

        output = self.output

        if self.evaluation_result == "perfect":
            pass
        else:
            adjustment = random.uniform(0, self.adjustment_size)
            # wenn adjustment sehr klein, dann entstehen die muster nicht.

            if self.evaluation_result == "too high":
                output -= adjustment
            else:
                output += adjustment

        # keep output within boundaries
        if output_min != None:
            if output < output_min:
                output = output_min

        if output_max != None:
            if output > output_max:
                output = output_max

        self.output = output


    def calculate_worldstate_and_input(self, interdependence_structure):

        # input_i = worldstate_i = output_i * (1 - p) + output_j * p
        if interdependence_structure == "local_exchange":

            own_contribution = self.output * (1 - self.loss_rate * self.n_borders)
            contribution_of_neighbors = sum([neigh.loss_rate * neigh.output for neigh in self.neighbors])
            self.worldstate = own_contribution + contribution_of_neighbors

            self.input = self.worldstate

        # input_i = worldstate_i = output_i + output_j * p
        elif interdependence_structure == "local_giving":

            own_contribution = self.output
            contribution_of_neighbors = sum([neigh.loss_rate * neigh.output for neigh in self.neighbors])
            self.worldstate = own_contribution + contribution_of_neighbors

            self.input = self.worldstate


        elif interdependence_structure == "diffusion":
            own_contribution = self.output

            contribution_of_neighbors = sum([neigh.loss_rate * neigh.worldstate for neigh in self.neighbors])

            self.worldstate = own_contribution + contribution_of_neighbors

            self.input = self.worldstate * (1 - self.loss_rate)
     






world = World(80, 80)
world.create_grid()

# Agenten-Population erstellen
world.agents.update({"agents_1": [] })

for cell in world.grid_as_flat_list:
    if random.random() < 0.975:
    
        agent = Heating_Agent(0,0,0,0,0.15)
        agent.desire += random.randint(-1,1)
    
        world.agents["agents_1"].append(agent)
    
    cell.neighbor_cells = cell.find_arounding_cells(
        "neumann", 
        world.len_x_grid_dim, 
        world.len_y_grid_dim, 
        world.grid_as_matrix,
    )
    
world.place_agents_on_grid(world.agents["agents_1"])

# Nachbarn der Agenten finden
for agent in world.agents["agents_1"]:
    agent.find_all_neighbors_on_neighbor_cells()

# Mittleren Agenten manipulieren
#world.grid_as_flat_list[int(len(world.grid_as_flat_list) / 2)].main_resident.desire += 10
#world.grid_as_flat_list[int(len(world.grid_as_flat_list) / 4)].main_resident.desire -= 10

def animate_heating():   
    
    agents = world.agents["agents_1"]
    #random.shuffle(agents)
    
    for focal_agent in agents:
        #focal_agent = random.choice(world.agents["agents_1"])
        focal_agent.random_move(world)
        focal_agent.calculate_worldstate_and_input("local_exchange")
        focal_agent.evaluate_input()
        focal_agent.set_output(output_min=-50, output_max=50)

    desire_output_matrix = [[(cell.main_resident.output if cell.main_resident else 0) for cell in row] 
                                for row in world.grid_as_matrix]
    #for row in world.grid_as_matrix:
    #    desire_output_row = []
    #    for cell in row:
    #        desire_output_row.append(cell.main_resident.output)
    #    desire_output_matrix.append(desire_output_row)
    return desire_output_matrix


import matplotlib.pyplot as plt
from matplotlib import animation, rc

fig, ax = plt.subplots()

im = ax.imshow(
        animate_heating(), 
        #cmap = "bwr",
        #cmap = "coolwarm",
        cmap = "RdGy",
        vmin=-50, 
        vmax=50,
        )

f = 100

def animate_func(i):
    im.set_array(animate_heating())
    return im



anim = animation.FuncAnimation(
                               fig, 
                               animate_func, 
                               interval = 0.001, # in ms
                               frames = f,
                               )

#writervideo = animation.FFMpegWriter(fps=60)

#anim.save("test.mp4", writer=writervideo)
