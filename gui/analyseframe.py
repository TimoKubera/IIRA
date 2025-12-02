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

def _validate_selection(ids, metrics, min_ids=2, min_metrics=1):
    """Validates the selection of ids and metrics.
    
    Args:
        ids: List of ids
        metrics: List of metrics
        min_ids: Minimum number of ids required
        min_metrics: Minimum number of metrics required
    
    Returns:
        Tuple of boolean and integer. Boolean indicates if the selection is valid. Integer indicates the error code.
    """
    if len(ids) < min_ids:
        return False, 1
    if len(metrics) < min_metrics:
        return False, 2
    
    valid_count = 0
    for id in ids:
        if isinstance(id, str) and len(id) > 0:
            valid_count += 1
    
    if valid_count < min_ids:
        return False, 3
    
    return True, 0

class AnalyseFrame(ContainerFrame):
    def __init__(self, container):
        """Initializes the AnalyseFrame.
        
        Args:
            container: The parent container
        """
        self.metrics: list = []
        self.intra_kappa = tk.IntVar()
        self.intra_fleiss_kappa = tk.IntVar()
        self.intra_alpha_coefficient = tk.IntVar()
        self.intra_ac = tk.IntVar()
        self.intra_icc = tk.IntVar()
        self.intra_metrics: dict = {
            "Cohen's-|Conger's ba": self.intra_kappa,
            "Fleiss' ba": self.intra