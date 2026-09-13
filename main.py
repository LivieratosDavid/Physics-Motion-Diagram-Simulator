import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk, messagebox
from motions import *
import pandas as pd
from saving import CSVManager 
from rendering import Rendering 
import os
import subprocess


data = {}
csv = CSVManager(data)
# ---------------- MAIN WINDOW ----------------

window = tk.Tk()
window.title("Motion Simulator")
window.geometry("500x700")
window.resizable(False, False)

# ---------------- VARIABLES ----------------

motion_var = tk.StringVar(value="Linear Motion")
diagram_var = tk.StringVar(value="x-t")
orbit_var = tk.StringVar(value="None")

# -------- FUNCTIONS --------------

def reset():
    time_entry.delete(0, tk.END)
    acceleration_entry.delete(0, tk.END)
    velocity_entry.delete(0, tk.END)
    mass_entry.delete(0, tk.END)
    height_entry.delete(0, tk.END)
    angle_entry.delete(0, tk.END)
    displacement_entry.delete(0, tk.END)
    k_entry.delete(0, tk.END)

def hide_all():
    widgets = [
        angle_label, angle_entry,
        height_label, height_entry,
        acceleration_label, acceleration_entry,
        k_label, k_entry,
        displacement_label, displacement_entry
    ]

    for w in widgets:
        w.place_forget()

def update_diagrams(*args):
    hide_all()
    motion = motion_var.get()

    if motion == "Linear Motion":
        diagram_menu["values"] = ["x-t", "v-t"]
        mass_label.place_forget()
        mass_entry.place_forget()
    else:
        mass_label.place(x=250, y=265, anchor="center")
        mass_entry.place(x=250, y=290, anchor="center")

        if motion == "Accelerated Motion":
            diagram_menu["values"] = ["x-t", "v-t", "Kinetic Energy"]

            acceleration_label.place(x=250, y=320, anchor="center")
            acceleration_entry.place(x=250, y=345, anchor="center")

        elif motion == "Projectile Motion":
            diagram_menu["values"] = ["x-t", "y-t", "x-y", "Kinetic Energy", "Potential Energy"]

            angle_label.place(x=250, y=320, anchor="center")
            angle_entry.place(x=250, y=345, anchor="center")

            height_label.place(x=250, y=375, anchor="center")
            height_entry.place(x=250, y=400, anchor="center")

        elif motion == "Simple Harmonic Motion":
            diagram_menu["values"] = ["x-t"]

            k_label.place(x=250, y=320, anchor="center")
            k_entry.place(x=250, y=345, anchor="center")

            displacement_label.place(x=250, y=375, anchor="center")
            displacement_entry.place(x=250, y=400, anchor="center")

    diagram_var.set(diagram_menu["values"][0])

def update_orbits(*args):

    orbit = orbit_var.get()

    if orbit == "Earth":
        hide_all()

        diagram_label.place_forget()
        diagram_menu.place_forget()

    else:
        diagram_label.place(x=250, y=440, anchor="center")
        diagram_menu.place(x=250, y=465, anchor="center")

        update_diagrams()

