import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GdkPixbuf

import maze
import qlearn_agent

# The main event handler for the program
# The functions here get called when buttons are clicked in the GUI
#
class MainWindowController:
    def __init__(self, builder):
        self.maze = None

        # Set these to the default values set in the Glade GUI
        #
        self.maze_size = (6,6)
        self.builder = builder
        self.gamma = 0.8
        self.maze_selected_block = None
        self.agent = None

    def GammaTextEntryValueChanged(self, text_entry):
        self.gamma = text_entry.get_text()

    def NumberOfColumnsAdjustmentValueChanged(self, adjustment):
        self.maze_size = (self.maze_size[0], int(adjustment.get_value()))

    def NumberOfRowsAdjustmentValueChanged(self, adjustment):
        self.maze_size = (int(adjustment.get_value()), self.maze_size[1])

    def GenerateNewMazeButtonPressed(self, button):
        self.maze = maze.Maze()
        self.maze.generate(self.maze_size[0], self.maze_size[1])
        self.__reset_agent()
        self.__redraw_maze()

    def SetStartingPointButtonPressed(self, button):
        if (self.maze_selected_block is not None):
            self.maze.set_start_point(self.maze_selected_block)
            self.maze.clear_selected_block()
            self.maze_selected_block = None
            self.maze.set_path(None)
            self.__redraw_maze()

    def SetEndingPointButtonPressed(self, button):
        if (self.maze_selected_block is not None):
            self.maze.set_end_point(self.maze_selected_block)
            self.maze.clear_selected_block()
            self.maze_selected_block = None
            self.maze.set_path(None)
            self.__reset_agent()
            self.__redraw_maze()

    def ResetAgentButtonPressed(self, button):
        self.__reset_agent() 
        self.maze.set_path(None)
        self.maze.set_start_point(None)
        self.maze.set_end_point(None)
        self.__redraw_maze()

    def TrainAgentButtonPressed(self, button):
        try:
            gamma = float(self.gamma)
            if (gamma < 0 or gamma > 1):
                raise ValueError('gamma')
        except:
            self.__show_popup('Error: gamma must be a value on the range [0, 1]')
            return

        if self.maze is None:
            self.__show_popup('Error: Maze is not generated. Please generate maze.')
            return

        if self.maze.get_end_point() is None:
            self.__show_popup('Error: End point not specified. Please specify end point by selecting a block and clicking "Set Endpoint"')
            return

        if self.agent is None:
            self.agent = qlearn_agent.QLearnAgent()
            self.agent.initialize(self.maze)

        self.agent.train(gamma, 0.001)
        self.__show_popup('Agent successfully trained.')

    def RunAgentButtonPressed(self, button):
        if (self.agent is None or not self.agent.is_trained()):
            self.__show_popup('Error: Agent not trained. Please train the agent before attempting to run it')
            return

        start_point = self.maze.get_start_point()
        if start_point is None:
            self.__show_popup('Error: Start point not specified. Please specify start point by selecting a block and clicking "Set Starting Point"')
            return

        path = self.agent.solve(start_point)
        self.maze.set_path(path)

        self.__redraw_maze()

    # Find the block that the user clicked on and highlight it
    #
    def MazeImageEventBoxPressed(self, event_box, click_event):
        block_size = self.maze.get_block_size()
        self.maze_selected_block = (int(click_event.y // block_size), int(click_event.x // block_size))
        self.maze.set_selected_block(self.maze_selected_block)
        self.__redraw_maze()

    def __reset_agent(self):
      if self.maze is None:
        self.agent = None
      else:
        self.agent = qlearn_agent.QLearnAgent()
        self.agent.initialize(self.maze)

    # Draws the maze image in the GUI
    #
    def __redraw_maze(self):
        # Note: new_from_data() has a memory corruption issue, and gives garbage image.
        # Below method is not terribly efficient, but in practice, it's fast enough.
        # 
        image = self.maze.generate_image()
        header = bytes('P6 {0} {1} 255 '.format(image.shape[1], image.shape[0]), 'ascii')
        iloader = GdkPixbuf.PixbufLoader.new_with_type('pnm')
        iloader.write(header)
        iloader.write(bytes(image))
        pixbuf = iloader.get_pixbuf()
        iloader.close()
        image_ref = builder.get_object('MazeImage')
        image_ref.set_from_pixbuf(pixbuf)

    # Shows a small popup window with a message to the user
    #
    def __show_popup(self, message):
        md = Gtk.MessageDialog()
        md.set_markup(message)
        md.run()
        md.destroy()


# The main entry point of the program
#
# Builds the window, attaches the MainWindowController, and shows the window
#
builder = Gtk.Builder()
builder.add_from_file('main_window.glade')

controller = MainWindowController(builder)
builder.connect_signals(controller)

window = builder.get_object('MainWindow')
window.connect('destroy', Gtk.main_quit)
window.show_all()

Gtk.main()
