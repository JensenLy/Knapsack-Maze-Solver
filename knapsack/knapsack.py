# -------------------------------------------------
# File for Tasks A and B
# Class for knapsack
# PLEASE UPDATE THIS FILE
#
# __author__ = 'Edward Small'
# __copyright__ = 'Copyright 2025, RMIT University'
# -------------------------------------------------

import csv
from maze.maze import Maze


class Knapsack:
    """
    Base class for the knapsack.
    """

    def __init__(self, capacity: int, knapsackSolver: str):
        """
        Constructor.

        @param capacity: the maximum weight the knapsack can hold
        @param knapsackSolver: the method we wish to use to find optimal knapsack items (recur or dynamic)
        """
        # initialise variables
        self.capacity = capacity
        self.optimalValue = 0
        self.optimalWeight = 0
        self.optimalCells = []
        self.knapsackSolver = knapsackSolver

    def solveKnapsack(self, maze: Maze, filename: str):
        """
        Calls the method to calculate the optimal knapsack solution
        @param maze: The maze we are considering
        """
        map = []
        # Sort by row (i) first, then column (j)
        sorted_items = sorted(maze.m_items.items(), key=lambda item: (item[0][0], item[0][1]))

        for cell, (weight, value) in sorted_items:
            map.append([cell, weight, value])

        if self.knapsackSolver == "recur":
            self.optimalCells, self.optimalWeight, self.optimalValue = self.recursiveKnapsack(map,
                                                                                              self.capacity,
                                                                                              len(map),
                                                                                              filename)
        elif self.knapsackSolver == "dynamic":
            self.optimalCells, self.optimalWeight, self.optimalValue = self.dynamicKnapsack(map,
                                                                                            self.capacity,
                                                                                            len(map),
                                                                                            filename)

        else:
            raise Exception("Incorrect Knapsack Solver Used.")

    def recursiveKnapsack(self, items: list, capacity: int, num_items: int, filename: str = None,
                          stats={'count': 0, 'logged': False}):
        """
        Recursive 0/1 Knapsack that logs how many times it's been called
        when the base case is first hit.

        @param items: list of (name, weight, value)
        @param capacity: current remaining knapsack capacity
        @param num_items: number of items still being considered
        @param filename: where to save call count on first base case (used for testing)
        @param stats: dict tracking call count and log status (used for testing)
        """
        # Increment call count on every call - feed back into the function on each call for testing
        stats['count'] += 1

        # Base case
        if capacity == 0 or num_items == 0:
            if not stats['logged'] and filename:
                with open(filename+'.txt', "w") as f:
                    f.write(str(stats['count']))
                stats['logged'] = True  # Make sure we only log once
            return [], 0, 0

        L_opt = []; 
        w_opt = 0; 
        v_opt = 0; 

        t: list = items[num_items - 1]

        location = t[0]
        weight = t[1]
        value = t[2]

        if weight > capacity: 
            return self.recursiveKnapsack(items, capacity, num_items - 1, filename, stats)

        L_inc, w_inc, v_inc = self.recursiveKnapsack(items, capacity - weight, num_items - 1, filename, stats)
        L_exc, w_exc, v_exc  = self.recursiveKnapsack(items, capacity, num_items - 1, filename, stats)

        if v_inc + value > v_exc:
            L_opt = L_inc + [location]
            w_opt = w_inc + weight
            v_opt = v_inc + value
        else:
            L_opt = L_exc
            w_opt = w_exc
            v_opt = v_exc

        return L_opt, w_opt, v_opt

    def dynamicKnapsack(self, items: list, capacity: int, num_items: int, filename: str):
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
       
        # === Save DP Table to CSV ===
        self.saveCSV(dp, items, capacity, filename)

        return selected_items, selected_weight, max_value

    def saveCSV(self, dp: list, items: list, capacity: int, filename: str):
        with open(filename+".csv", 'w', newline='') as f:
            writer = csv.writer(f)

            # Header: capacities from 0 to capacity
            header = [''] + [str(j) for j in range(capacity + 1)]
            writer.writerow(header)

            # First row: dp[0], meaning "no items considered"
            first_row = [''] + [(val if val is not None else '#') for val in dp[0]]
            writer.writerow(first_row)

            # Following rows: each item
            for i in range(1, len(dp)):
                row_label = f"({items[i - 1][1]}, {items[i - 1][2]})"
                row = [row_label] + [(val if val is not None else '#') for val in dp[i]]
                writer.writerow(row)

