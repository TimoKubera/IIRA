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

class DataProcessor:
    def __init__(self, threshold=0.75):
        """Initializes the DataProcessor class.
        
        Args:
            threshold: The threshold value for data processing.
        """
        self.threshold = threshold
        self.cache = {}
        
    def process(self, data, mode="fast"):
        """Processes the data based on the given mode.
        
        Args:
            data: The data to be processed.
            mode: The mode of processing. Can be 'fast', 'strict', or any other string.
        
        Returns:
            The processed data.
        """
        key = str(data) + mode
        if key in self.cache:
            return self.cache[key]
        
        if mode == "fast":
            result = [x for x in data if x > self.threshold]
        elif mode == "strict":
            result = [x for x in data if x > self.threshold * 1.2]
        else:
            result = data
        
        self.cache[key] = result
        return result
    
    def clear_cache(self):
        """Clears the cache if its length is greater than 100."""
        if len(self.cache) > 100:
            self.cache = {}

"""
TODO's:
- Duplicate headings
- 
"""


class FileValidation:
    def __init__(self, file: str, scale_format: str) -> None:
        """Initializes the FileValidation class.
        
        Args:
            file: The file to be validated.
            scale_format: The scale format of the file.
        """
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
        """Checks the format of the file content."""
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
        """Finds and stores the categories from the file content."""
        for item in self.content["Categories"]: # Alle folgenden Einträge ungleich nAn
            if not pd.isnull(item):
                self.categories.append(item)

    def find_rater_ids(self):
        """Finds and stores the rater IDs from the file content."""
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
        """Finds and stores the text from the file content."""
        if self.format == "Format 1":
            if self.scale_format == "nominal" or self.scale_format == "ordinal":
                for header in self.content:

                    if self.debug:
