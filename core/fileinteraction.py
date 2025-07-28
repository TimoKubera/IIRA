"""
In dem Modul wird eine Klasse definiert, die es ermöglicht eine Eingabedatei zu validieren.
TODO ...
"""

import re
import pathlib
import datetime
from math import isnan
""" Standardbibliothek Imports """

import pandas as pd
import numpy as np
import xlsxwriter
from pprint import pprint
""" Third Party Imports """

from core.metrics import map_metrics
""" Lokale Imports """

PROFILE = 0
RATING = 1
""" Globale Variablen und Konstanten """

"""
TODO's:
- Duplicate headings
- 
"""


class FileValidation:
    def __init__(self, file: str, scale_format: str) -> None:
        self.debug: bool = False
        self.content: pd.DataFrame | None = None
        self.format: str | None = None
        self.scale_format: str = scale_format
        self.categories: list = []
        self.rater_ids: list = []
        self.text: list = []
        self.formatted_text: list = []
        self.labels: dict = {}

        file_extension = pathlib.Path(file).suffix
        if file_extension in (".xlsx", ".xls"):
            self.content = pd.read_excel(file)
        elif file_extension == ".ods":
            self.content = pd.read_excel(file, engine="odf")
        else:
            self.content = pd.read_csv(file, delimiter=";")  # TODO: Andere Delimiter akzeptieren

        self.content = self.content.loc[:, ~self.content.columns.str.contains("^Unnamed")]
        self.check_format()
        if self.scale_format in ("nominal", "ordinal"):
            self.find_categories()
        self.find_rater_ids()
        self.find_text()
        self.find_labels()

        if self.debug:
            print("Format:")
            print(self.format)
            print("Scale Format:")
            print(self.scale_format)
            print("Categories:")
            print(self.categories)
            print("Rater ID's:")
            print(self.rater_ids)
            print()

            print("Text:")
            print(self.text)
            print()

            print("Formatted Text")
            print(self.formatted_text)
            print()

            print("Labels")
            print(self.labels)
            print()
        
    def check_format(self):
        headers = list(self.content.columns)

        for header in headers: #TODO ggf. stemming
            header = header.lower()
            if header == "Rater ID".lower():
                self.format = "Format 1"
                return
            
            if header == "Subject".lower():
                self.format = "Format 2"
                return
        
        raise ValueError
        

    def find_categories(self):
        for item in self.content["Categories"]: # Alle folgenden Einträge ungleich nAn
            if not pd.isnull(item):
                self.categories.append(item)

    def find_rater_ids(self):
        if self.format == "Format 1":
            for item in self.content["Rater ID"]: # Alle folgenden Einträge ungleich nAn
                if not pd.isnull(item):
                    if item not in self.rater_ids:
                        self.rater_ids.append(item) # Duplikate nicht erlaubt
        elif self.format == "Format 2":
            if self.scale_format == "nominal" or self.scale_format == "ordinal":
                for header in self.content:
                    # Über alle Spalten iterieren
                    if all(self.content[header].isin(self.categories) | self.content[header].isnull()):
                        # In der Spalte sind alle Einträge mit Kategorie-Labeln versehen worden, oder der Eintrag ist nAn.
                        # => Der Header ist eine Rater_id
                        if header not in self.rater_ids:
                            self.rater_ids.append(header)
            else: 
                # Für Intervall- und Rationaldaten sind alle Header außer "Subject" Rater ID's
                for header in self.content:
                    if header == "Subject":
                        continue
                    if header not in self.rater_ids:
                        self.rater_ids.append(header)

        
    def find_text(self):
        if self.format == "Format 1":
            if self.scale_format == "nominal" or self.scale_format == "ordinal":
                for header in self.content:

                    if self.debug:
                        print("header: " + str(header))

                    # Über alle Spalten iterieren
                    if all(self.content[header].isin(self.categories) | self.content[header].isnull()):
                        # In der Spalte sind alle Einträge mit Kategorie-Labeln versehen worden, oder der Eintrag ist nAn.
                        # => Der Header ist ein Text
                        if header not in self.rater_ids:
                            if "Categories" == header:                   # Skippe die Categories-Spalte
                                continue
                            self.formatted_text.append(self.nlp(header)) # Duplikate erlaubt
                            self.text.append(header)
            else:
                # Für Intervall- und Rationaldaten sind alle Spalten außer der Subject-Spalte relevant
                for header in self.content:
                    if header == "Rater ID":                            # Skippe die Rater ID Spalte
                        continue
                    self.formatted_text.append(self.nlp(header)) # Duplikate erlaubt
                    self.text.append(header)

        elif self.format == "Format 2":
            for item in self.content["Subject"]: # Alle folgenden Einträge ungleich nAn
                if not pd.isnull(item):
                    self.formatted_text.append(self.nlp(item))
                    self.text.append(item)

    def find_labels(self):
        if self.format == "Format 1":
            for row in range(len(self.content)): # Iteriere über die Zeilen
                if pd.isnull(self.content.loc[row, "Rater ID"]):
                    # Zeilen mit leeren Eintrag bei "Rater ID" überspringen
                    continue

                text_label_list = []

                for i, text in enumerate(self.text):
                    # Iteriert über alle Text-Spalten
                    # Fügt der text_label_list Tupel hinzu, die aus dem Text und dem Label bestehen.
                    text_label_list.append((self.formatted_text[i], self.content.loc[row, text]))

                if self.content.loc[row, "Rater ID"] in self.labels:
                    # Falls es Zeilen mit der gleichen Rater ID gibt, füge sie dem label-dictionary hinzu.
                    self.labels[self.content.loc[row, "Rater ID"]] += text_label_list
                else:
                    self.labels[self.content.loc[row, "Rater ID"]] = text_label_list
        elif self.format == "Format 2":
            for rater_id in self.rater_ids:
                text_label_list = []
                for row in range(len(self.content)): # Iteriere über die Zeilen
                    if pd.isnull(self.content.loc[row, "Subject"]):
                        # Zeilen mit leeren Eintrag bei Spalte "Subject" überspringen
                        continue

                    text_label_list.append((self.content.loc[row, "Subject"], self.content.loc[row, rater_id]))

                if rater_id in self.labels:
                    self.labels[rater_id] += text_label_list
                else:
                    self.labels[rater_id] = text_label_list

    def write_file(self, path, ratings):
        """
        Die neu geschrieben Datei hat das folgende Format.
        Categories | Rater ID | Datum_ir_app | Subj_1 | ... | Subj_n
        ------------------------------------------------------------
        alt_1,1    | alt_1,2  |    nAn       | alt_1,4| ... | alt_1,n
            .      |     .    |     .        |     .  |  .  |     .
            .      |     .    |     .        |     .  |  .  |     .
            .      |     .    |     .        |     .  |  .  |     .
        alt_k,1    | alt_k,2  |    nAn       | alt_k,4| ... | alt_k,n
        nAn        | user_1   | datetime x   | new    | ... | new
            .      |     .    |     .        |     .  |  .  |     .
            .      |     .    |     .        |     .  |  .  |     .
            .      |     .    |     .        |     .  |  .  |     .
        nAn        | user_l   | datetime x   | new    | ... | new  
        """
        if self.scale_format == "nominal" or self.scale_format == "ordinal":
            columns = ["Categories", "Rater ID"]
        else:
            columns = ["Rater ID"]
        users = []
        col_rename = {}

        if self.format == "Format 1":
            for txt in self.text:
                columns.append(txt)
                col_rename[txt] = self.nlp(txt) # Dictionary erstellen, um die Pandas Header umzubenennen
        else:
            pass

        for rating in ratings:
            # Alle user die an der Bewertungssession beteiligt waren in der users-Liste speichern.
            if rating == ():
                continue
            if rating[PROFILE] not in users:
                users.append(rating[PROFILE])

        # Den Datenframen mit den alten, relevanten Daten erzeugen
        old_df = pd.DataFrame(self.content, columns=columns)
        old_df = old_df.rename(columns=col_rename)

        if self.debug:
            print("old df")
            print(old_df)
            print()

        # Den Datenframen mit den neuen relevanten Daten, also Ratings pro User, erzeugen.
        #columns += "Datum_ir_app"
        if self.scale_format == "nominal" or self.scale_format == "ordinal":
            columns = ["Categories", "Rater ID"]
        else:
            columns = ["Rater ID"]
        for txt in self.formatted_text:
            columns.append(txt)
        #columns.append("Datum_ir_app")
        new_df = pd.DataFrame([], columns=columns)

        for user in users:
            if self.scale_format == "nominal" or self.scale_format == "ordinal": 
                row = [np.nan, self.usr_to_id(user)]
            else:
                row = [self.usr_to_id(user)]
            for rating in ratings:
                if rating == ():
                    row.append(np.nan)
                elif rating[PROFILE] == user:
                    row.append(rating[RATING])
                else:
                    row.append(np.nan)
            #row.append(current_datetime)
            new_df.loc[len(new_df)] = row # Append the row to the dataframe

        # Dataframe speichern
        df = pd.concat([old_df, new_df], axis="index")
        df = df.reset_index(drop=True)

        # Daten der neuen Bewertungssession hinzufügen.
        current_datetime = datetime.datetime.now()
        current_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S') # Without milliseconds

        date_col = []
        for i in range(len(old_df)):
            date_col.append(np.nan)
        for i in range(len(new_df)):
            date_col.append(current_datetime)
        date_df = pd.DataFrame({"datum_ir_app": date_col})

        df = pd.concat([df, date_df], axis="columns")

        file_extension = pathlib.Path(path).suffix
        if file_extension == ".xlsx" or file_extension == ".xls":
            df.to_excel(path, index = False, header=True)
        elif file_extension == ".ods":
            df.to_excel(path, engine="odf", index = False, header=True)
        else:
            df.to_csv(path, sep=";", index = False, header=True)

    def usr_to_id(self, user):
        return "ir_app_" + user

    def nlp(self, text):
        # Bei Sentisurvey-Header gibt es viele Metadaten. Der eigentliche Text ist in eckige Klammern [] eingeklammert.
        sentisurvey_metadata = "How would you label the following sentences regarding its polarity? Rate the sentences as positive, negative or neutral (neither positive nor negative) based on your perception."
        if sentisurvey_metadata in text:
            text = max(re.findall(re.escape("[")+"(.*?)"+re.escape("]"),text), key=len)

        # Pandas benennt Headers automatisch um, wenn read_csv, bzw. read_excel genutzt wird.
        # Ein Header mit dem Namen "Duplikat" würde "Duplikat.1", bzw. "Duplikat.2" heißen, 
        # wenn er 2-, bzw. 3 mal auftauchn.
        # Das ist nicht erwünscht und wird in diesre Funktion rückgängig gemacht.

        text = re.sub("\.[0-9]*$", "", text)

        # Platz für weiteres NLP bei Bedarf
        return text


