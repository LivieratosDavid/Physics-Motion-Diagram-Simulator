import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
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
window.geometry("500x700")
window.resizable(False, False)

# ---------------- VARIABLES ----------------

motion_var = tk.StringVar(value="Linear Motion")
diagram_var = tk.StringVar(value="x-t")
orbit_var = tk.StringVar(value="None")

# ---------------- DATA HANDLING ----------------

data = {}

# ---------------- FUNCTIONS ----------------

def clicked_motion(event, photo):
    win = tk.Toplevel()
    win.title("Equations Used")
    win.geometry("350x700")

    img = tk.PhotoImage(file=photo)

    canvas = tk.Canvas(win, width=354, height=700)
    scrollbar = tk.Scrollbar(win, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_image(0, 0, anchor="nw", image=img)
    canvas.configure(scrollregion=canvas.bbox("all"))

    win.photo = img

def clicked_energy(event):
    win = tk.Toplevel()
    win.title("Equations Used")
    win.geometry("226x272")

    photo = tk.PhotoImage(file='energy.png')
    image = tk.Label(win, image=photo)
    image.pack()

    image.photo = photo

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

def compare_csv():
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

    # ---------------- COMPARISON WINDOW ----------------

    compare_window = tk.Toplevel(window)
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

    # ---------------- PLOT ----------------

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

    # ---------------- BUTTON ----------------

    tk.Button(
        compare_window,
        text="Compare",
        font=("Arial", 12, "bold"),
        command=plot_comparison
    ).pack(pady=10)

def save_img(event):

    filename = filedialog.asksaveasfilename(
            title="Save Image",
            defaultextension=".png",
            filetypes=[("PNG files", '*.png')]
        )

    if not filename:
        return

    plt.savefig(filename, dpi = 300, bbox_inches='tight')

    messagebox.showinfo("Image Saved", "Your image was saved!")

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

    fig, ax = plt.subplots(figsize=(8, 5))
    fig.subplots_adjust(top=0.80)
    
    button_ax = fig.add_axes([0.125, 0.85, 0.2, 0.07])
    button_ax.set_xticks([])
    button_ax.set_yticks([])

    button = Button(button_ax, "Show Equations Used")

    ax.plot(t, y_data, color="red", linewidth=3)
    ax.set_title(title)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel(ylabel)
    ax.grid(True)

    img_button_ax = fig.add_axes([0.75, 0.85, 0.15, 0.07])
    img_button_ax.set_xticks([])
    img_button_ax.set_yticks([])

    img_button = Button(img_button_ax, "Save Image")

    img_button.on_clicked(save_img)
    button.on_clicked(lambda event: clicked_motion(event, 'linear.png'))
    

    fig.text(0.15, 0.02, f"U = {U} J", fontsize=9, color="red")
    fig.text(0.02, 0.02, f"ΔK = {dK} J", fontsize=9, color="darkred")

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
        fig, ax = plt.subplots(figsize=(8, 5))
        fig.subplots_adjust(top=0.80)

        button_ax = fig.add_axes([0.125, 0.85, 0.2, 0.07])
        button_ax.set_xticks([])
        button_ax.set_yticks([])
        button = Button(button_ax, "Show Equations Used")

        ax.plot(t, x, color="red", linewidth=3)
        ax.set_title("Accelerated Motion: x-t")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Distance (m)")
        ax.grid(True)

        img_button_ax = fig.add_axes([0.75, 0.85, 0.15, 0.07])
        img_button_ax.set_xticks([])
        img_button_ax.set_yticks([])

        img_button = Button(img_button_ax, "Save Image")

        fig.text(0.15, 0.02, f"U = {U} J", fontsize=9, color="red")
        fig.text(0.02, 0.02, f"ΔK = {d_K:.2f} J", fontsize=9, color="darkred")

        img_button.on_clicked(save_img)
        button.on_clicked(lambda event: clicked_motion(event, "acc.png"))
        plt.show()


    elif diagram == "v-t":
        fig, ax = plt.subplots(figsize=(8, 5))
        fig.subplots_adjust(top=0.80)

        button_ax = fig.add_axes([0.125, 0.85, 0.2, 0.07])
        button_ax.set_xticks([])
        button_ax.set_yticks([])
        button = Button(button_ax, "Show Equations Used")

        ax.plot(t, v, color="red", linewidth=3)
        ax.set_title("Accelerated Motion: v-t")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Velocity (m/s)")
        ax.grid(True)

        img_button_ax = fig.add_axes([0.75, 0.85, 0.15, 0.07])
        img_button_ax.set_xticks([])
        img_button_ax.set_yticks([])
        
        img_button = Button(img_button_ax, "Save Image")
        
        fig.text(0.15, 0.02, f"U = {U} J", fontsize=9, color="red")
        fig.text(0.02, 0.02, f"ΔK = {d_K:.2f} J", fontsize=9, color="darkred")

        img_button.on_clicked(save_img)
        button.on_clicked(lambda event: clicked_motion(event, "acc.png"))
        plt.show()


    elif diagram == "Kinetic Energy":
        fig, ax = plt.subplots(figsize=(8, 5))
        fig.subplots_adjust(top=0.80)

        button_ax = fig.add_axes([0.125, 0.85, 0.2, 0.07])
        button_ax.set_xticks([])
        button_ax.set_yticks([])
        button = Button(button_ax, "Show Equations Used")

        ax.plot(t, K, color="red", linewidth=3)
        ax.set_title("Accelerated Motion: Kinetic Energy")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Kinetic Energy (J)")
        ax.grid(True)

        img_button_ax = fig.add_axes([0.75, 0.85, 0.15, 0.07])
        img_button_ax.set_xticks([])
        img_button_ax.set_yticks([])
        
        img_button = Button(img_button_ax, "Save Image")

        
        fig.text(0.15, 0.02, f"U = {U} J", fontsize=9, color="red")
        fig.text(0.02, 0.02, f"ΔK = {d_K:.2f} J", fontsize=9, color="darkred")

        img_button.on_clicked(save_img)
        button.on_clicked(clicked_energy)
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
        "Time (s)": t, 
        "Horizontal Position (m)": x,
        "Vertical Position (m)": y,
        "Velocity (m/s)": v_t,
        "Kinetic Energy (J)": K,
        "Potential Energy (J)": U
    }

    if diagram == "x-t":

        fig, ax = plt.subplots(figsize=(8, 5))
        fig.subplots_adjust(top=0.80)
    
        button_ax = fig.add_axes([0.125, 0.85, 0.2, 0.07])
        button_ax.set_xticks([])
        button_ax.set_yticks([])
        button = Button(button_ax, "Show Equations Used")

        ax.plot(t,x,color="red",linewidth=3)
        ax.set_title("Projectile Motion: x-t")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Horizontal Distance (m)")
        ax.grid(True)
        fig.text(0.15,0.02,f"ΔU = {dU:.2f} J",fontsize=9,color="red")
        fig.text(0.02,0.02,f"ΔK = {d_K:.2f} J",fontsize=9,color="darkred") 

        img_button_ax = fig.add_axes([0.75, 0.85, 0.15, 0.07])
        img_button_ax.set_xticks([])
        img_button_ax.set_yticks([])

        img_button = Button(img_button_ax, "Save Image")

        img_button.on_clicked(save_img)   
        button.on_clicked(lambda event: clicked_motion(event, "proj.png"))

        plt.show()


    elif diagram == "y-t":
        fig, ax = plt.subplots(figsize=(8, 5))
        fig.subplots_adjust(top=0.80)
    
        button_ax = fig.add_axes([0.125, 0.85, 0.2, 0.07])
        button_ax.set_xticks([])
        button_ax.set_yticks([])
        button = Button(button_ax, "Show Equations Used")

        ax.plot(t,y,color="red",linewidth=3)
        ax.set_title("Projectile Motion: y-t")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Vertical Distance (m)")
        ax.grid(True)

        img_button_ax = fig.add_axes([0.75, 0.85, 0.15, 0.07])
        img_button_ax.set_xticks([])
        img_button_ax.set_yticks([])

        img_button = Button(img_button_ax, "Save Image")

        img_button.on_clicked(save_img)

        fig.text(0.15,0.02,f"ΔU = {dU:.2f} J",fontsize=9,color="red")
        fig.text(0.02,0.02,f"ΔK = {d_K:.2f} J",fontsize=9,color="darkred")    

        button.on_clicked(lambda event: clicked_motion(event, "proj.png"))
        plt.show()

    elif diagram == "Kinetic Energy":
        fig, ax = plt.subplots(figsize=(8, 5))
        fig.subplots_adjust(top=0.80)

        button_ax = fig.add_axes([0.125, 0.85, 0.2, 0.07])
        button_ax.set_xticks([])
        button_ax.set_yticks([])
        button = Button(button_ax, "Show Equations Used")

        ax.plot(t,K,color="red",linewidth=3)
        ax.set_title("Projectile Motion: Kinetic Energy")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Kinetic Energy (J)")
        ax.grid(True)

        img_button_ax = fig.add_axes([0.75, 0.85, 0.15, 0.07])
        img_button_ax.set_xticks([])
        img_button_ax.set_yticks([])

        img_button = Button(img_button_ax, "Save Image")

        img_button.on_clicked(save_img)

        fig.text(0.15,0.02,f"ΔU = {dU:.2f} J",fontsize=9,color="red")
        fig.text(0.02,0.02,f"ΔK = {d_K:.2f} J",fontsize=9,color="darkred")    

        button.on_clicked(clicked_energy)
        plt.show()

    elif diagram == "Potential Energy":
        fig, ax = plt.subplots(figsize=(8, 5))
        fig.subplots_adjust(top=0.80)
    
        button_ax = fig.add_axes([0.125, 0.85, 0.2, 0.07])
        button_ax.set_xticks([])
        button_ax.set_yticks([])
        button = Button(button_ax, "Show Equations Used")

        ax.plot(t,U,color="red",linewidth=3)
        ax.set_title("Projectile Motion: Potential Energy")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Potential Energy (J)")
        ax.grid(True)

        img_button_ax = fig.add_axes([0.75, 0.85, 0.15, 0.07])
        img_button_ax.set_xticks([])
        img_button_ax.set_yticks([])

        img_button = Button(img_button_ax, "Save Image")

        img_button.on_clicked(save_img)
        
        fig.text(0.15,0.02,f"ΔU = {dU:.2f} J",fontsize=9,color="red")
        fig.text(0.02,0.02,f"ΔK = {d_K:.2f} J",fontsize=9,color="darkred")    

        button.on_clicked(clicked_energy)
        plt.show()

    elif diagram == "x-y":
        fig, ax = plt.subplots(figsize=(8, 5))
        fig.subplots_adjust(top=0.80)

        button_ax = fig.add_axes([0.125, 0.85, 0.2, 0.07])
        button_ax.set_xticks([])
        button_ax.set_yticks([])
        button = Button(button_ax, "Show Equations Used")

        img_button_ax = fig.add_axes([0.75, 0.85, 0.15, 0.07])
        img_button_ax.set_xticks([])
        img_button_ax.set_yticks([])
        img_button = Button(img_button_ax, "Save Image")

        ax.plot(x, y, color="red", linewidth=3)
        ax.set_title("Projectile Trajectory (x-y)")
        ax.set_xlabel("Horizontal Distance (m)")
        ax.set_ylabel("Vertical Distance (m)")
        ax.grid(True)

        fig.text(0.15, 0.02, f"ΔU = {dU:.2f} J", fontsize=9, color="red")
        fig.text(0.02, 0.02, f"ΔK = {d_K:.2f} J", fontsize=9, color="darkred")

        img_button.on_clicked(save_img)
        button.on_clicked(lambda event: clicked_motion(event, photo="proj.png"))

        plt.show()

    return data3