# ---------------- MAIN SIMULATION ----------------
def simulate():

    orbit = orbit_var.get()
    data.clear()

    if orbit == "Earth":
        run_orbit()
        return

    try:

        motion = motion_var.get()
        t_max = float(time_entry.get())
        v0 = float(velocity_entry.get())
        diagram = diagram_var.get()
        rendering = Rendering(None)

        if t_max <= 0: 
            messagebox.showerror("Syntax Error","Time must be greater than 0")
            return 
        else:
        # ---------------- LINEAR MOTION ----------------
            t = np.linspace(0, t_max, 100)
            if motion == "Linear Motion":
                motion = LinearMotion(v0, t_max)

                data.update ({
                    "Time (s)": t,
                    "Position (m)": motion.position(), 
                    "Velocity (m/s)": motion.velocity(),
                })
            
                diagrams = {
                    "x-t": (motion.position(), "Linear Motion: x-t", "Distance (m)"),
                    "v-t": (motion.velocity(), "Linear Motion: v-t", "Velocity (m/s)"),
                }
            
                y_data, title, ylabel = diagrams[diagram]
                rendering.render_diagrams(
                    t, y_data, title, "Time (s)", ylabel,
                    extra_text=[(0.13, 0.04, "U = 0 J", "red"), (0.13, 0.08, "ΔK = 0 J", "darkred")]
                )

            # ---------------- ACCELERATED MOTION ----------------

            elif motion == "Accelerated Motion":
                a = float(acceleration_entry.get())
                m = float(mass_entry.get())
                motion = AcceleratedMotion(v0, t_max, a, m)

                if m <= 0: 
                    messagebox.showerror("Syntax Error", "Mass must be greater than 0")
                    return

                data.update ({
                    "Time (s)": t,
                    "Position (m)": motion.position(),
                    "Velocity (m/s)": motion.velocity(),
                    "Kinetic Energy (J)": motion.kinetic()
                })

                diagrams = {
                    "x-t": (motion.position(), "Accelerated Motion: x-t", "Distance (m)", False),
                    "v-t": (motion.velocity(), "Accelerated Motion: v-t", "Velocity (m/s)", False),
                    "Kinetic Energy": (motion.kinetic(), "Accelerated Motion: Kinetic Energy", "Kinetic Energy (J)", True),
                }

                y_data, title, ylabel, energy = diagrams[diagram]

                rendering.render_diagrams(
                    t, y_data, title, "Time (s)", ylabel, "acc.png",
                    energy_button=energy,
                    extra_text=[
                        (0.15, "U = 0 J", "red"),
                        (0.13, f"ΔK = {motion.dk():.2f} J", "darkred")
                    ]
                )
            

            # ---------------- PROJECTILE MOTION ----------------

            elif motion == "Projectile Motion":
                theta = float(angle_entry.get())
                h0 = float(height_entry.get())
                m = float(mass_entry.get())
                

                if m <= 0: 
                    messagebox.showerror("Syntax Error", "Mass must be greater than 0")
                    return

                if theta < 0 or theta >= 90:
                    messagebox.showerror("Syntax Error", "Angle must be 0-89 degrees")
                    return

                motion = ProjectileMotion(v0, t_max, h0, theta, m)

                data.update ({
                    "Time (s)": t,
                    "Horizontal Position (m)": motion.position(),
                    "Vertical Position (m)": motion.height(),
                    "Velocity (m/s)": motion.v_full(),
                    "Kinetic Energy (J)": motion.kinetic(),
                    "Potential Energy (J)": motion.potential()
                })

                extra_text = [
                    (0.15, f"ΔU = {motion.dU():.2f} J", "red"),
                    (0.13, f"ΔK = {motion.dk():.2f} J", "darkred")
                ]

                diagrams = {
                    "x-t": (
                        t, motion.position(),
                        "Projectile Motion: x-t",
                        "Time (s)",
                        "Horizontal Distance (m)",
                        False
                    ),

                    "y-t": (
                        t, motion.height(),
                        "Projectile Motion: y-t",
                        "Time (s)",
                        "Vertical Distance (m)",
                        False
                    ),

                    "Kinetic Energy": (
                        t, motion.kinetic(),
                        "Projectile Motion: Kinetic Energy",
                        "Time (s)",
                        "Kinetic Energy (J)",
                        True
                    ),

                    "Potential Energy": (
                        t, motion.potential(),
                        "Projectile Motion: Potential Energy",
                        "Time (s)",
                        "Potential Energy (J)",
                        True
                    ),

                    "x-y": (
                        motion.position(),
                        motion.height(),
                        "Projectile Trajectory (x-y)",
                        "Horizontal Distance (m)",
                        "Vertical Distance (m)",
                        False
                    ),
                }

                x_data, y_data, title, xlabel, ylabel, energy = diagrams[diagram]

                rendering.render_diagrams(
                    x_data, y_data, title, xlabel, ylabel,
                    "proj.png",
                    energy_button=energy,
                    extra_text=extra_text
                )
            
                

            # ---------------- SIMPLE HARMONIC MOTION ----------------

            elif motion == "Simple Harmonic Motion":
                k = float(k_entry.get())
                A = float(displacement_entry.get())
                m = float(mass_entry.get())

                if m <= 0: 
                    messagebox.showerror("Syntax Error", "Mass must be greater than 0")
                    return

                if k <= 0:
                    messagebox.showerror("Syntax Error", "Spring Constant must be greater than 0")
                    return

                motion = SimpleHarmonicMotion(v0, t_max, A, k, m)

                data.update ({
                    "Time (s)": t,
                    "Horizontal Position (m)": motion.position(),
                    "Kinetic Energy (J)": motion.kinetic(),
                    "Potential Energy (J)": motion.potential()
                })

                rendering.render_diagrams(
                        t,
                        motion.position(),
                        "Simple Harmonic Motion: x-t",
                        "Time (s)",
                        "Displacement (m)",
                        "shm.png"
                    )
                
            

    except ValueError:
        messagebox.showerror("Error","Please enter valid numbers.")

