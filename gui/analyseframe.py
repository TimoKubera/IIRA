"""
TODO
"""

import tkinter as tk
from tkinter import ttk, messagebox
from math import isnan
""" Standardbibliothek Imports """

from gui.containerframe import ContainerFrame
from gui.helperframes import ScrollFrame, PrepAnalyseHelpFrame, ResultsHelpFrame
from core.create_analyses import CreateAnalyses
from core.fileinteraction import write_excel
from core.metrics import map_metrics
""" Lokale Imports """

selected_intra_ids = []
selected_inter_ids = []
selected_intra_metrics = []
selected_inter_metrics = []
""" Globale Variablen """

class AnalyseFrame(ContainerFrame):
    def __init__(self, container):
        # Metriken in Abhängigkeit vom Skalenformat festlegen
        self.metrics = []

        # Checkbutton-Variablen für die Metriken
        # Für Intrarater-Reliability
        self.intra_kappa = tk.IntVar()
        self.intra_fleiss_kappa = tk.IntVar()
        self.intra_alpha_coefficient = tk.IntVar()
        self.intra_ac = tk.IntVar()
        #self.intra_g_index = tk.IntVar()
        self.intra_icc = tk.IntVar()
        self.intra_metrics = {
            "Cohen's-|Conger's \u03BA": self.intra_kappa,
            "Fleiss' \u03BA": self.intra_fleiss_kappa,
            "Krippendorff's \u03B1": self.intra_alpha_coefficient,
            "Gwet's AC": self.intra_ac,
            #"G-Index": self.intra_g_index,
            "ICC": self.intra_icc
        }
        # Für Interrater-Reliability
        self.inter_kappa = tk.IntVar()
        self.inter_fleiss_kappa = tk.IntVar()
        self.inter_alpha_coefficient = tk.IntVar()
        self.inter_ac = tk.IntVar()
        #self.inter_g_index = tk.IntVar()
        self.inter_icc = tk.IntVar()
        self.inter_metrics = {
            "Cohen's-|Conger's \u03BA": self.inter_kappa,
            "Fleiss' \u03BA": self.inter_fleiss_kappa,
            "Krippendorff's \u03B1": self.inter_alpha_coefficient,
            "Gwet's AC": self.inter_ac,
            #"G-Index": self.inter_g_index,
            "ICC": self.inter_icc
        }

        # Diese Dictionaries werden in den populate-Funktionen befüllt, da die keys erst
        # zur Laufzeit ermittelt werden.
        self.intra_ids = {}
        self.inter_ids = {}


        super().__init__(container)
        # Styling
        container.style.configure("AnalyseFrame.TButton", font="Arial 15", foreground="black", width=15)

        # GUI-Elemente
        left_frame = ttk.Frame(self, style="Card", padding=(5, 6, 7, 8))
        right_frame = ttk.Frame(self, style="Card", padding=(5, 6, 7, 8))

        rater_label = ttk.Label(left_frame, font="Arial 20", text="1. Auswahl der Bewerter")

        self.rater_container = ScrollFrame(left_frame)

        self.toggle_ids = ttk.Button(left_frame, text="Alle auswählen", style="AnalyseFrame.TButton",
                                    command=lambda: self.toggle("id"))

        metrics_label = ttk.Label(right_frame, font="Arial 20", text="2. Auswahl der Metriken")
        self.metrics_container = ttk.Frame(right_frame)

        self.toggle_metrics = ttk.Button(right_frame, text="Alle auswählen", style="AnalyseFrame.TButton",
                                    command=lambda: self.toggle("metric"))

        start_btn = ttk.Button(self, text="Analyse Starten", style="AnalyseFrame.TButton", 
                                 command=lambda: self.analyse_start(container))

        # Platzierungen
        self.menu_bar.grid(row=0, column=0, sticky="nsew")
        left_frame.grid(row=1, column=0, sticky="nsew", padx=50, pady=50)
        right_frame.grid(row=1, column=1, sticky="nsew", padx=50, pady=50)

        rater_label.pack(side="top", padx=25, pady=10)
        self.rater_container.pack(side="top", fill="y", expand=True, padx=25, pady=50)
        self.toggle_ids.pack(side="bottom")

        metrics_label.pack(side="top", padx=25, pady=10)
        self.metrics_container.pack(side="top", padx=25, pady=50)
        self.toggle_metrics.pack(side="bottom")

        start_btn.grid(row=2, column=0, columnspan=2, pady=25)

        # Responsive Design
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    def analyse_start(self, container):
        """
        Die Funktion startet die Berechnungen für die Analyse.
        Zusätzlich wird Error handling implementiert, falls der User eine ungültige Auswahl an Metriken, 
        und/oder Bewertern vornimmt.
        """
        global selected_intra_metrics
        for metric in self.intra_metrics:
            if self.intra_metrics[metric].get() == 1 and metric not in selected_intra_metrics:
                selected_intra_metrics.append(metric)

        global selected_inter_metrics 
        for metric in self.inter_metrics:
            if self.inter_metrics[metric].get() == 1 and metric not in selected_inter_metrics:
                selected_inter_metrics.append(metric)

        global selected_intra_ids
        for id in self.intra_ids:
            if self.intra_ids[id].get() == 1 and id not in selected_intra_ids:
                selected_intra_ids.append(id)

        global selected_inter_ids
        for id in self.inter_ids:
            if self.inter_ids[id].get() == 1 and id not in selected_inter_ids:
                selected_inter_ids.append(id)
        
        if len(selected_inter_ids) == 1:
            messagebox.showerror("Ungültige Eingabe", "Es kann keine Interrater-Untersuchung von nur einer Bewerter-ID berechnet werden.")
            # Auswahl vom User rückgängig machen
            selected_intra_metrics = []
            selected_inter_metrics = []
            selected_intra_ids = []
            selected_inter_ids = []
            return
        elif len(selected_inter_ids) == 0 and len(selected_inter_ids) == 0:
            messagebox.showerror("Ungültige Eingabe", "Bitte Bewerter-ID's für die Reliabilitätsuntersuchung auswählen.")
            # Auswahl vom User rückgängig machen
            selected_intra_metrics = []
            selected_inter_metrics = []
            return
        elif len(selected_intra_metrics) == 0 and len(selected_inter_metrics) == 0:
            messagebox.showerror("Ungültige Eingabe", "Bitte Metriken für die Reliabilitätsuntersuchung auswählen.")
            # Auswahl vom User rückgängig machen
            selected_intra_ids = []
            selected_inter_ids = []
            return
        
        container.frames["ResultsFrame"].update_frame()
        container.show_frame("ResultsFrame")

    def populate_rater_container(self):
        """
        Die Funktion befüllt den Frame, in dem die Bewerter ID's dargestellt werden.
        Die Bewerter ID's stammen aus der zuvor importierten Datei.
        """
        headings = ["ID", "Intrarater", "Interrater"]
        content = []
        for id in self.container.rater_ids:
            self.intra_ids[id] = tk.IntVar()
            self.inter_ids[id] = tk.IntVar()
            content.append([str(id), self.intra_ids[id], self.inter_ids[id]])

        self.create_table(self.rater_container.viewPort, headings, content)
        
    def populate_metrics_container(self):
        """
        Die Funktion befüllt den Frame, in dem die Metriken dargestellt werden.
        In Abhängigkeit vom zuvor ausgewählten Skalenformat.
        """
        # Variablen zum Erstellen der Tabelle erzeugen.
        if self.container.scale_format == "nominal":
            self.metrics = ["Cohen's-|Conger's \u03BA", "Fleiss' \u03BA", "Krippendorff's \u03B1", "Gwet's AC"]
        elif self.container.scale_format == "ordinal":
            self.metrics = ["Cohen's-|Conger's \u03BA", "Fleiss' \u03BA", "Krippendorff's \u03B1", "Gwet's AC"]
        elif self.container.scale_format == "intervall":
            self.metrics = ["ICC"]
        elif self.container.scale_format == "rational":
            self.metrics = ["ICC"]
        
        headings = ["Metrik", "Intrarater", "Interrater"]
        content = []
        for metric in self.metrics:
            content.append([metric, self.map_metric_to_var("intra", metric), self.map_metric_to_var("inter", metric)])

        self.create_table(self.metrics_container, headings, content)
        
    def map_metric_to_var(self, mode, metric_name):
        """
        Gibt für einen Metriknamen die entsprechende Variable zurück, die dem Checkbutton zugeornet wird.
        Mode ist ein String mit den Werten "intra", oder "inter".
        """
        if mode == "intra":
            if metric_name == "Cohen's-|Conger's \u03BA":
                return self.intra_kappa
            elif metric_name == "Fleiss' \u03BA":
                return self.intra_fleiss_kappa
            elif metric_name == "Krippendorff's \u03B1":
                return self.intra_alpha_coefficient
            elif metric_name == "Gwet's AC":
                return self.intra_ac
            #elif metric_name == "G-Index":
            #    return self.intra_g_index
            elif metric_name == "ICC":
                return self.intra_icc
        elif mode == "inter":
            if metric_name == "Cohen's-|Conger's \u03BA":
                return self.inter_kappa
            elif metric_name == "Fleiss' \u03BA":
                return self.inter_fleiss_kappa
            elif metric_name == "Krippendorff's \u03B1":
                return self.inter_alpha_coefficient
            elif metric_name == "Gwet's AC":
                return self.inter_ac
            #elif metric_name == "G-Index":
            #    return self.inter_g_index
            elif metric_name == "ICC":
                return self.inter_icc
            

    def toggle(self, mode):
        """
        Buttom comman mit dem alle Elemente ausgewählt, bzw. abgewählt werden können.
        Es gibt die modes "id" und "metric". Beim "id"-mode werden alle Bewerter ID's ausgewählt, bzw. abgewählt.
        Beim Modus "metric" analog die Metriken.
        """
        if mode == "id":
            intra_dic = self.intra_ids
            inter_dic = self.inter_ids
            btn = self.toggle_ids
        if mode == "metric":
            intra_dic = self.intra_metrics
            inter_dic = self.inter_metrics
            btn = self.toggle_metrics

        all_set = True
        for i in intra_dic:
            if mode == "metric":
                # Für den Skalentyp nicht erlaubte Metriken übersprüngen.
                if i not in self.metrics:
                    continue
            # Checken, ob eine intra-rater-id nicht ausgewählt wurde.
            if intra_dic[i].get() == 0:
                all_set = False
                break
        for i in inter_dic:
            if mode == "metric":
                # Für den Skalentyp nicht erlaubte Metriken übersprüngen.
                if i not in self.metrics:
                    continue
            # Checken, ob eine inter-rater-id nicht ausgewählt wurde.
            if inter_dic[i].get() == 0:
                all_set = False
                break
        
        if all_set:
            # Alle ausgwählten Checkbuttons abwählen
            for i in intra_dic:
                intra_dic[i].set(0)
            for i in inter_dic:
                inter_dic[i].set(0)
            # Button-Beschriftung ändern
            btn.config(text="Alle auswählen")
        else:
            # Alle Checkbuttons auswählen
            for i in intra_dic:
                if mode == "metric":
                    # Für den Skalentyp nicht erlaubte Metriken übersprüngen.
                    if i not in self.metrics:
                        continue
                intra_dic[i].set(1)
            for i in inter_dic:
                if mode == "metric":
                    # Für den Skalentyp nicht erlaubte Metriken übersprüngen.
                    if i not in self.metrics:
                        continue
                inter_dic[i].set(1)
            # Button-Beschriftung ändern
            btn.config(text="Alle abwählen")

    def help_cmd(self,event=None):
        """
        Die Funktion öffnet das Helpframe.
        """
        PrepAnalyseHelpFrame(self.container)

    def update_frame(self):
        """
        Die Funktion füllt den Frame mit dynamisch erzeugten Daten.
        """
        self.populate_rater_container()
        self.populate_metrics_container()

