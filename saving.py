import tkinter as tk 
from tkinter import filedialog, ttk, messagebox
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

class CSVManager:
    def __init__(self, data):
        self.data = data

    def export_csv(self):
        if not self.data:
            messagebox.showerror("Export Error", "Run a simulation before exporting.")
            return

        filename = filedialog.asksaveasfilename(
            title="Export Simulation",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )

        if not filename:
            return

        headers = list(self.data.keys())
        arrays = list(self.data.values())

        csv_data = np.column_stack(arrays)

        np.savetxt(
            filename,
            csv_data,
            delimiter=",",
            header=",".join(headers),
            comments="",
            fmt="%.1f"
        )

        messagebox.showinfo("Export Complete", "Simulation data exported successfully.")

    def compare_csv(self):
        file1 = filedialog.askopenfilename(
            title="Select First CSV",
            filetypes=[("CSV files", "*.csv")]
        )

        if not file1:
            return

        file2 = filedialog.askopenfilename(
            title="Select Second CSV",
            filetypes=[("CSV files", "*.csv")]
        )

        if not file2:
            return

        data1 = pd.read_csv(file1)
        data2 = pd.read_csv(file2)

        diagrams = {
            "x-t": ("Time (s)", "Position (m)"),
            "v-t": ("Time (s)", "Velocity (m/s)"),
            "K-t": ("Time (s)", "Kinetic Energy (J)"),
            "U-t": ("Time (s)", "Potential Energy (J)"),
            "x-y": ("Horizontal Position (m)", "Vertical Position (m)")
        }

        common_diagrams = []

        for diagram, (x_column, y_column) in diagrams.items():

            if (
                x_column in data1.columns and
                y_column in data1.columns and
                x_column in data2.columns and
                y_column in data2.columns
            ):
                common_diagrams.append(diagram)

        if not common_diagrams:
            messagebox.showerror(
                "Comparison Error",
                "The two CSV files have no diagrams in common."
            )
            return

        compare_window = tk.Toplevel()
        compare_window.title("Compare Simulations")
        compare_window.geometry("300x200")
    
        tk.Label(
            compare_window,
            text="Select diagram to compare:",
            font=("Arial", 12, "bold")
        ).pack(pady=15)
    
        diagram_var = tk.StringVar()
    
        diagram_menu = ttk.Combobox(
            compare_window,
            textvariable=diagram_var,
            values=common_diagrams,
            state="readonly"
        )
    
        diagram_menu.pack(pady=5)
    
        diagram_menu.current(0)

        def plot_comparison():
            diagram = diagram_var.get()
            x_column, y_column = diagrams[diagram]
            plt.figure(figsize=(8, 5))
    
            plt.plot(
                data1[x_column],
                data1[y_column],
                linewidth=3,
                label="Simulation 1"
            )
    
            plt.plot(
                data2[x_column],
                data2[y_column],
                linewidth=3,
                label="Simulation 2"
            )
    
            plt.title(f"Comparison: {diagram}")
            plt.xlabel(x_column)
            plt.ylabel(y_column)
    
            plt.grid(True)
            plt.legend()
    
            plt.show()


        tk.Button(
                compare_window,
                text="Compare",
                font=("Arial", 12, "bold"),
                command=plot_comparison
            ).pack(pady=10)