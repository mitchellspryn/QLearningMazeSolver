import sys
import numpy as np
import maze
import random

# The main learning agent
# Given a maze, learns the optimal path from each starting point via Q-Learning
# For more info on this algorithm, check out the blog post here: https://github.com/mitchellspryn/QLearningMazeSolver
#
class QLearnAgent():
    def __init__(self):
      # Reward matrix
      # R(A(s, s')) in the blog post
      # s indexes the rows, s' the columns
      # So R(A(s,s')) = R[s][s']
      self.R = None

      # State matrix 
      # Q(A(s,s')) in the blog post
      # s indexes the rows, s' the columns
      # So Q(A(s,s')) = Q[s][s']
      self.Q = None

      self.num_columns = None
      self.end_state = None
      self.num_states = None
      self.next_states = {}
      self.trained = False

    # Public Members
    #
    def is_trained(self):
      return self.trained

    # Initializes the learning matricies
    # Q matrix -> zeros
    # R matrix -> 0 if connected, 1 if goal, -1 otherwise
    #
    def initialize(self, maze):
      if maze is None:
        return
      maze_fields = maze.get_maze()
      end_point = maze.get_end_point()
      if end_point is None:
        return
      self.num_states = len(maze_fields)*len(maze_fields[0])
      self.num_columns = len(maze_fields[0])

      # Begin by initializing the reward matrix to zero connectivity
      #
      self.R = np.full((self.num_states, self.num_states), -1, dtype=np.float64)

      # For each point in the maze, connect it to its parent
      #
      for y in range(0, len(maze_fields), 1):
        for x in range(0, len(maze_fields[0]), 1):
          first_point = (y,x)
          second_point = maze_fields[y][x]

          # States may not point to themselves
          #
          if (first_point[0] != second_point[0] or first_point[1] != second_point[1]):
            first_state = self.__maze_dims_to_state(first_point[0], first_point[1])
            second_state = self.__maze_dims_to_state(second_point[0], second_point[1])

            # Create a hashtable for neighboring states to avoid continuous iteration over matrix
            #
            if first_state not in self.next_states:
              self.next_states[first_state] = []
            self.next_states[first_state].append(second_state)

            if second_state not in self.next_states:
              self.next_states[second_state] = []
            self.next_states[second_state].append(first_state)

            self.R[first_state][second_state] = 0
            self.R[second_state][first_state] = 0

      # Set terminal state to point to self, as well as all neighbors to point to it
      #
      self.end_state = self.__maze_dims_to_state(end_point[0], end_point[1])
      for i in range(0, self.num_states, 1):
        if self.R[i][self.end_state] != -1:
          self.R[i][self.end_state] = 1.0
      self.R[self.end_state][self.end_state] = 1.0

      # Initialize Q matrix to zeros
      #
      self.Q = np.full((self.num_states, self.num_states), 0.0)
      self.trained = False

    # Trains the agent
    # initialize() should have been called before this function is called
    #
    def train(self, gamma, min_change_per_epoch):
      print('Training...')
      epoch_iteration = 0
      while True:
        previous_q = np.copy(self.Q)

        # Consider multiple states per epoch.
        # Early termination can happen if same state is picked twice
        #
        for i in range(0, 10, 1):
          # Pick a random starting position
          #
          current_state = random.randint(0, self.num_states-1)

          # Keep iterating until goal is reached
          #
          while(current_state != self.end_state):

            # Pick a random next state
            #
            possible_next_states = self.next_states[current_state]
            next_state = random.choice(possible_next_states)

            # Get the outgoing states from next state.
            # Compute the max Q values of those outgoing states
            #
            max_q_next_state = -1
            next_next_states = self.next_states[next_state]
            for next_next_state in next_next_states:
              max_q_next_state = max([max_q_next_state, self.Q[next_state][next_next_state]])
            
            # Set Q value for transition from current->next state via bellman equation
            #
            self.Q[current_state][next_state] = self.R[current_state][next_state] + (gamma * max_q_next_state)

            # Move to next state
            #
            current_state = next_state


        # Normalize the Q matrix to avoid overflow
        #
        self.Q = self.Q / np.max(self.Q)

        #Check stopping criteria
        diff = np.sum(np.abs(self.Q - previous_q))
        print('In epoch {0}, difference is {1}'.format(epoch_iteration, diff))
        if (diff < min_change_per_epoch):
          break

        epoch_iteration += 1

      # Agent is trained!
      #
      self.trained = True

    # Given a starting state, predict the optimal path to the ending state
    # This should be called only on a trained agent
    def solve(self, starting_state):
      if not self.trained:
        return []

      # The first point in the path is the starting state
      # Translate from (y,x) coordinates into state index
      #
      path = [starting_state]
      current_state = self.__maze_dims_to_state(starting_state[0], starting_state[1])

      # Keep going until we reach the goal 
      # (or we've visited every spot - safety check to ensure that we don't get stuck in infinite loop)
      #
      while(current_state != self.end_state and len(path) < self.num_states):

        # For all of the next states, determine the state with the highest Q value
        #
        possible_next_states = self.next_states[current_state]
        best_next_state = possible_next_states[0]
        best_next_state_reward = self.Q[current_state][best_next_state]

        for i in range(1, len(possible_next_states), 1):
          potential_next_state = possible_next_states[i]
          if (self.Q[current_state][potential_next_state] > best_next_state_reward):
            best_next_state = potential_next_state
            best_next_state_reward = self.Q[current_state][potential_next_state]
        
        # Move to that state, and add to path
        #
        current_state = best_next_state
        path.append(self.__state_to_maze_dims(current_state))
        
      return path

    # Private Members
    #

    # Converts (y,x) coordinates to a numerical state
    #
    def __maze_dims_to_state(self, y, x):
      return (y*self.num_columns) + x

    # Converts a numerical state to (y,x) coordinates
    #
    def __state_to_maze_dims(self, state):
      y = int(state // self.num_columns)
      x = state % self.num_columns
      return (y,x)