class ResultsFrame(ContainerFrame):
    """
    In diesem Frame werden die Ergebnisse der Intra- und der Inter-Rater-Analysen dargestellt.
    """
    def __init__(self, container):
        self.debug = True
        self.reliability_analyses = None
        super().__init__(container)
        # Styling
        container.style.configure("ResultsFrame.TButton", font="Arial 15", foreground="black")
        container.style.configure("TNotebook.Tab", font="Arial 15")

        # GUI-Elemente
        center_container = ttk.Frame(self)
        self.notebook = ttk.Notebook(center_container)

        results_label = ttk.Label(center_container, font="Arial 20", text="Ergebnisse")

        self.intrarater_frame = ttk.Frame(self.notebook)
        self.intrarater_results = ScrollFrame(self.intrarater_frame)
        self.intrarater_infos = ScrollFrame(self.intrarater_frame)



        self.interrater_frame = ttk.Frame(self.notebook)
        self.interrater_results = ttk.Frame(self.interrater_frame)
        self.interrater_infos = ScrollFrame(self.interrater_frame)

        export_btn = ttk.Button(center_container, text="Exportieren", style="ResultsFrame.TButton", 
                                command=self.export_cmd) #TODO command

        # Platzierungen
        self.menu_bar.grid(row=0, column=0, sticky="nsew")
        center_container.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)

        results_label.grid(row=0, column=0, columnspan=3 ,padx=5, pady=5)
        self.notebook.grid(row=1, column=0, sticky="nsew",padx=5, pady=5)

        export_btn.grid(row=2, column=0)

        self.intrarater_results.pack(side="left", fill="both", expand=True, padx=(15, 0), pady=25)
        self.intrarater_infos.pack(side="right", fill="both", padx=(0, 15), pady=25)
        #self.intrarater_results.grid(row=0, column=0, sticky="nsew")
        #self.intrarater_infos.grid(row=0, column=1, sticky="ns")

        self.interrater_results.pack(side="left", fill="both", expand=True, padx=(15, 0), pady=25)
        self.interrater_infos.pack(side="right", fill="both", padx=(0, 15), pady=25)



        # Responsive Design
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        center_container.rowconfigure(1, weight=1)
        center_container.columnconfigure(0, weight=1)

        self.intrarater_frame.rowconfigure(0, weight=1)
        self.intrarater_frame.columnconfigure(0, weight=1)

        #TODO entfernen, nur für Entwicklung
        #self.notebook.add(self.intrarater_frame, text="Intra-Rater")

    def calculate_results(self):
        """
        Die Funktion berechnet die Ergebnisse der Reliabilitätsuntersuchungen.
        """
        self.reliability_analyses = CreateAnalyses(selected_intra_ids, selected_inter_ids, 
                                                   selected_intra_metrics, selected_inter_metrics,
                                                   self.container.scale_format, self.container.categories,
                                                   self.container.weights, self.container.filevalidation.labels)

    def populate_intra_results(self):
        """
        Die Funktion füllt den Frame, in dem die Ergebnisse der Intrarater-Reliabilitätsuntersuchung 
        dargestellt werden.
        """
        if selected_intra_ids and selected_intra_metrics:
            self.notebook.add(self.intrarater_frame, text="Intra-Rater")    # Legt einen neuen Tab im Notebook an

            # In den Listen werden Header, bzw. Zellen-Elemente für die Tabelle gespeichert.
            headings = ["ID"]
            for metric in selected_intra_metrics:
                headings.append(metric)
            if self.container.scale_format == "nominal" or self.container.scale_format == "ordinal":
                headings.append("#Subjects")
                headings.append("#Replicates")

            content = []

            # In den Listen werden Rater ID's gespeichert, von denen keine Intra-Rater-Analyse erstellt werden kann.
            not_enough_ratings = []

            if self.container.scale_format == "nominal" or self.container.scale_format == "ordinal":
                # In self.reliability_analyses wird ein CAC-Objekt gespeichert, falls das
                # Skalenformat nominal oder ordinal ist.
                for rater_id in self.reliability_analyses.results["intra"]:
                    quant_subjects = self.reliability_analyses.results["intra"][rater_id].n
                    quant_replicates = self.reliability_analyses.results["intra"][rater_id].r

                    if quant_replicates < 2 or quant_subjects < 1:
                        # Falls keine Subjects bewertet worden sind, oder keine Subjects mehrfach bewertet worden sind
                        # kann keine Intra-Rater-Analyse vorgenommen werden.
                        not_enough_ratings.append(str(rater_id))
                        continue
                    
                    if self.debug:
                        print("populate_intra_results")
                        print("Rater id: " + str(rater_id))
                        print("quant_subjects " + str(quant_subjects))
                        print("quant_replicates " + str(quant_replicates))
                        print()
                    #TODO checken, ob keine subjects oder nur 1 Rater. => Dann wurde keine Intra-Analyse vorgneommen
                    # Dementsprechend in der Info-Box anzeigen lassen.
                    row = []
                    cont = False
                    for metric in selected_intra_metrics:
                        metric_function_name = map_metrics(metric)

                        metric_value = -99          # Dummy-Wert der im Fehlerfall ausgegeben wird
                        try:
                            metric_value = getattr(self.reliability_analyses.results["intra"][rater_id], metric_function_name)()["est"]["coefficient_value"]
                        except ZeroDivisionError:
                            # Tritt auf, wenn alle Subjects identisch bewertet worden sind.
                            metric_value = 1.0
                        except Exception as e:
                            print("Exception in populate_intra_results:" + str(e))
                        
                        if isnan(metric_value) and metric == "Cohen's-|Conger's \u03BA":
                            # Bei Conger's-Kappa gibt es einen Bug, wenn alle Subjects identisch bewertet worden sind.
                            # Es wird hier kein ZeroDivisionError geworfen sondern, der Wert ist nan.
                            metric_value = 1.0
                            
                        row.append(str(metric_value))                                    # Mittleren Elemente der Reihe, also Metrikwerte, hinzufügen.
                    
                    if cont:
                        continue
                    row.insert(0, str(rater_id))                                             # Erste Element der Reihe, also Rater-ID, hinzufügen
                    row.append(str(quant_subjects))  # Vorletztes Element der Reihe, also #Subjects, hinzufügen.
                    row.append(str(quant_replicates))  # Letzte Element der Reihe, also #Duplikate, hinzufügen.
                    content.append(row)

            else:
                # Andernfalls wird in self.reliability_analyses ein pingouin-Objekt gespeichert.
                for rater_id in self.reliability_analyses.results["intra"]:
                    #TODO quantity subjects und replicates herausfinden

                    #TODO checken, ob keine subjects oder nur 1 Rater. => Dann wurde keine Intra-Analyse vorgneommen
                    # Dementsprechend in der Info-Box anzeigen lassen.
                    row = [str(rater_id)]      # Erste Element der Reihe, also Rater-ID, hinzufügen
                    metric_function_name = map_metrics(metric)

                    metric_value = -99          # Dummy-Wert der im Fehlerfall ausgegeben wird
                    try:
                        metric_value = self.reliability_analyses.results["intra"][rater_id].iloc[2]["ICC"]
                    except Exception as e:
                        print("Exception in populate_intra_results:" + str(e))

                    row.append(str(metric_value)) # Mittleren Elemente der Reihe, also Metrikwerte, hinzufügen.
                    content.append(row)

            if self.debug:
                print("populate_intra_results")

                print("Headings")
                print(headings)
                print()

                print("Content")
                print(content)
                print()

            self.create_table(self.intrarater_results.viewPort, headings, content)

            # Info-Frame ggf. befüllen TODO Bedingungen
            # GUI-Elemente
            intrarater_infolabel = ttk.Label(self.intrarater_infos.viewPort, font="Arial 20", text="Infos:")

            intrarater_info_list = ttk.Frame(self.intrarater_infos.viewPort)

            txt = "Skalenformat: " + self.container.scale_format
            scale_format_lbl = ttk.Label(intrarater_info_list, font="Arial 18", text=txt)
            scale_format_lbl.pack(padx=5, pady=5, fill="x")

            if self.container.scale_format == "nominal" or self.container.scale_format == "ordinal": 
                txt = "Gewichte: " + self.container.weights
                weights_lbl = ttk.Label(intrarater_info_list, font="Arial 18", text=txt)
                weights_lbl.pack(padx=5, pady=(5, 15), fill="x")

                if not_enough_ratings:
                    txt = "Keine Subjects mehrfach\nbewertet:"
                    not_enough_ratings_lbl = ttk.Label(intrarater_info_list, font="Arial 18", text=txt)
                    not_enough_ratings_lbl.pack(padx=5, pady=5, fill="x")

                    for rater_id in not_enough_ratings:
                        txt = "• " + str(rater_id) #TODO Zeilenumbruch, falls zu lang
                        no_replicates = ttk.Label(intrarater_info_list, font="Arial 18", text=txt)
                        no_replicates.pack(padx=5, pady=5, fill="x")


            # Platzierungen
            intrarater_infolabel.pack(pady=15)
            intrarater_info_list.pack(fill="y")

    def populate_inter_results(self):
        """
        Die Funktion füllt den Frame, in dem die Ergebnisse der Interrater-Reliabilitätsuntersuchung 
        dargestellt werden.
        """
        if selected_inter_ids and selected_inter_metrics:
            self.notebook.add(self.interrater_frame, text="Inter-Rater")    # Legt einen neuen Tab im Notebook an

            # In den Listen werden Header, bzw. Zellen-Elemente für die Tabelle gespeichert.
            headings = []
            for metric in selected_inter_metrics:
                headings.append(metric)
            if self.container.scale_format == "nominal" or self.container.scale_format == "ordinal":
                headings.append("#Subjects")
                headings.append("#Rater")

            content = []

            row = []
            if self.container.scale_format == "nominal" or self.container.scale_format == "ordinal":
                for metric in selected_inter_metrics:
                    metric_function_name = map_metrics(metric)

                    metric_value = -99          # Dummy-Wert der im Fehlerfall ausgegeben wird
                    try:
                        metric_value = getattr(self.reliability_analyses.results["inter"], metric_function_name)()["est"]["coefficient_value"]
                    except Exception as e:
                        print("Exception in populate_intra_results:" + str(e))
                    row.append(str(metric_value))
            else:
                # Intervall oder Rationalskala
                metric_value = -99          # Dummy-Wert der im Fehlerfall ausgegeben wird
                try:
                    metric_value = self.reliability_analyses.results["inter"].iloc[2]["ICC"]
                except Exception as e:
                    print("Exception in populate_intra_results:" + str(e))

                row.append(str(metric_value)) # Mittleren Elemente der Reihe, also Metrikwerte, hinzufügen.
                content.append(row)

            if self.container.scale_format == "nominal" or self.container.scale_format == "ordinal":
                quant_subjects = self.reliability_analyses.results["inter"].n
                row.append(str(quant_subjects))
                quant_raters = self.reliability_analyses.results["inter"].r
                row.append(str(quant_raters))
                content.append(row)
            
            self.create_table(self.interrater_results, headings, content)

            # Info-Frame ggf. befüllen TODO Bedingungen
            # GUI-Elemente
            interrater_infolabel = ttk.Label(self.interrater_infos, font="Arial 18", text="Infos:")

            interrater_info_list = ttk.Frame(self.interrater_infos)
            txt = "Skalenformat: " + self.container.scale_format
            scale_format_lbl = ttk.Label(interrater_info_list, font="Arial 18", text=txt)
            scale_format_lbl.pack(padx=5, pady=5, fill="x")

            if self.container.scale_format == "nominal" or self.container.scale_format == "ordinal":
                txt = "Gewichte: " + self.container.weights
                weights_lbl = ttk.Label(interrater_info_list, font="Arial 18", text=txt)
                weights_lbl.pack(padx=5, pady=(5, 15), fill="x")


            # Platzierungen
            interrater_infolabel.pack(pady=15)
            interrater_info_list.pack(pady=15)

    def export_cmd(self):
        """
        Die Funktion ermöglicht aus die Reliabilitätsuntersuchungen als Excel-, Libreoffice-, oder CSV-Datei zu 
        exportieren.
        """
        filename = tk.filedialog.asksaveasfilename(filetypes=[
            ("Excel files", ".xlsx .xls"), 
            ("Libreoffice Calc files", ".ods"),
            ("Csv files", ".csv")
            ])
        write_excel(self.reliability_analyses, selected_intra_ids, selected_intra_metrics, selected_inter_ids, 
                    selected_inter_metrics, self.container.scale_format, filename) # TODO path abfragen

    def help_cmd(self,event=None):
        """
        Die Funktion öffnet das Helpframe.
        """
        # Jedes Frame erzeugt ein HelpFrame mit eigenen Inhalten.
        # Wird in den vererbten Klassen implementiert.
        ResultsHelpFrame(self.container)

    def update_frame(self):
        """
        Die Funktion füllt den Frame mit dynamisch erzeugten Daten.
        """
        self.calculate_results()
        self.populate_intra_results()
        self.populate_inter_results()
