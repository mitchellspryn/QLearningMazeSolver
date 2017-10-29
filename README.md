# QLearnMazeSolver
An interactive maze solver using Q Learning. 

This application allows the generation of random mazes, and will solve them using the classical Q Learning RL algorithm. Read the (blog post)[http://www.mitchellspryn.com/2017/10/28/Solving-A-Maze-With-Q-Learning.html] for more information.

## Usage

`python3 main_window.py`

After clicking "Generate Maze," click on a square to select it and then click "Select Ending Point" to set the goal point. Click "Train Agent" to train the Q Learning agent. After training completed. you can click on a square to select it and click "Set Starting Point" to set the starting point. Click "Run Agent" to show the shortest path in blue. The starting point shows up in red, the ending point in green, and the path in blue:

![img](http://www.mitchellspryn.com/content/Q-Learn-Maze/large_maze_cropped.png)

## Other notes
This project was tested on Ubuntu Linux with python 3. The GTK tookit is required to be installed, as well as numpy. Should work on other platforms, but has not been tested.