class DBInteraction():
    def __init__(self, db_path):
        file_extension = pathlib.Path(db_path).suffix
        self.db_path = db_path
        self.db = None # Beinhaltet das Pandas-Objekt, welches vom File geparsed wird.

        self.active_profile = ""
        self.profiles = []

        if file_extension == ".xlsx" or file_extension == ".xls":
            self.db = pd.read_excel(db_path)
        elif file_extension == ".ods":
            self.db = pd.read_excel(db_path, engine="odf")
        else:
            self.db = pd.read_csv(db_path, delimiter=";") #TODO Andere Delimiter akzeptieren
        
        self.load_profiles()

    def load_profiles(self):
        # Lädt beim Systemstart alle Profile
        if len(self.db["Profile"]) > 0:
            if not pd.isnull(self.db["Profile"][0]):
                self.active_profile = self.db["Profile"][0]
                self.profiles = list(self.db["Profile"][1:])
        else:
            return
    
    def create_profile(self, new_profile):
        if self.active_profile != "":
            self.profiles.append(self.active_profile)
        self.active_profile = new_profile

        self.write_to_db()

    
    def delete_profile(self):
        self.active_profile = self.profiles[0]
        self.profiles.remove(self.active_profile)

        self.write_to_db()

    def change_profile(self, change_to):
        tmp = self.active_profile
        self.active_profile = change_to
        self.profiles.remove(change_to)
        self.profiles.append(tmp)

        self.write_to_db()

    def write_to_db(self):
        # Falls mehr Spalten zur DB hinzukommen muss man ggf. noch darauf achten, dass
        # leere Spalten mit nAn gefüllt werden, um Seiteneffekte zu vermeiden.
        self.db = pd.DataFrame([self.active_profile] + self.profiles, columns=["Profile"])
        self.db.to_csv(self.db_path, sep=";", index = False, header=True)


