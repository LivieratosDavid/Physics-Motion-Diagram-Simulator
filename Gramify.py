import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import *
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk, messagebox
import pandas as pd
import os
import subprocess

g = 9.81

# ---------------- MAIN WINDOW ----------------

window = tk.Tk()
window.title("Motion Simulator")
window.geometry("500x600")
window.resizable(False, False)

# ---------------- VARIABLES ----------------

motion_var = tk.StringVar(value="Linear Motion")
diagram_var = tk.StringVar(value="x-t")
orbit_var = tk.StringVar(value="None")

# ---------------- DATA HANDLING ----------------

data = {}

# ---------------- FUNCTIONS ----------------

def export_csv():

    if not data:
        messagebox.showerror("Export Error", "Run a simulation before exporting.")
        return

    filename = filedialog.asksaveasfilename(
        title="Export Simulation",
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")]
    )

    if not filename:
        return

    headers = list(data.keys())
    arrays = list(data.values())

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

    elif motion == "Accelerated Motion":
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

# ----- LINEAR MOTION ------
def linear_motion(t, v0, diagram):
    x = v0 * t
    v = np.full_like(t,v0)

    dK = 0
    U = 0

    data1 = {
           "Time (s)": t,
           "Position (m)": x,
           "Velocity (m/s)": v,
       }

    if diagram == "x-t":
        y_data = x
        ylabel = "Distance (m)"
        title = "Linear Motion: x-t"

    else:
        y_data = v
        ylabel = "Velocity (m/s)"
        title = "Linear Motion: v-t"

    plt.figure(figsize=(8, 5))
    plt.plot(t,y_data,color="red",linewidth=3)
    plt.title(title)
    plt.xlabel("Time (s)")
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.figtext(0.15,0.02,f"U = {U} J",fontsize=9,color="red")
    plt.figtext(0.02,0.02,f"ΔK = {dK} J",fontsize=9,color="darkred")
    plt.show()

    return data1

# ---------------- ACCELERATED MOTION ----------------

def accelerated_motion(t, v0, m, a, diagram):

    x = v0 * t + 0.5 * a * t**2
    v = v0 + a * t

    K_init = 0.5 * m * v0**2
    K_final = 0.5 * m * v[-1]**2
    d_K = K_final - K_init

    K = 0.5 * m * v**2
    U = 0

    data2 = {
        "Time (s)": t,
        "Position (m)": x,
        "Velocity (m/s)": v,
        "Kinetic Energy (J)": K
    }

    if diagram == "x-t":
        y_data = x
        ylabel = "Distance (m)"
        title = "Accelerated Motion: x-t"

    elif diagram == "v-t":
        y_data = v
        ylabel = "Velocity (m/s)"
        title = "Accelerated Motion: v-t"

    else:
        y_data = K
        ylabel = "Kinetic Energy (J)"
        title = "Accelerated Motion: K-t"

    plt.figure(figsize=(8, 5))
    plt.plot(t,y_data,color="red",linewidth=3)
    plt.title(title)
    plt.xlabel("Time (s)")
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.figtext(0.15,0.02,f"U = {U} J",fontsize=9,color="red")
    plt.figtext(0.02,0.02,f"ΔK = {d_K:.2f} J",fontsize=9,color="darkred")
    plt.show()

    return data2

# ------- PROJECTILE MOTION -------
def projectile_motion(t, v0, h0, theta,  m, diagram):

    angle = np.radians(theta)

    vx = v0 * np.cos(angle)
    vy = v0 * np.sin(angle)

    x = vx * t
    y = h0 + vy * t - 0.5 * g * t**2

    landing_index = np.where(y <= 0)[0]

    if len(landing_index) > 0:
        cutoff = landing_index[0] + 1

        t = t[:cutoff]
        x = x[:cutoff]
        y = y[:cutoff]

    y = np.maximum(y,0)

    vy_t = vy - g * t
    v_t = np.sqrt(vx**2 + vy_t**2)

    K = 0.5 * m * v_t**2
    U = m * g * y

    K_init = 0.5 * m * v0**2
    K_final = K[-1]
    d_K = K_final - K_init

    U_start = m * g * h0
    U_final = U[-1]
    dU = U_start - U_final


    data3 = {
        "Time(s)": t, 
        "Horizontal Position(m)": x, 
        "Velocity(m/s)": v_t,
        "Kinetic Energy(J)": K,
        "Potential Energy(J)": U
    }

    if diagram == "x-t":
        plt.figure(figsize=(8, 5))
        plt.plot(t,x,color="red",linewidth=3)
        plt.title("Projectile Motion: x-t")
        plt.xlabel("Time (s)")
        plt.ylabel("Horizontal Distance (m)")
        plt.grid(True)
        plt.figtext(0.15,0.02,f"ΔU = {dU:.2f} J",fontsize=9,color="red")
        plt.figtext(0.02,0.02,f"ΔK = {d_K:.2f} J",fontsize=9,color="darkred")
        plt.show()


    elif diagram == "y-t":
        plt.figure(figsize=(8, 5))
        plt.plot(t,y,color="red",linewidth=3)
        plt.title("Projectile Motion: y-t")
        plt.xlabel("Time (s)")
        plt.ylabel("Vertical Distance (m)")
        plt.grid(True)
        plt.figtext(0.15,0.02,f"ΔU = {dU:.2f} J",fontsize=9,color="red")
        plt.figtext(0.02,0.02,f"ΔK = {d_K:.2f} J",fontsize=9,color="darkred")
        plt.show()

    elif diagram == "Kinetic Energy":
        plt.figure(figsize=(8, 5))
        plt.plot(t,K,color="red",linewidth=3)
        plt.title("Projectile Motion: Kinetic Energy")
        plt.xlabel("Time (s)")
        plt.ylabel("Kinetic Energy (J)")
        plt.grid(True)
        plt.figtext(0.15,0.02,f"ΔU = {dU:.2f} J",fontsize=9,color="red")
        plt.figtext(0.02,0.02,f"ΔK = {d_K:.2f} J",fontsize=9,color="darkred")
        plt.show()

    elif diagram == "Potential Energy":
        plt.figure(figsize=(8, 5))
        plt.plot(t,U,color="red",linewidth=3)
        plt.title("Projectile Motion: Potential Energy")
        plt.xlabel("Time (s)")
        plt.ylabel("Potential Energy (J)")
        plt.grid(True)
        plt.figtext(0.15,0.02,f"ΔU = {dU:.2f} J",fontsize=9,color="red")
        plt.figtext(0.02,0.02,f"ΔK = {d_K:.2f} J",fontsize=9,color="darkred")
        plt.show()

    elif diagram == "x-y":
        plt.figure(figsize=(8, 5))
        plt.plot(x,y,color="red",linewidth=3)
        plt.title("Projectile Trajectory (x-y)")
        plt.xlabel("Horizontal Distance (m)")
        plt.ylabel("Vertical Distance (m)")
        plt.grid(True)
        plt.figtext(0.15,0.02,f"ΔU = {dU:.2f} J",fontsize=9,color="red")
        plt.figtext(0.02,0.02,f"ΔK = {d_K:.2f} J",fontsize=9,color="darkred")
        plt.show()

    return data3

def shm(t, v0, m, A, k, diagram):

    omega = np.sqrt(k/m)
    x = A * np.cos(omega*t)
    v = -A * omega * np.sin(omega*t)

    K = 0.5 * m * v**2
    U = 0.5 * k * x**2

    data3 = {
        "Time(s)": t, 
        "Horizontal Position(m)": x, 
        "Velocity(m/s)": v0,
        "Kinetic Energy(J)": K,
        "Potential Energy(J)": U
    }

    plt.figure(figsize=(8, 5))
    plt.plot(t,x,color="red",linewidth=3)
    plt.title("Simple Harmonic Motion: x-t")
    plt.xlabel("Time (s)")
    plt.ylabel("Displacement (m)")
    plt.grid(True)
    plt.show()
    
# ---------------- MAIN SIMULATION ----------------

def simulate():

    global data

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
        m = float(mass_entry.get())

        t = np.linspace(0,t_max,100)

        # ---------------- LINEAR MOTION ----------------

        if motion == "Linear Motion":
            data = linear_motion(t, v0, diagram)

        # ---------------- ACCELERATED MOTION ----------------

        elif motion == "Accelerated Motion":

            a = float(acceleration_entry.get())
            data = accelerated_motion(t, v0, m, a, diagram)

        # ---------------- PROJECTILE MOTION ----------------

        elif motion == "Projectile Motion":

            theta = float(angle_entry.get())
            h0 = float(height_entry.get())

            data = projectile_motion(t, v0, h0, theta, m, diagram)

        # ---------------- SIMPLE HARMONIC MOTION ----------------

        elif motion == "Simple Harmonic Motion":

            k = float(k_entry.get())
            A = float(displacement_entry.get())
            omega = np.sqrt(k/m)

            data = shm(t, v0, m, A, k, diagram)

            

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
    text="Launch Angle (degrees):"
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
    y=560,
    anchor="center"
)


# Simulate button

simulate_button = tk.Button(
    button_frame,
    text="Run Simulation",
    font=("Arial",13,"bold"),
    bg="lightblue",
    width=12,
    command=simulate
)


# Reset button

reset_button = tk.Button(
    button_frame,
    text="Reset",
    font=("Arial",13,"bold"),
    bg="lightblue",
    width=9,
    command=reset
)


# Export CSV button

export_button = tk.Button(
    button_frame,
    text="Export CSV",
    font=("Arial",13,"bold"),
    bg="lightblue",
    width=10,
    command=export_csv
)


simulate_button.pack(side="left",padx=5)
reset_button.pack(side="left",padx=5)
export_button.pack(side="left",padx=5)


# ---------------- START ----------------

motion_var.trace_add("write",update_diagrams)
orbit_var.trace_add("write",update_orbits)

update_diagrams()
window.mainloop()