# ------ SHM -------
def shm(t, v, m, A, k, diagram):

    omega = np.sqrt(k/m)
    x = A * np.cos(omega*t)
    v = -A * omega * np.sin(omega*t)

    K = 0.5 * m * v**2
    U = 0.5 * k * x**2

    data4 = {
        "Time (s)": t, 
        "Horizontal Position (m)": x, 
        "Velocity (m/s)": v,
        "Kinetic Energy (J)": K,
        "Potential Energy (J)": U
    }

    if diagram == "x-t":
        fig, ax = plt.subplots(figsize=(8, 5))
        fig.subplots_adjust(top=0.80)

        button_ax = fig.add_axes([0.125, 0.85, 0.2, 0.07])
        button_ax.set_xticks([])
        button_ax.set_yticks([])
        button = Button(button_ax, "Show Equations Used")

        img_button_ax = fig.add_axes([0.75, 0.85, 0.15, 0.07])
        img_button_ax.set_xticks([])
        img_button_ax.set_yticks([])

        img_button = Button(img_button_ax, "Save Image")

        img_button.on_clicked(save_img)
        button.on_clicked(lambda event: clicked_motion(event, photo="shm.png"))

        ax.plot(t, x, color="red", linewidth=3)
        ax.set_title("Simple Harmonic Motion: x-t")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Displacement (m)")

        plt.show()

    return data4
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

        t = np.linspace(0,t_max,100)

        if t_max <= 0: 
            messagebox.showerror("Syntax Error","Time cannot be >= 0")

        else:
        # ---------------- LINEAR MOTION ----------------

            if motion == "Linear Motion":
                data = linear_motion(t, v0, diagram)

            # ---------------- ACCELERATED MOTION ----------------

            elif motion == "Accelerated Motion":

                a = float(acceleration_entry.get())
                m = float(mass_entry.get())

                if m <= 0: 
                    messagebox.showerror("Syntax Error", "Mass cannot be >= 0")
                    return

                data = accelerated_motion(t, v0, m, a, diagram)

            # ---------------- PROJECTILE MOTION ----------------

            elif motion == "Projectile Motion":

                theta = float(angle_entry.get())
                h0 = float(height_entry.get())
                m = float(mass_entry.get())

                if m <= 0: 
                    messagebox.showerror("Syntax Error", "Mass cannot be >= 0")
                    return
                if 0 >= theta <= 90:
                    messagebox.showerror("Syntax Error", "Angle must be 0-89 degrees")
                    return

                data = projectile_motion(t, v0, h0, theta, m, diagram)

            # ---------------- SIMPLE HARMONIC MOTION ----------------

            elif motion == "Simple Harmonic Motion":

                k = float(k_entry.get())
                A = float(displacement_entry.get())
                m = float(mass_entry.get())

                if m <= 0: 
                    messagebox.showerror("Syntax Error", "Mass cannot be >= 0")
                    return
                if k <= 0:
                    messagebox.showerror("Syntax Error", "Spring constant cannot be <= 0")
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
    command=export_csv

)

compare_button = tk.Button(
    bottom_buttons,
    text="Compare CSV",
    font=("Arial", 13, "bold"),
    bg="lightblue",
    width=12,
    command=compare_csv

)

export_button.pack(side="left", padx=5, pady=5)
compare_button.pack(side="left", padx=5, pady=5)


# ---------------- START ----------------

motion_var.trace_add("write",update_diagrams)
orbit_var.trace_add("write",update_orbits)

update_diagrams()
window.mainloop()