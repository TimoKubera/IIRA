"""
In diesem Modul wird die Steuerung der Anwendung realisiert.
Es ist das Top-Level-Modul der Anwendung und ruft alle weiteren Submodule auf.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html
"""
__author__ = "Timo Kubera"
__email__ = "timo.kubera@stud.uni-hannover.de"

import os
import tkinter as tk
from tkinter import ttk
""" Standardbibliothek Imports """

from gui.mainframe import MainFrame
from gui.fileframes import FileFrame, ScaleFrame
from gui.analyseframe import AnalyseFrame, ResultsFrame
from gui.rateframe import RateFrame
from core.fileinteraction import DBInteraction
""" Lokale Imports """

from PIL import ImageTk
""" Third Party Imports """

file_path = os.path.dirname(os.path.realpath(__file__))
""" Globale Variablen """

class App(tk.Tk):
    """
    The App class is responsible for controlling the application.

    The App class inherits from the TK class and provides the root window during initialization.
    In addition, the class takes over the control of the application to display further GUI elements and interact with the user.

    Attributes:
        title (str): Title of the application. Displayed at the top center of the window frame.
        geoometry (str): Size of the window when calling the app. Can be adjusted by the user.
        rowconfigure (int, int): The first integer argument indicates which row should be selected in the grid layout manager. The second integer argument gives a weight. Weights greater than 0 signal that the additional available space should be filled when the window size is changed. Larger weights are preferred.
        colconfigure (int, int): Analogous to rowconfigure, but with column-wise consideration.
        frames (dic): Contains all frames that can occur in the application. For example, the MainFrame, or the RateFrame, where different interactions can be executed.
    TODO icons in the description; Insert styles
    """

    def __init__(self):
        """
        Constructor method of the App class.
        """
        super().__init__()
        self.load_icons()

        self.filevalidation = None
        self.dbinteraction = DBInteraction(os.path.join(file_path, "data/internal_db.csv"))
        self.scale_format = ""
        self.weights = ""
        self.categories = []
        self.rater_ids = []
        self.text = []
        self.formatted_text = []
        self.labels = {}

        self.title("IIRA")
        self.geometry("1500x750")
        self.minsize(1450, 750)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.light_mode = True
        self.mode = None

        self.tk.call("source", os.path.join(file_path, "data/themes/forest-light.tcl"))
        self.style = ttk.Style()
        self.style.theme_use("forest-light")

        self.frames = {}
        self.init_frames()
        self.show_frame("MainFrame")

    def show_frame(self, frame_name):
        """
        Method to switch the frame that is currently displayed.

        Args:
            frame_name (ttk.Frame): The frame to be displayed.
        """
        frame = self.frames[frame_name]
        frame.tkraise()

    def load_icons(self):
        """
        Load all icons displayed in the application.
        """
        self.app_icon = ImageTk.PhotoImage(file=os.path.join(file_path, "data/icons/intrarater_512px.png"))
        self.file_select_icon = ImageTk.PhotoImage(file=os.path.join(file_path, "data/icons/file_select.png"))
        self.home_icon = ImageTk.PhotoImage(file=os.path.join(file_path, "data/icons/home_32px.png"))
        self.profile_icon = ImageTk.PhotoImage(file=os.path.join(file_path, "data/icons/profile_32px.png"))
        self.help_icon = ImageTk.PhotoImage(file=os.path.join(file_path, "data/icons/help_32px.png"))
        self.face_icon = ImageTk.PhotoImage(file=os.path.join(file_path, "data/icons/face_32px.png"))
        self.rate_icon = ImageTk.PhotoImage(file=os.path.join(file_path, "data/icons/rate.png"))
        self.analyse_icon = ImageTk.PhotoImage(file=os.path.join(file_path, "data/icons/analyse.png"))
        self.tooltip_icon = ImageTk.PhotoImage(file=os.path.join(file_path, "data/icons/tooltip-16px.png"))
        self.save_icon = ImageTk.PhotoImage(file=os.path.join(file_path, "data/icons/save_32px.png"))
        self.delete_icon = ImageTk.PhotoImage(file=os.path.join(file_path, "data/icons/delete_32px.png"))
        self.light_icon = ImageTk.PhotoImage(file=os.path.join(file_path, "data/icons/light_mode_32px.png"))
        self.dark_icon = ImageTk.PhotoImage(file=os.path.join(file_path, "data/icons/dark_mode.png"))
        self.unchecked_icon = ImageTk.PhotoImage(file=os.path.join(file_path, "data/themes/forest-light/check-unsel-accent.png"))
        self.checked_icon = ImageTk.PhotoImage(file=os.path.join(file_path, "data/themes/forest-light/check-accent.png"))

    def init_root_frame(self, frame):
        """
        Initialize the root frame.

        Args:
            frame (ttk.Frame): The frame to be initialized.
        """
        frame.grid(row=0, column=0, sticky="nsew")

    def init_frames(self):
        """
        Initialize all frames in the software.
        The frames are stored in a dictionary to be able to switch between the frames with the show_frame function.
        """
        for frame in self.frames:
            for widget in self.frames[frame].winfo_children():
                widget.destroy()

        main_frame = MainFrame(self)
        self.init_root_frame(main_frame)
        self.frames["MainFrame"] = main_frame

        scale_frame = ScaleFrame(self)
        self.init_root_frame(scale_frame)
        self.frames["ScaleFrame"] = scale_frame

        file_frame = FileFrame(self)
        self.init_root_frame(file_frame)
        self.frames["FileFrame"] = file_frame

        rate_frame = RateFrame(self)
        self.init_root_frame(rate_frame)
        self.frames["RateFrame"] = rate_frame

        restults_frame = ResultsFrame(self)
        self.init_root_frame(restults_frame)
        self.frames["ResultsFrame"] = restults_frame

        analyse_frame = AnalyseFrame(self)
        self.init_root_frame(analyse_frame)
        self.frames["AnalyseFrame"] = analyse_frame

def printSampleText():
    print("Hello World")

if __name__ == "__main__":
  app = App()
  app.mainloop()