# ---------------- ORBIT ----------------

def run_orbit():
    subprocess.Popen(["python3","orbits.py"])


# ---------------- WIDGETS ----------------

# Title

title_label = tk.Label(
    window,
    text="Physics Motion Simulator",
    font=("Arial",18,"bold")
)

title_label.place(x=250,y=25,anchor="center")


# Motion type

motion_label = tk.Label(
    window,
    text="Select Motion Type:"
)

motion_label.place(x=140,y=70,anchor="center")


motion_menu = ttk.Combobox(
    window,
    textvariable=motion_var,
    values=[
        "Linear Motion",
        "Accelerated Motion",
        "Projectile Motion",
        "Simple Harmonic Motion"
    ],
    state="readonly",
    width=18
)

motion_menu.place(x=140,y=95,anchor="center")


# Orbit animations

orbit_label = tk.Label(
    window,
    text="Select Orbit Animation:"
)

orbit_label.place(x=350,y=70,anchor="center")


orbit_menu = ttk.Combobox(
    window,
    textvariable=orbit_var,
    values=["None","Earth"],
    state="readonly",
    width=18
)

orbit_menu.place(x=350,y=95,anchor="center")


# Maximum time

time_label = tk.Label(
    window,
    text="Maximum Time (s):"
)

time_label.place(x=250,y=140,anchor="center")
time_entry = tk.Entry(window)
time_entry.place(x=250,y=165,anchor="center")


# Initial velocity

velocity_label = tk.Label(
    window,
    text="Initial Velocity (m/s):"
)

velocity_label.place(x=250,y=205,anchor="center")
velocity_entry = tk.Entry(window)
velocity_entry.place(x=250,y=230,anchor="center")


# Mass
mass_label = tk.Label(
    window,
    text="Mass (kg):"
)

mass_label.place(x=250,y=265,anchor="center")
mass_entry = tk.Entry(window)
mass_entry.place(x=250,y=290,anchor="center")


# Acceleration

acceleration_label = tk.Label(
    window,
    text="Acceleration (m/s²):"
)

acceleration_entry = tk.Entry(window)


# Angle

angle_label = tk.Label(
    window,
    text="Launch Angle (degrees: 0-89°):"
)

angle_entry = tk.Entry(window)


# Height

height_label = tk.Label(
    window,
    text="Initial Height (m):"
)

height_entry = tk.Entry(window)


# Spring constant

k_label = tk.Label(
    window,
    text="Spring Constant (N/m):"
)

k_entry = tk.Entry(window)


# Amplitude

displacement_label = tk.Label(
    window,
    text="Amplitude (m):"
)

displacement_entry = tk.Entry(window)


# Diagram selection

diagram_label = tk.Label(
    window,
    text="Select Graph:"
)

diagram_label.place(x=250,y=440,anchor="center")


diagram_menu = ttk.Combobox(
    window,
    textvariable=diagram_var,
    values=["x-t","v-t"],
    state="readonly"
)

diagram_menu.place(x=250,y=465,anchor="center")


# ---------------- BUTTON FRAME ----------------

button_frame = tk.Frame(window)
button_frame.place(
    x=250,
    y=650,
    anchor="center"
)

# First row
top_buttons = tk.Frame(button_frame)
top_buttons.pack()

simulate_button = tk.Button(
    top_buttons,
    text="Run Simulation",
    font=("Arial", 13, "bold"),
    bg="lightblue",
    width=12,
    command=simulate
)

reset_button = tk.Button(
    top_buttons,
    text="Reset",
    font=("Arial", 13, "bold"),
    bg="lightblue",
    width=12,
    command=reset

)
simulate_button.pack(side="left", padx=5, pady=5)
reset_button.pack(side="left", padx=5, pady=5)

# Second row
bottom_buttons = tk.Frame(button_frame)
bottom_buttons.pack()
export_button = tk.Button(
    bottom_buttons,
    text="Export CSV",
    font=("Arial", 13, "bold"),
    bg="lightblue",
    width=12,
    command=csv.export_csv

)

compare_button = tk.Button(
    bottom_buttons,
    text="Compare CSV",
    font=("Arial", 13, "bold"),
    bg="lightblue",
    width=12,
    command=csv.compare_csv

)

export_button.pack(side="left", padx=5, pady=5)
compare_button.pack(side="left", padx=5, pady=5)


# ---------------- START ----------------

motion_var.trace_add("write",update_diagrams)
orbit_var.trace_add("write",update_orbits)

update_diagrams()
window.mainloop()