def write_excel(analyse, intra_ids, intra_metrics, inter_ids, inter_metrics, scale_format, filename):
    """
    Exportiert eine Excel-Datei, die alle Daten der Intra- und Inter-Reliability-Analse enthält.
    """

    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()
    b_cell_format = workbook.add_format()
    b_cell_format.set_bold()

    not_enough_ratings = []
    
    if scale_format == "nominal" or scale_format == "ordinal":
        # In self.reliability_analyses wird ein CAC-Objekt gespeichert, falls das
        # Skalenformat nominal oder ordinal ist.
        if intra_ids and intra_metrics:
            worksheet.write(0, 0, "Intra-Rater-Analyse", b_cell_format)
            worksheet.write(1, 0, "")
            worksheet.write(2, 0, "Gewichte", b_cell_format)
            worksheet.write(3, 0, analyse.results["intra"][intra_ids[0]].weights_name)
            worksheet.write(4, 0, "")
            worksheet.write(5, 0, "")
            worksheet.write(6, 0, "Rater ID", b_cell_format)
            worksheet.write(6, 1, "#Subjects", b_cell_format)
            worksheet.write(6, 2, "#Replicates", b_cell_format)
            j = 3
            for metric in intra_metrics:
                worksheet.write(6, j, metric, b_cell_format)
                j += 1
            i = 7
            for rater_id in intra_ids:
                quant_subjects = analyse.results["intra"][rater_id].n
                quant_replicates = analyse.results["intra"][rater_id].r
                if quant_replicates < 2 or quant_subjects < 1:
                    # Falls keine Subjects bewertet worden sind, oder keine Subjects mehrfach bewertet worden sind
                    # kann keine Intra-Rater-Analyse vorgenommen werden.
                    not_enough_ratings.append(str(rater_id))
                    continue

                worksheet.write(i, 0, rater_id)
                worksheet.write(i, 1, quant_subjects)
                worksheet.write(i, 2, quant_replicates)

                j = 3
                cont = False
                for metric in intra_metrics:
                    metric_function_name = map_metrics(metric)

                    try:
                        metric_dict = getattr(analyse.results["intra"][rater_id], metric_function_name)()["est"]
                        metric_value = metric_dict["coefficient_value"]

                        if isnan(metric_value) and metric == "Cohen's-|Conger's \u03BA":
                            # Bei Conger's-Kappa gibt es einen Bug, wenn alle Subjects identisch bewertet worden sind.
                            # Es wird hier kein ZeroDivisionError geworfen sondern, der Wert ist nan.
                            metric_value = 1.0
                                
                        worksheet.write(i, j, str(metric_value))
                    except ZeroDivisionError:
                        # Tritt auf, wenn ein Subject doppelt und identisch bewertet wurde.
                        worksheet.write(i, j, "1.0")
                    j += 1
                if cont:
                    continue
                i += 1
            worksheet.write(i, 0, "")
            worksheet.write(i + 1, 0, "")
            i += 2
            # Original
            #i = 6
            for rater_id in intra_ids:
                quant_subjects = analyse.results["intra"][rater_id].n
                quant_replicates = analyse.results["intra"][rater_id].r

                if quant_replicates < 2 or quant_subjects < 1:
                    # Falls keine Subjects bewertet worden sind, oder keine Subjects mehrfach bewertet worden sind
                    # kann keine Intra-Rater-Analyse vorgenommen werden.
                    #not_enough_ratings.append(str(rater_id))
                    continue

                worksheet.write(i, 0, "Rater ID", b_cell_format)
                worksheet.write(i+1, 0, rater_id)

                worksheet.write(i, 1, "#Subjects", b_cell_format)
                worksheet.write(i+1, 1, quant_subjects)

                worksheet.write(i, 2, "#Replikate", b_cell_format)
                worksheet.write(i+1, 2, quant_replicates)

                worksheet.write(i+2, 0, "")

                i = i +3
                for metric in intra_metrics:
                    metric_function_name = map_metrics(metric)

                    try:
                        metric_dict = getattr(analyse.results["intra"][rater_id], metric_function_name)()["est"]

                        worksheet.write(i, 0, metric, b_cell_format)
                        worksheet.write(i+1, 0, str(metric_dict["coefficient_value"]))

                        worksheet.write(i, 1, "p-Wert", b_cell_format)
                        worksheet.write(i+1, 1, str(metric_dict["p_value"]))

                        worksheet.write(i, 2, "95% Konfidenzintervall", b_cell_format)
                        worksheet.write(i+1, 2, str(metric_dict["confidence_interval"]))

                        worksheet.write(i+2, 0, "")
                    except ZeroDivisionError:
                        # Tritt auf, wenn ein Subject doppelt und identisch bewertet wurde.
                        worksheet.write(i, 0, metric, b_cell_format)
                        worksheet.write(i+1, 0, "1.0")

                        worksheet.write(i, 1, "p-Wert", b_cell_format)
                        worksheet.write(i+1, 1, "n.a.")

                        worksheet.write(i, 2, "95% Konfidenzintervall", b_cell_format)
                        worksheet.write(i+1, 2, "(n.a., n.a.)")

                        worksheet.write(i+2, 0, "")
                    i = i +3
            worksheet.write(i, 0, "")
            worksheet.write(i+1, 0, "")
            worksheet.write(i+2, 0, "")
            worksheet.write(i+3, 0, "ID's, die kein Subject mehrfach bewertet haben:")
            i = i + 4
            for id in not_enough_ratings:
                worksheet.write(i, 0, id)
                i += 1

        else:
            i = 0

        if inter_ids and inter_metrics:
            # Falls eine inter-rater-analyse vorgenommen wurde, ergänze die Zeilen
            quant_subjects = analyse.results["inter"].n
            quant_raters = analyse.results["inter"].r
            worksheet.write(i, 0, "Inter-Rater-Analyse", b_cell_format)
            worksheet.write(i+1, 0, "")
            worksheet.write(i+2, 0, "Gewichte", b_cell_format)
            worksheet.write(i+3, 0, analyse.results["inter"].weights_name)
            worksheet.write(i+4, 0, "")
            worksheet.write(i+5, 0, "Rater ID's", b_cell_format)
            worksheet.write(i+5, 1, "#Subjects", b_cell_format)
            worksheet.write(i+5, 2, "#Raters", b_cell_format)
            worksheet.write(i+6, 1, str(quant_subjects))
            worksheet.write(i+6, 2, str(quant_raters))
            i = i + 6
            for rater_id in inter_ids:
                worksheet.write(i, 0, rater_id)
                i = i + 1
            worksheet.write(i, 0, "")
            i = i + 1
            for metric in inter_metrics:
                metric_function_name = map_metrics(metric)
                metric_dict = getattr(analyse.results["inter"], metric_function_name)()["est"]

                worksheet.write(i, 0, metric, b_cell_format)
                worksheet.write(i+1, 0, str(metric_dict["coefficient_value"]))

                worksheet.write(i, 1, "p-Wert", b_cell_format)
                worksheet.write(i+1, 1, str(metric_dict["p_value"]))

                worksheet.write(i, 2, "95% Konfidenzintervall", b_cell_format)
                worksheet.write(i+1, 2, str(metric_dict["confidence_interval"]))

                worksheet.write(i+2, 0, "")
                i = i + 3
                

    workbook.close()
