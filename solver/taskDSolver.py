# -------------------------------------------------------------------
# PLEASE UPDATE THIS FILE.
# Greedy maze solver for all entrance, exit pairs
#
# __author__ = <student name here>
# __copyright__ = 'Copyright 2025, RMIT University'
# -------------------------------------------------------------------


from maze.util import Coordinates
from maze.maze import Maze

from knapsack.knapsack import Knapsack
from itertools import permutations

from typing import List, Dict, Optional

import math
# import time


class TaskDSolver:
    def __init__(self, knapsack:Knapsack):
        self.m_solverPath: List[Coordinates] = []
        self.m_cellsExplored = 0 # count of UNIQUE cells visited. i.e. final count should equal len(set(self.m_solverPath))
        self.m_entranceUsed = None
        self.m_exitUsed = None
        self.m_knapsack = knapsack
        self.m_value = 0
        self.m_reward = float('-inf') # initial reward should be terrible

        # you may which to add more parameters here, such as probabilities, etc
        # you may update these parameters using the Maze object in SolveMaze

    def reward(self):
        return self.m_knapsack.optimalValue - self.m_cellsExplored

    def solveMaze(self, maze: Maze, entrance: Coordinates, exit: Coordinates):
        # startGenTime: float = time.perf_counter()
        """
        Solution for Task D goes here.

        Be sure to increase self.m_cellsExplored whenever you visit a NEW cell
        Be sure to increase the knapsack_value whenever you find an item and put it in your knapsack.
        You may use the maze object to check if a cell you visit has an item
        maze.m_itemParams can be used to calculate things like predicted reward, etc. But you can only use
        maze.m_items to check if your current cell contains an item (and if so, what is its weight and value)

        Code in this function will be rigorously tested. An honest but bad solution will still gain quite a few marks.
        A cheated solution will gain 0 marks for all of Task D.
        Args:
            maze: maze object
            entrance: initial entrance coord
            exit: exit coord

        Returns: Nothing, but updates variables
        """
        # set up initial condition for knapsack. It should be empty
        self.m_knapsack.optimalCells = []
        self.m_knapsack.optimalValue = 0
        self.m_knapsack.optimalWeight = 0

        # get intial knowledge base of the maze items. This is the only occasion we can use maze.m_items
        # get the number of items in the maze from the paramaters
        items_in_maze = maze.m_itemParams[0]
        # calculate total weight in maze form item list
        maze_item_weight = sum(weight_value[0] for weight_value in maze.m_items.values())
        # calculate total value in maze from item list
        maze_item_value = sum(weight_value[1] for weight_value in maze.m_items.values())

        # set up some intitial values for the TaskDSolver object. As you calculate a solution, you will need
        # to change the solver path and recalculate your reward.
        self.m_solverPath = []
        self.m_entranceUsed = entrance
        self.m_exitUsed = exit
        self.m_cellsExplored = len(set(self.m_solverPath))
        self.m_reward = self.reward()
        
        self.foundTreasures: List[tuple[Coordinates, int, int]] = [] #coords, value, weight

        # Centre point of the maze
        centre = Coordinates(maze.rowNum() // 2, maze.colNum() // 2)    
        # 4 Corners of the maze
        southWest = Coordinates(0, 0)
        southEast = Coordinates(0, maze.colNum() - 1)
        northEast = Coordinates(maze.rowNum() - 1, maze.colNum() - 1)
        northWest = Coordinates(maze.rowNum() - 1, 0)

        # Path will be entrance -> southWest -> southEast -> northEast -> southWest -> exit (with the path going to the centre and back for each corner visit)
        pathSegments = [
            (entrance, southWest),

            (southWest, centre),
            (centre, southWest),
            (southWest, southEast),

            (southEast, centre),
            (centre, southEast),
            (southEast, northEast),

            (northEast, centre),
            (centre, northEast),
            (northEast, northWest),

            (northWest, centre),
            (centre, northWest),
            (northWest, southWest),

            (southWest, exit)
        ]

        for i, (start, end) in enumerate(pathSegments):
            segment = self.bfs(maze, start, end)
            if i == 0:
                self.m_solverPath.extend(segment)
            else:
                self.m_solverPath.extend(segment[1:]) #if it's not the first segment then remove the head of that segment 

        # Checking if the cell contains a treasure
        for cell in set(self.m_solverPath):
            loc = (cell.getRow(), cell.getCol())
            item = maze.m_items.get(loc)

            if item: 
                value, weight = item       
                toBeAdded = (loc, value, weight)
                self.foundTreasures.append(toBeAdded)
        
        # Dynamic knapsack to choose which treasure to pick 
        self.m_knapsack.optimalCells, self.m_knapsack.optimalWeight, self.m_knapsack.optimalValue = self.dynamicKnapsack(self.foundTreasures, self.m_knapsack.capacity, len(self.foundTreasures))

        # Recalculate the reward
        self.m_cellsExplored = len(set(self.m_solverPath))
        self.m_reward = self.reward()

        self.checkPathLegal(maze, entrance, exit)

        # endGenTime: float = time.perf_counter()
        # print("Task D Solver took " + str(endGenTime - startGenTime) + " seconds")

    def checkPathLegal(self, maze:Maze, entrance:Coordinates, exit:Coordinates):
        """
        Checks if the generated path is legal. Throws an error if not.
        Also checks that the path starts at the entrance and ends at the exit.
        """
        if not self.m_solverPath:
            raise ValueError("Illegal path: Path is empty.")

        # Check start and end positions
        if self.m_solverPath[0] != entrance:
            raise ValueError(
                f"Illegal path: Path does not start at entrance ({entrance.getRow()}, {entrance.getCol()})."
            )
        if self.m_solverPath[-1] != exit:
            raise ValueError(
                f"Illegal path: Path does not end at exit ({exit.getRow()}, {exit.getCol()})."
            )

        # LEGAL PATH CHECK
        for i in range(1, len(self.m_solverPath)):
            prev = self.m_solverPath[i - 1]
            curr = self.m_solverPath[i]
            # Check adjacency
            if curr not in maze.neighbours(prev):
                raise ValueError(
                    f"Illegal path: ({prev.getRow()}, {prev.getCol()}) and ({curr.getRow()}, {curr.getCol()}) are not adjacent."
                )
            # Check for wall
            if maze.hasWall(prev, curr):
                raise ValueError(
                    f"Illegal path: Wall between ({prev.getRow()}, {prev.getCol()}) and ({curr.getRow()}, {curr.getCol()})."
                )

        print("Path is legal.")

    def bfs(self, maze: Maze, start: Coordinates, goal: Coordinates) -> List[Coordinates]:
        """
        Finds the shortest path between start and goal coordinate using breadth first search

        @param maze: the maze we are working on.
        @param start: the starting coordinate.
        @param goal: the goal coordinate.

        @return A list containing coordinates to go from the start to the goal.
        """

        if start == goal:
            return [start]

        visited = set()
        queue = [start]
        predecessors: Dict[Coordinates, Optional[Coordinates]] = {start: None}

        while queue:
            curr = queue.pop(0)

            if curr == goal:
                # Reconstruct path from goal to start
                path = []
                while curr is not None:
                    path.append(curr)
                    curr = predecessors[curr]
                return list(reversed(path))

            visited.add(curr)

            for neighbor in maze.neighbours(curr):
                if neighbor not in visited and neighbor not in predecessors:
                    if not maze.hasWall(curr, neighbor):
                        queue.append(neighbor)
                        predecessors[neighbor] = curr

        # If goal is unreachable (shouldn’t happen in a fully connected maze)
        return []
    
    def dynamicKnapsack(self, items: list, capacity: int, num_items: int):
        """
        Dynamic 0/1 Knapsack that saves the dynamic programming table as a csv.

        @param items: list of (name, weight, value)
        @param capacity: current remaining knapsack capacity
        @param num_items: number of items still being considered
        @param filename: save name for csv of table (used for testing)
        """
        # Initialize DP table with None
        dp = [[None] * (capacity + 1) for _ in range(num_items + 1)]
        # first row is all 0s
        dp[0] = [0] * (capacity + 1)

        selected_items, selected_weight, max_value = [], 0, 0
    
        # Any of "items[i - 1]" is from converting the (kind of?) 1-indexed of the table to 0-indexed of items
        # topDown is a Memory Function
        def topDown(i: int, c: int): 
            if dp[i][c] is not None: 
                return dp[i][c]
    
            if i == 0 or c == 0:
                output = 0
            elif items[i - 1][1] > c:
                output = topDown(i-1, c)
            else:
                inc = topDown(i - 1, c - items[i - 1][1]) + items[i - 1][2]
                exc = topDown(i - 1, c)
                output = max(inc, exc)

            dp[i][c] = output; 
            return output
        
        max_value = topDown(num_items, capacity)    

        # Backtracking
        i = num_items
        c = capacity
        
        while i > 0 and c > 0:
            # If the value at this cell is not the same as the one right above it in the table
            if dp[i][c] != dp[i-1][c]:
                selected_items.append(items[i - 1][0])  # Add location
                selected_weight += items[i - 1][1]  # Add weight
                
                # Subtract weight from remaining capacity
                c -= items[i - 1][1]
            
            # Move to the previous item
            i -= 1

        return selected_items, selected_weight, max_value