import numpy as np
import random

# A class to represent a maze
#
class Maze:
    def __init__(self):
        self.maze = None
        self.start_point = None
        self.end_point = None
        self.path = None
        self.selected_block = None
        self.block_size = 49
        self.WALL_COLOR = [0,0,0]
        self.BACKGROUND_COLOR_INT = 255
        self.BACKGROUND_COLOR = [self.BACKGROUND_COLOR_INT for i in range(0, 3, 1)]
        self.START_COLOR = [255, 0, 0]
        self.GOAL_COLOR = [0, 255, 0]
        self.PATH_COLOR = [0, 0, 255]
        self.SELECTION_COLOR = [232, 244, 66]

    # Public members
    #

    # Generates a new maze of (num_rows x num_cols) blocks
    # Each item in the maze index will point to a cell to which it is adjacent
    # For example, if index [2,5] has the value (2,4), then there is no wall between (2,5) and (2,4)
    #
    def generate(self, num_rows, num_cols):
        self.maze = [[None for i in range(0, num_cols, 1)] for j in range(0, num_rows, 1)]

        # Straightforward implementation of the depth-first search maze generation algorithm
        # https://en.wikipedia.org/wiki/Maze_generation_algorithm
        #
        # Start by setting top-left corner as current point
        #
        current_point=(0,0) 
        self.maze[0][0] = current_point
        maze_stack = [current_point]
        unvisited_spaces = (num_rows * num_cols) - 1

        # Keep iterating until all spaces have are joined to at least one neighbor
        #
        while (unvisited_spaces > 0):

            # Count the number of unvisited neighbors to the current point
            #
            current_unvisited_neighbors = self.__get_unvisited_neighbors(current_point)

            # If all are visited, backtrack until we find a visited point with unvisited neighbors
            #
            if (len(current_unvisited_neighbors) == 0):
                current_point = maze_stack.pop()

            # If some are unvisited, randomly pick one to move to
            # Mark that block as adjacent to current_point
            else:
                next_point = random.choice(current_unvisited_neighbors) 
                self.maze[next_point[0]][next_point[1]] = current_point
                maze_stack.append(current_point)
                current_point = next_point
                unvisited_spaces -= 1

    def set_start_point(self, start_point):
        self.start_point = start_point

    def get_start_point(self):
      return self.start_point

    def set_end_point(self, end_point):
        self.end_point = end_point

    def get_end_point(self):
        return self.end_point

    def get_maze(self):
        return self.maze

    def set_path(self, path):
        self.path = path
    
    def set_selected_block(self, selected_block_coords):
        self.selected_block = selected_block_coords

    def clear_selected_block(self):
        self.selected_block = None

    def get_block_size(self):
        return self.block_size

    # Generates an image to graphically represent the maze
    #
    def generate_image(self):
        if self.maze is None:
            raise ValueError('Maze is not initialized')

        # First, draw the background
        #
        image = self.__initialize_image()

        # The order of the drawing is important - otherwise, we can get weird graphical artifacts
        #
        if (self.path is not None):
            image = self.__draw_path(image, self.path)
        if (self.selected_block is not None):
            image = self.__draw_selected_block(image, self.selected_block)
        if (self.start_point is not None):
            image = self.__draw_start(image, self.start_point)
        if (self.end_point is not None):
            image = self.__draw_end(image, self.end_point)

        # Draw all of the walls
        #
        image = self.__draw_all_walls(image)
        
        # If two blocks are adjacent, remove the walls between them
        #
        for y in range(0, len(self.maze), 1):
            for x in range(0, len(self.maze[0]), 1):
                # 0, 0 is the starting point, so it has no walls to remove
                #
                if (x != 0 or y != 0):
                    image = self.__remove_walls(image, (y,x), self.maze[y][x])
        
        return image

    # Private members
    #

    # Given a block in a maze, determine how many of its neighbors are 'None'
    # This is used to generate the maze
    #
    def __get_unvisited_neighbors(self, point):
        unvisited_neighbors = []
        for offsets in [(0, -1), (0, 1), (1, 0), (-1, 0)]:
            y_ind = point[0] + offsets[0]
            x_ind = point[1] + offsets[1]

            if y_ind >= 0 and y_ind < len(self.maze):
                if x_ind >= 0 and x_ind < len(self.maze[0]):
                    if self.maze[y_ind][x_ind] is None:
                        unvisited_neighbors.append((y_ind, x_ind))
        return unvisited_neighbors

    # Initializes the image to a constant color
    #
    def __initialize_image(self):
        image = np.full((len(self.maze) * self.block_size, len(self.maze[0]) * self.block_size, 3), self.BACKGROUND_COLOR_INT, dtype=np.uint8)
        return image

    # Draws all of the possible maze walls on the board
    #
    def __draw_all_walls(self, image):
        for y in range(0, image.shape[0], 1):
            for x in range(0, image.shape[1], 1):
                is_wall = False
                if y % self.block_size == 0 or y % self.block_size == self.block_size-1:
                    is_wall = True
                elif x % self.block_size == 0 or x % self.block_size == self.block_size-1:
                    is_wall = True
                if is_wall:
                    image[y][x] = self.WALL_COLOR
        return image

    # Erases a wall between two points
    #
    def __remove_walls(self, image, first_point, second_point):
        if (first_point[0] == second_point[0] and first_point[1] == second_point[1]):
            raise ValueError('Duplicate points: {0} and {1}'.format(first_point, second_point))

        # Vertical alignment
        #
        if (first_point[0] == second_point[0]):
            if (first_point[1] > second_point[1]):
                image = self.__remove_left_wall(image, first_point)
                image = self.__remove_right_wall(image, second_point)
            elif (first_point[1] < second_point[1]):
                image = self.__remove_right_wall(image, first_point)
                image = self.__remove_left_wall(image, second_point)
        
        #Horizontal alignment
        #
        elif (first_point[1] == second_point[1]):
            if (first_point[0] > second_point[0]):
                image = self.__remove_top_wall(image, first_point)
                image = self.__remove_bottom_wall(image, second_point)
            elif (first_point[0] < second_point[0]):
                image = self.__remove_bottom_wall(image, first_point)
                image = self.__remove_top_wall(image, second_point)
        else:
            raise ValueError('points {0} and {1} cannot be connected.'.format(first_point, second_point))
        return image

    # Removes the wall on the top of a block
    #
    def __remove_top_wall(self, image, point):
        y_px = (point[0]) * self.block_size
        x_start = (point[1] * self.block_size) + 1
        x_end = ( (point[1]+1) * self.block_size ) - 1

        color = self.BACKGROUND_COLOR
        if self.path is not None and point in self.path:
            color = self.PATH_COLOR

        while x_start < x_end:
            image[y_px][x_start] = color
            x_start += 1
        return image

    # Removes the wall on the bottom of a block
    #
    def __remove_bottom_wall(self, image, point):
        y_px = ((point[0]+1) * self.block_size) - 1
        x_start = (point[1] * self.block_size) + 1
        x_end = ((point[1]+1) * self.block_size) - 1

        color = self.BACKGROUND_COLOR
        if self.path is not None and point in self.path:
            color = self.PATH_COLOR

        while x_start < x_end:
            image[y_px][x_start] = color
            x_start += 1
        return image

    # Removes the wall on the left of a block
    #
    def __remove_left_wall(self, image, point):
        x_px = (point[1]) * self.block_size
        y_start = (point[0] * self.block_size) + 1
        y_end = ( (point[0]+1) * self.block_size ) - 1
        
        color = self.BACKGROUND_COLOR
        if self.path is not None and point in self.path:
            color = self.PATH_COLOR

        while y_start < y_end:
            image[y_start][x_px] = color
            y_start += 1
        return image

    # Removes the wall on the right of a block
    #
    def __remove_right_wall(self, image, point):
        x_px = ((point[1] + 1) * self.block_size) - 1
        y_start = (point[0] * self.block_size) + 1
        y_end = ((point[0]+1) * self.block_size) - 1

        color = self.BACKGROUND_COLOR
        if self.path is not None and point in self.path:
            color = self.PATH_COLOR

        while y_start < y_end:
            image[y_start][x_px] = color
            y_start += 1
        return image
    
    # Draws the icon for the starting point for the agent
    #
    def __draw_start(self, image, point):
        return self.__draw_square_in_center_of_patch(image, point, self.START_COLOR)

    # Draws the icon for the ending point for the agent
    #
    def __draw_end(self, image, point):
        return self.__draw_square_in_center_of_patch(image, point, self.GOAL_COLOR)

    # Draws a small square in the center of the block
    #
    def __draw_square_in_center_of_patch(self, image, point, color):
        center_y_pixel = (point[0] * self.block_size) + (self.block_size // 2)
        center_x_pixel = (point[1] * self.block_size) + (self.block_size // 2)

        min_x = center_x_pixel - 3
        max_x = center_x_pixel + 3
        min_y = center_y_pixel - 3
        max_y = center_y_pixel + 3
        
        return self.__draw_filled_rectangle(image, min_x, min_y, max_x, max_y, color)

    def __draw_path(self, image, path):
        for path_node in path:
            min_x = path_node[1] * self.block_size
            min_y = path_node[0] * self.block_size
            max_x = (path_node[1] + 1) * self.block_size
            max_y = (path_node[0] + 1) * self.block_size

            image = self.__draw_filled_rectangle(image, min_x, min_y, max_x, max_y, self.PATH_COLOR)
        return image

    
    def __draw_selected_block(self, image, selected_block):
        min_x = selected_block[1] * self.block_size
        min_y = selected_block[0] * self.block_size
        max_x = (selected_block[1] + 1) * self.block_size
        max_y = (selected_block[0] + 1) * self.block_size

        return self.__draw_filled_rectangle(image, min_x, min_y, max_x, max_y, self.SELECTION_COLOR)

    def __draw_filled_rectangle(self, image, min_x, min_y, max_x, max_y, color):
        for y in range(min_y, max_y, 1):
            for x in range(min_x, max_x, 1):
                image[y][x] = color
        return image
        
