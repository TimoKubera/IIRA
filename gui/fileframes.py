"""
TODO
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.font as font
""" Standardbibliothek Imports """

from gui.containerframe import ContainerFrame
from gui.helperframes import ScaleHelpFrame, ImportHelpFrame
from core.fileinteraction import FileValidation
""" Lokale Imports """

import pandas as pd
""" Third Party Imports """


class ScaleFrame(ContainerFrame):
    def __init__(self, container):
        super().__init__(container)
        self.scale_types = ["nominal", "ordinal", "intervall", "ratio"]
        self.weights = ["identity", "linear", "quadratic", "bipolar", "circular", "ordinal", "radial", "ratio"]

        self.selected_scale = tk.StringVar()

        self.selected_weight = tk.StringVar()

        container.style.configure("FileFrame.TMenubutton", font="Arial 18", foreground="black", width=10)

        # GUI-Elemente
        self.center_container = ttk.Frame(self, style="Card", padding=(5, 6, 7, 8))
        next_button = ttk.Button(self.center_container, text="Weiter", style="FileFrame.TButton",
                                    command=self.next_cmd)
        # Platzierungen
        self.menu_bar.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.center_container.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)

        tk.Frame(self.center_container).grid(row=3, column=0, columnspan=3) # Separator, der den Button ganz unten erscheinen lässt.
        next_button.grid(row=4, column=0, columnspan=3)

        # Responsive Design
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self.center_container.columnconfigure(0, weight=1)
        self.center_container.rowconfigure(0, weight=1)
        self.center_container.rowconfigure(1, weight=1)
        self.center_container.rowconfigure(2, weight=1)
        self.center_container.rowconfigure(3, weight=1)



    def populate_frame(self, mode):
        if mode == "analyse":
            self.populate_scaletype()
            self.populate_weights()
        else:
            self.populate_scaletype()
    
    def populate_weights(self):
            # GUI-Elemente
            weights_label = ttk.Label(self.center_container, font="Arial 22",
                                    text="Gewichte")
            weights_menu = ttk.OptionMenu(self.center_container, self.selected_weight, "identity", *self.weights,
                                        style="FileFrame.TMenubutton")
            
            infolabel_container = ttk.Frame(self.center_container)
            weights_infolabel = ttk.Label(infolabel_container, font="Arial 18",
                                    text="• Legen fest in welchem Verhältnis die Kategorien zueinander stehen.")
            identity_infolabel = ttk.Label(infolabel_container, font="Arial 18",
                                    text="• Identity entspricht den ungewichteten Metriken.\n  Übereinstimmung nur dann, wenn exakt die gleiche\n  Kategorie ausgewählt wurde. ")
            linear_infolabel = ttk.Label(infolabel_container, font="Arial 18",
                                    text="• Üblich sind die Gewichte identity, linear, oder quadratic.")
            #quadratic_infolabel = ttk.Label(infolabel_container, font="Arial 18",
            #                        text="• bei quadratischer ...")
            
            # Platzierungen
            weights_label.grid(row=0, column=1, pady=10)
            weights_menu.grid(row=1, column=1, pady=20)
            infolabel_container.grid(row=2, column=1, pady=10)

            weights_infolabel.pack(fill="x", pady=5)
            identity_infolabel.pack(fill="x", pady=5)
            linear_infolabel.pack(fill="x", pady=5)
            #quadratic_infolabel.pack(fill="x", pady=5)

            # Responsive Design
            self.center_container.columnconfigure(0, weight=1)

    def populate_scaletype(self):
            # GUI-Elemente
            scale_format_label = ttk.Label(self.center_container, font="Arial 22",
                                    text="Skalenformat")
            scale_menu = ttk.OptionMenu(self.center_container, self.selected_scale, "nominal", *self.scale_types,
                                        style="FileFrame.TMenubutton")
            
            infolabel_container = ttk.Frame(self.center_container)
            nominal_infolabel = ttk.Label(infolabel_container, font="Arial 18",
                                    text="• Nominalskala: Objekte werden nur mit Namen versehen.")
            ordinal_infolabel = ttk.Label(infolabel_container, font="Arial 18",
                                    text="• Ordinalskala: Es gibt zusätzlich eine Äquivalenz- und\n  Ordungsrelation.")
            intervall_infolabel = ttk.Label(infolabel_container, font="Arial 18",
                                    text="• Intervallskala: Zusätzlich sind Abstände/Intervall definierbar.")
            rational_infolabel = ttk.Label(infolabel_container, font="Arial 18",
                                    text="• Rationalskala: Es gibt zusätzlich einen Nullpunkt.")
            
            # Platzierungen
            scale_format_label.grid(row=0, column=0, pady=10)
            scale_menu.grid(row=1, column=0, pady=20)
            infolabel_container.grid(row=2, column=0, pady=10)

            nominal_infolabel.pack(fill="x", pady=5)
            ordinal_infolabel.pack(fill="x", pady=5)
            intervall_infolabel.pack(fill="x", pady=5)
            rational_infolabel.pack(fill="x", pady=5)

            # Responsive Design
            self.center_container.columnconfigure(0, weight=1)
    
    def next_cmd(self):
        self.container.scale_format = self.selected_scale.get()
        if self.container.mode == "analyse":
            self.container.weights = self.selected_weight.get()
        
        self.container.frames["FileFrame"].update_frame()
        self.container.show_frame("FileFrame")
    
    def help_cmd(self,event=None):
        # Jedes Frame erzeugt ein HelpFrame mit eigenen Inhalten.
        # Wird in den vererbten Klassen implementiert.
        ScaleHelpFrame(self.container)

    def update_frame(self):
        for widget in self.center_container.winfo_children():
            # Alte widgets ggf. löschen, falls bereits eine Auswahl erfolgt ist.
            # und der User erneut Analyse- bzw. Rate auswählt, nachdem er über den Home
            # Button zurück in den MainFrame zurückgekehrt ist.
            if not isinstance(widget, tk.ttk.Button) and not isinstance(widget, tk.Frame):
                # Der Weiter-Button und der Separator-Frame sollen erhalten bleiben.
                widget.destroy()
        self.populate_frame(self.container.mode)


class FileFrame(ContainerFrame):
    #TODO Mit MainFrame zusammenfügen. Ggf. die Images etwas kleiner gestalten.
    def __init__(self, container):
        super().__init__(container)
        container.style.configure("FileFrame.TButton", font="Arial 18", foreground="black")

        # GUI-Elemente
        center_container = ttk.Frame(self, style="Card", padding=(5, 6, 7, 8))
        file_import_label = ttk.Label(center_container, font="Arial 20",
                                text="Datei importieren")
        accepted_formats_label = ttk.Label(center_container, font="Arial 20",
                                text="Es werden zwei Formate akzeptiert")
        
        format_1_label = ttk.Label(center_container, font="Arial 20",
                                text="Format 1:")
        
        self.format_1_container = ttk.Frame(center_container)
        self.format_1_bulletlist_container = ttk.Frame(center_container)
    
        format_2_label = ttk.Label(center_container, font="Arial 20",
                                text="Format 2:")

        self.format_2_container = ttk.Frame(center_container)
        self.format_2_bulletlist_container = ttk.Frame(center_container)

        self.format_1_2_bulletlist_container = ttk.Frame(center_container)

        select_file_button = ttk.Button(center_container, text="Datei auswählen", style="FileFrame.TButton",
                                        command=lambda: self.select_file(container))

        # Platzierungen
        center_container.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)
        self.menu_bar.grid(row=0, column=0, columnspan=2, sticky="nsew")

        file_import_label.grid(row=0, column=0, columnspan=3, pady=10)
        accepted_formats_label.grid(row=1, column=0, columnspan=3, pady=10)

        format_1_label.grid(row=2, column=0, pady=15)
        format_2_label.grid(row=2, column=2, pady=15)

        self.format_1_container.grid(row=3, column=0, padx=15)
        ttk.Frame(center_container).grid(row=2, rowspan=2, column=1, sticky="nsew") # Trennt format_1_container und format_2_container voneinander.
        self.format_2_container.grid(row=3, column=2, padx=15)

        self.format_1_bulletlist_container.grid(row=4, column=0, padx=15, pady=(15, 0))

        self.format_2_bulletlist_container.grid(row=4, column=2, padx=15, pady=(15, 0))

        self.format_1_2_bulletlist_container.grid(row=5, column=0, columnspan=3)

        ttk.Frame(center_container).grid(row=6, column=0, columnspan=3) # Separator, der den Button ganz unten erscheinen lässt.
        select_file_button.grid(row=7, column=0, columnspan=3)

        # Responsive Design
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        center_container.columnconfigure(1, weight=1)
        center_container.rowconfigure(6, weight=1)


    def populate_format_preview(self, format_container):
        if self.container.scale_format == "nominal" or self.container.scale_format == "ordinal":
            if format_container == self.format_1_container:
                headings = ["Categories", "Rater ID", "Sentiment Analysis\nis nice!", "If I run the code in\nthe GUI, it just hangs."]
                content = [["positive", "Alice", "positive", "neutral"],
                            ["neutral", "Bob", "positive", "negative"],
                            ["negative"]]
            
                self.create_table(self.format_1_container, headings, content)

                rater_id_infolabel = ttk.Label(self.format_1_bulletlist_container, font="Arial 18",
                        text="• Header \"Rater ID\" muss in Datei vorkommen.")
                rater_id_infolabel.pack(fill="x", pady=5)
            else:
                headings = ["Categories", "Subject", "Alice", "Bob"]
                content = [["positive", "Sentiment Analysis\nis nice!", "positive", "positive"],
                            ["neutral", "If I run the code in\nthe GUI, it just hangs.", "neutral", "negative"],
                            ["negative"]]
            
                self.create_table(self.format_2_container, headings, content)

                text_infolabel = ttk.Label(self.format_2_bulletlist_container, font="Arial 18",
                                        text="• Header \"Subject\" muss in Datei vorkommen.")
                text_infolabel.pack(fill="x", pady=5)
                
                categories_infolabel = ttk.Label(self.format_1_2_bulletlist_container, font="Arial 18",
                                        text="• Header \"Categories\" in beiden Formaten.")
                
                if self.container.scale_format == "nominal":
                    info_txt = "• Kategorienamen angeben; hier: positive, neutral, negative."
                else:
                    info_txt = "• Kategorienamen in sortierter Reihenfolge angeben.\n  (aufsteigend, oder absteigend)"

                category_entries_infolabel = ttk.Label(self.format_1_2_bulletlist_container, font="Arial 18",
                                        text=info_txt)
                black_headers_infolabel = ttk.Label(self.format_1_2_bulletlist_container, font="Arial 18",
                                        text="• Spalten mit schwarzen Header werden automatisch erkannt.")
                other_columns_infolabel = ttk.Label(self.format_1_2_bulletlist_container, font="Arial 18",
                                        text="• Andere Spalten werden ignoriert.")

                categories_infolabel.pack(fill="x", pady=5)
                category_entries_infolabel.pack(fill="x", pady=5)
                black_headers_infolabel.pack(fill="x", pady=5)
                other_columns_infolabel.pack(fill="x", pady=5)
        else:
            # Intervall, oder rationaler Skalentyp
            if format_container == self.format_1_container:
                headings = ["Rater ID", "Herzfrequenz\n24.01. 16:30", "Herzfrequenz\n24.01. 17:00"]
                content = [["Alice", "121.5", "89"],
                            ["Bob", "123", "75"]]
            
                self.create_table(self.format_1_container, headings, content)

                rater_id_infolabel = ttk.Label(self.format_1_bulletlist_container, font="Arial 18",
                        text="• Header \"Rater ID\" muss in Datei vorkommen.")
                rater_id_infolabel.pack(fill="x", pady=15)
            else:
                headings = ["Subject", "Alice", "Bob"]
                content = [["Herzfrequenz\n24.01. 16:30", "121.5", "123"],
                            ["Herzfrequenz\n24.01. 17:00", "89", "75"]]
            
                self.create_table(self.format_2_container, headings, content)

                text_infolabel = ttk.Label(self.format_2_bulletlist_container, font="Arial 18",
                                        text="• Header \"Subject\" muss in Datei vorkommen.")
                text_infolabel.pack(fill="x", pady=15)

                other_columns_infolabel = ttk.Label(self.format_1_2_bulletlist_container, font="Arial 18",
                                        text="• Spalten die davor auftauchen werden ignoriert.")
                
                subjects_infolabel = ttk.Label(self.format_1_2_bulletlist_container, font="Arial 18",
                                        text="• Danach ausschließlich Spalten mit den Messergebnissen.")
                
                other_columns_infolabel.pack(fill="x", pady=15)
                subjects_infolabel.pack(fill="x", pady=15)


    # Button commands
    def select_file(self, container):
        filename = tk.filedialog.askopenfilename(filetypes=[
            ("Excel files", ".xlsx .xls"), 
            ("Libreoffice Calc files", ".ods"),
            ("Csv files", ".csv")
            ])

        if filename == "":
            # Keine Datei ausgewählt.
            return

        try:
            container.filevalidation = FileValidation(filename, self.container.scale_format)
            # App mit den Daten vom file_validator füllen
            container.categories = container.filevalidation.categories
            container.rater_ids = container.filevalidation.rater_ids
            container.text = container.filevalidation.text
            container.formatted_text = container.filevalidation.formatted_text
            container.labels = container.filevalidation.labels
        except:
            messagebox.showerror(title="Error", message="Fehler beim importieren der Datei. Auf passendes Format geachtet?")
            return

        if container.mode == "analyse":
            container.frames["AnalyseFrame"].update_frame()
            container.show_frame("AnalyseFrame")
        elif container.mode == "rate":
            result = messagebox.askyesno(title="Reihenfolge", message="Soll die Reihenfolge der Bewertungsobjekte zufällig sein?")
            if result:
                container.frames["RateFrame"].update_frame(mode="do")
            else:
                container.frames["RateFrame"].update_frame()
            container.show_frame("RateFrame")
        else:
            #TODO Fehlermeldung / Fehlerframe ausgeben
            container.show_frame("MainFrame")

    def help_cmd(self,event=None):
        # Jedes Frame erzeugt ein HelpFrame mit eigenen Inhalten.
        # Wird in den vererbten Klassen implementiert.
        ImportHelpFrame(self.container)

    def update_frame(self):
        # Widgets aus vorheriger Session löschen, falls User über Home-Button den Frame erneut öffnet.
        for widget in self.format_1_container.winfo_children():
            widget.destroy()
        for widget in self.format_2_container.winfo_children():
            widget.destroy()
        for widget in self.format_1_bulletlist_container.winfo_children():
            widget.destroy()
        for widget in self.format_2_bulletlist_container.winfo_children():
            widget.destroy()
        for widget in self.format_1_2_bulletlist_container.winfo_children():
            widget.destroy()

        # Frames neu befüllen
        self.populate_format_preview(self.format_1_container)
        self.populate_format_preview(self.format_2_container)