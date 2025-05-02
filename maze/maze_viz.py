# -------------------------------------------------
# DON'T CHANGE THIS FILE.
# Visualiser, original code from https://github.com/jostbr/pymaze writteb by Jostein Brændshøi
# Subsequentially modified by Jeffrey Chan.
#
# __author__ = 'Jostein Brændshøi, Jeffrey Chan', 'Elham Naghizade', 'Edward Small'
# __copyright__ = 'Copyright 2025, RMIT University'
# -------------------------------------------------

# MIT License

# Copyright (c) 2021 Jostein Brændshøi

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.



try:
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrow
except:
    plt = None
    

from maze.maze import Maze
from maze.util import Coordinates
from scipy.interpolate import make_interp_spline
from matplotlib.collections import LineCollection
import numpy as np

from solver.mazeSolver import MazeSolver


class Visualizer(object):
    """Class that handles all aspects of visualization.


    Attributes:
        maze: The maze that will be visualized
        solver: Contains the info of the solved path
        multiPath: Related to Task C & D where non-overlapping paths 
        between pairs of (ent, exit) are found
        cell_size (int): How large the cells will be in the plots
        height (int): The height of the maze
        width (int): The width of the maze
        ax: The axes for the plot
    """

    def __init__(self, maze :Maze, solver: MazeSolver, multiPath, cellSize, knapsack):
        self.m_maze     = maze
        self.m_solver   = solver
        self.multiPaths = multiPath 
        self.m_cellSize = cellSize
        self.m_height   = (maze.rowNum()+2) * cellSize
        self.m_width    = (maze.colNum()+2) * cellSize
        self.m_ax       = None
        self.m_knapsack = knapsack


    def show_maze(self, outFilename: str = None):
        """Displays a plot of the maze without the solution path"""

        # create the plot figure and style the axes
        fig = self.configure_plot()

        # plot the walls on the figure
        self.plot_walls()

        # plot the item locations on the figure
        self.plot_items()

        # plot optimal items
        self.plot_optimal_items()

        # plot the entrances and exits on the figure
        self.plotEntExit()

        # plot the parameters
        self.plot_params()

        # plot the solver path
        if self.m_solver != None:
            self.plotSolverPath()

        # display the plot to the user
        if outFilename == None:
            plt.show()
        else:
            # save image
            plt.savefig(outFilename, bbox_inches='tight')

    def plot_params(self):
        """
        Display knapsack parameters on the right side of the plot.
        """
        if plt is None or self.m_ax is None:
            return

        # Prepare values
        path = self.m_solver.getSolverPath()
        capacity = self.m_knapsack.capacity
        optimal_items = self.m_knapsack.optimalCells  # list of item names/IDs
        value = self.m_knapsack.optimalValue
        weight = self.m_knapsack.optimalWeight
        path_length = len(path) if self.m_solver else 0
        row_num = self.m_maze.m_rowNum
        col_num = self.m_maze.m_colNum
        num_items = len(self.m_maze.m_items)
        max_weight = self.m_maze.m_itemParams[1]
        max_value = self.m_maze.m_itemParams[2]
        cells_visited = len(set(path))
        total_weight = sum(item[0] for item in self.m_maze.m_items.values())
        total_value = sum(item[1] for item in self.m_maze.m_items.values())
        reward = self.m_solver.m_solver.m_reward

        # Format the list into lines of 3 items
        items_per_line = 3
        items_lines = [
            ", ".join(str(item) for item in optimal_items[i:i + items_per_line])
            for i in range(0, len(optimal_items), items_per_line)
        ]
        formatted_items = "\n".join(items_lines)

        # Format text block
        text = (
            f"Knapsack capacity: {capacity}\n"
            f"Maze dimensions: {row_num}x{col_num}\n"
            f"Number of items: {num_items}\n"
            f"Max weight: {max_weight}\n"
            f"Max value: {max_value}\n"
            f"Total weight: {total_weight}\n"
            f"Total value: {total_value}\n"
            f"Optimal items: {formatted_items}\n"
            f"Optimal value: {value}\n"
            f"Optimal weight: {weight}\n"
            f"Path length: {path_length}\n"
            f"Unique cells visted: {cells_visited}\n"
            f"Reward: {reward}"
        )

        # Place the text just outside the right edge
        self.m_ax.text(1.05, 0.95, text,
                       transform=self.m_ax.transAxes,
                       fontsize=10,
                       verticalalignment='top',
                       bbox=dict(boxstyle="round", facecolor='wheat', alpha=0.5))


    def plot_items(self):
        """ 
        Plots the items of a maze. This is used when generating the maze image.
        """
        for loc, item in self.m_maze.m_items.items():
            self.m_ax.plot(loc[1] + 1.5, loc[0] + 1.5, 'r*')
            self.m_ax.text(loc[1] + 1.5, loc[0] + 1.75, 'w='+str(item[0]), ha='center', va='center')
            self.m_ax.text(loc[1] + 1.5, loc[0] + 1.25, 'v='+str(item[1]), ha='center', va='center')


    def plot_optimal_items(self):
        """
        Plots the optimal items of a maze. This is used when generating the maze image.
        """
        for cell in self.m_knapsack.optimalCells:
            self.m_ax.plot(cell[1] + 1.5, cell[0] + 1.5, 'gs', alpha=0.5, markersize=7)

    def plot_walls(self):
        """ 
        Plots the walls of a maze. Solid black lines for walls, dotted lines where walls are missing.
        """
        for r in range(0, self.m_maze.rowNum()):
            for c in range(0, self.m_maze.colNum()):
                # Top wall (between (r-1, c) and (r, c))
                p1 = Coordinates(r - 1, c)
                p2 = Coordinates(r, c)
                x_start = (c + 1) * self.m_cellSize
                x_end = (c + 2) * self.m_cellSize
                y = (r + 1) * self.m_cellSize

                if self.m_maze.hasWall(p1, p2):
                    self.m_ax.plot([x_start, x_end], [y, y], color="k", linewidth=1)
                else:
                    self.m_ax.plot([x_start, x_end], [y, y], color="gray", linewidth=0.5, linestyle=":")

                # Left wall (between (r, c-1) and (r, c))
                p3 = Coordinates(r, c - 1)
                p4 = Coordinates(r, c)
                x = (c + 1) * self.m_cellSize
                y_start = (r + 1) * self.m_cellSize
                y_end = (r + 2) * self.m_cellSize

                if self.m_maze.hasWall(p3, p4):
                    self.m_ax.plot([x, x], [y_start, y_end], color="k", linewidth=1)
                else:
                    self.m_ax.plot([x, x], [y_start, y_end], color="gray", linewidth=0.5, linestyle=":")

        # Bottom boundary
        for c in range(0, self.m_maze.colNum()):
            p1 = Coordinates(self.m_maze.rowNum() - 1, c)
            p2 = Coordinates(self.m_maze.rowNum(), c)
            x_start = (c + 1) * self.m_cellSize
            x_end = (c + 2) * self.m_cellSize
            y = (self.m_maze.rowNum() + 1) * self.m_cellSize

            if self.m_maze.hasWall(p1, p2):
                self.m_ax.plot([x_start, x_end], [y, y], color="k", linewidth=1)
            else:
                self.m_ax.plot([x_start, x_end], [y, y], color="gray", linewidth=0.5, linestyle=":")

        # Right boundary
        for r in range(0, self.m_maze.rowNum()):
            p1 = Coordinates(r, self.m_maze.colNum() - 1)
            p2 = Coordinates(r, self.m_maze.colNum())
            x = (self.m_maze.colNum() + 1) * self.m_cellSize
            y_start = (r + 1) * self.m_cellSize
            y_end = (r + 2) * self.m_cellSize

            if self.m_maze.hasWall(p1, p2):
                self.m_ax.plot([x, x], [y_start, y_end], color="k", linewidth=1)
            else:
                self.m_ax.plot([x, x], [y_start, y_end], color="gray", linewidth=0.5, linestyle=":")


    def plotEntExit(self):
        """
        Plots the entrances and exits in the displayed maze.
        """

        for ent in self.m_maze.getEntrances():
            # check direction of arrow
            # upwards arrow
            if ent.getRow() == -1:
                self.m_ax.arrow((ent.getCol()+1.5)*self.m_cellSize, (ent.getRow()+1)*self.m_cellSize, 0, self.m_cellSize*0.6, head_width=0.1)
            # downwards arrow
            elif ent.getRow() == self.m_maze.rowNum():
                self.m_ax.arrow((ent.getCol()+1.5)*self.m_cellSize, (ent.getRow()+2)*self.m_cellSize, 0, -self.m_cellSize*0.6, head_width=0.1)
            # rightward arrow
            elif ent.getCol() == -1:
                self.m_ax.arrow((ent.getCol()+1)*self.m_cellSize, (ent.getRow()+1.5)*self.m_cellSize, self.m_cellSize*0.6, 0, head_width=0.1)
            # leftward arrow
            elif ent.getCol() == self.m_maze.colNum():
                self.m_ax.arrow((ent.getCol()+2)*self.m_cellSize, (ent.getRow()+1.5)*self.m_cellSize, -self.m_cellSize*0.6, 0, head_width=0.1)

        for ext in self.m_maze.getExits():
            # downwards arrow
            if ext.getRow() == -1:
                self.m_ax.arrow((ext.getCol()+1.5)*self.m_cellSize, (ext.getRow()+1.8)*self.m_cellSize, 0, -self.m_cellSize*0.6, head_width=0.1)
            # upwards arrow
            elif ext.getRow() == self.m_maze.rowNum():
                self.m_ax.arrow((ext.getCol()+1.5)*self.m_cellSize, (ext.getRow()+1.2)*self.m_cellSize, 0, self.m_cellSize*0.6, head_width=0.1)
            # leftward arrow
            elif ext.getCol() == -1:
                self.m_ax.arrow((ext.getCol())*self.m_cellSize, (ext.getRow()+1.5)*self.m_cellSize, -self.m_cellSize*0.6, 0, head_width=0.1)
            # leftward arrow
            elif ext.getCol() == self.m_maze.colNum():
                self.m_ax.arrow((ext.getCol()+1.2)*self.m_cellSize, (ext.getRow()+1.5)*self.m_cellSize, self.m_cellSize*0.6, 0, head_width=0.1)

    def plotSolverPath(self):
        """
        Draw the solver's path as smooth interpolated curves with gradient color,
        offset to simulate hugging the right wall in movement direction.
        """
        if not self.multiPaths:
            solverPath = self.m_solver.getSolverPath()
            solverPath = [solverPath]
        else:
            solverPath = self.m_solver.getSolverPath().values()

        if len(solverPath) == 0:
            return

        offset_spacing = 0.1 * self.m_cellSize

        for path in solverPath:
            if len(path) < 2:
                continue

            points = []
            for i in range(len(path)):
                coord = path[i]
                x = (coord.getCol() + 1.5) * self.m_cellSize
                y = (coord.getRow() + 1.5) * self.m_cellSize

                # Determine direction to next point if possible
                if i < len(path) - 1:
                    next_coord = path[i + 1]
                    dx = next_coord.getCol() - coord.getCol()
                    dy = next_coord.getRow() - coord.getRow()
                else:
                    # Use previous direction if last point
                    dx = coord.getCol() - path[i - 1].getCol()
                    dy = coord.getRow() - path[i - 1].getRow()

                length = (dx ** 2 + dy ** 2) ** 0.5
                if length == 0:
                    offset_dx = offset_dy = 0
                else:
                    unit_dx = dx / length
                    unit_dy = dy / length

                    # Clockwise perpendicular (right-hand wall)
                    offset_dx = unit_dy * offset_spacing
                    offset_dy = -unit_dx * offset_spacing

                points.append([x + offset_dx, y + offset_dy])

            points = np.array(points)

            # Interpolate curve
            x_vals, y_vals = points[:, 0], points[:, 1]
            t_vals = np.linspace(0, 1, len(points))

            # More dense points for smoothness
            t_dense = np.linspace(0, 1, 1000)

            # Fit splines
            spline_x = make_interp_spline(t_vals, x_vals, k=3)
            spline_y = make_interp_spline(t_vals, y_vals, k=3)

            x_smooth = spline_x(t_dense)
            y_smooth = spline_y(t_dense)

            # Create smooth segments
            smooth_points = np.column_stack((x_smooth, y_smooth))
            segments = np.array([[smooth_points[i], smooth_points[i + 1]] for i in range(len(smooth_points) - 1)])

            # Gradient color from blue to red with alpha
            colors = [
                (
                    i / (len(segments) - 1),  # R
                    0.0,  # G
                    1.0 - i / (len(segments) - 1),  # B
                    0.3  # Alpha
                )
                for i in range(len(segments))
            ]

            lc = LineCollection(segments, colors=colors, linewidths=2, alpha=0.7)
            self.m_ax.add_collection(lc)
    
    def configure_plot(self):
        """Sets the initial properties of the maze plot. Also creates the plot and axes"""

        # Create the plot figure
        fig = plt.figure(figsize = (7, 7*self.m_maze.rowNum() / self.m_maze.colNum()))

        # Create the axes
        self.m_ax = plt.axes()

        # Set an equal aspect ratio
        self.m_ax.set_aspect("equal")

        # Remove the axes from the figure
        self.m_ax.axes.get_xaxis().set_visible(False)
        self.m_ax.axes.get_yaxis().set_visible(False)


        return fig

