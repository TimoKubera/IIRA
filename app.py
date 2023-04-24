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
    Die App-Klasse is für die Steuerung der Anwendung verantwortlich.

    Die App-Klasse erbt von der TK-Klasse und stellt bei der Initialisierung das
    Root-Fenster zur Verfügung.
    Zusätzlich übernimmt die Klasse die Steuerung der Anwendung, um weitere
    GUI-Elemente anzeigen zu lassen und mit dem Nutzer zu interagieren.

    Attributes:
        title (str): Titel der Anwendung. Wird oben mittig im Fensterrahmen angezeigt.
        geoometry (str): Größe des Fensters beim Aufrufen der App. Kann vom Nutzer
                         angepasst werden.
        rowconfigure (int, int): Das erste Integer-Argument gibt an welche Reihe im Grid-Layout-
                                Manager ausgewählt werden soll. Das zweite Integer-Argument gibt ein
                                Gewicht an. Gewiche größer als 0 signalisieren, dass die zusätzlich
                                verfügbaren Platz ausfüllen soll, wenn die Fenstergröße verändert wird.
                                Größere Gewiche werden dabei bevorzugt behandelt.
        colconfigure (int, int): Analog zu rowconfigure, allerdings bei spalenweiser Betrachtung.
        frames (dic): Enthält alle frames die in der Anwendung vorkommen können.
                      Beispielsweise das MainFrame, oder das RateFrame, wo unterschiedliche
                      Interaktionen ausgeführt werden können.
    TODO icons in die Beschreibung; Styles einfügen
    """

    def __init__(self):
        """
        Konstruktor-Methode der App-Klasse.
        """
        super().__init__()
        # Alle Icons die in der Anwendung angezeigt werden.
        self.load_icons()

        # Attribute die nicht mit tkinter zusammenhängen
        #TODO Dummy-Werte löschen
        self.filevalidation = None
        self.dbinteraction = DBInteraction(os.path.join(file_path, "data/internal_db.csv"))
        self.scale_format = ""      # Skalenformate sind nominal, ordinal, intervall und ratio.
        self.weights = ""
        
        #TODO löschen und auf Attribute von filevalidation zurückgreifen
        self.categories = []
        self.rater_ids = []
        self.text = []
        self.formatted_text = []
        self.labels = {} # Label pro Text und Rater

        # tkinter Attribute
        self.title("IIRA")
        #self.iconphoto(False, self.app_icon)
        self.geometry("1500x750")
        self.minsize(1450, 750)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.light_mode = True  #TODO Wert aus DB auslesen, soblad darkmode implementiert wurde.
        # ---> Inhalte die in den Frames angezeigt, oder gesetzt werden.
        self.mode = None # Speichert, ob der User analysieren, oder bewerten will.

        # Anwendungsweite Style-Konfigurationen
        # Import the tcl file
        self.tk.call("source", os.path.join(file_path, "data/themes/forest-light.tcl"))
        self.style = ttk.Style()

        # Set the theme with the theme_use method
        #TODO dark mode kann implementiert werden. Dafür auch Icon-Farben verändern
        self.style.theme_use("forest-light")

        self.frames = {} 
        self.init_frames()
        self.show_frame("MainFrame")
    
    def show_frame(self, frame_name):
        """
        Methode zum Wechseln des Frames der aktuell angezeigt wird.

        Args:
            frame_name (ttk.Frame): Der Frame, der angezeigt werden soll.
        """
        frame = self.frames[frame_name]
        frame.tkraise()
    
    def load_icons(self):
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
        
        #TODO Für darkmode anpassen, bzw löschen
        self.light_icon = ImageTk.PhotoImage(file=os.path.join(file_path, "data/icons/light_mode_32px.png"))
        self.dark_icon = ImageTk.PhotoImage(file=os.path.join(file_path, "data/icons/dark_mode.png"))
        self.unchecked_icon = ImageTk.PhotoImage(file=os.path.join(file_path, "data/themes/forest-light/check-unsel-accent.png"))
        self.checked_icon = ImageTk.PhotoImage(file=os.path.join(file_path, "data/themes/forest-light/check-accent.png"))

    def init_root_frame(self, frame):
        frame.grid(row=0, column=0, sticky="nsew")
    
    def init_frames(self):
        """ 
        Initialisiert alle Frames, die es in der Software gibt. 
        Die Frames werden in einem Dictionary gespeichert, um mit der show_frame-Funktion zwischen den Frames
        wechseln zu können.
        """
        for frame in self.frames:
            # Löscht den Inhalt der frames.
            # Ist beim startup der Applikation nicht von Bedeutung und wird dann übersprüngen, weil
            # self.frames leer ist. Die Funktion wird aber auch benutzt, wenn der Home-Button angeklickt wird.
            # In dem Fall werden die Fensterinhalte zurückgesetzt. 
            for widget in self.frames[frame].winfo_children():
                widget.destroy()

        # Frames initialisieren
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



if __name__ == "__main__":
  app = App()
  app.mainloop()