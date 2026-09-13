import matplotlib.pyplot as plt
import tkinter as tk 
from matplotlib.widgets import Button as MPLButton
from saving import CSVManager
from tkinter import filedialog
from tkinter import ttk, messagebox

class Rendering:
    def __init__(self, photo):
        self.photo = photo

    def save_img(self, event):
        filename = filedialog.asksaveasfilename(
                title="Save Image",
                defaultextension=".png",
                filetypes=[("PNG files", '*.png')]
            )

        if not filename:
            return

        plt.savefig(filename, dpi = 300, bbox_inches='tight')
        messagebox.showinfo("Image Saved", "Your image was saved!")

    def clicked_motion(self, event):
        win = tk.Toplevel()
        win.title("Equations Used")
        win.geometry("350x700")

        img = tk.PhotoImage(file=self.photo)

        canvas = tk.Canvas(win, width=354, height=700)
        scrollbar = tk.Scrollbar(win, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_image(0, 0, anchor="nw", image=img)
        canvas.configure(scrollregion=canvas.bbox("all"))

        win.photo = img

    def clicked_energy(self, event):
        win = tk.Toplevel()
        win.title("Equations Used")
        win.geometry("226x272")

        energy_photo = tk.PhotoImage(file='energy.png')
        image = tk.Label(win, image=energy_photo)
        image.pack()

        image.photo = energy_photo

    def render_diagrams(self, xdata, y_data, title, xlabel, ylabel, photo=None, energy_button=False, extra_text=None):
        self.photo = photo
        fig, ax = plt.subplots(figsize=(8, 5))
        fig.subplots_adjust(top=0.80)

        img_button_ax = fig.add_axes([0.75, 0.85, 0.15, 0.07])
        img_button_ax.set_xticks([])
        img_button_ax.set_yticks([])
        img_button = MPLButton(img_button_ax, "Save Image")

        eq_ax = fig.add_axes([0.125, 0.85, 0.2, 0.07])
        eq_ax.set_xticks([]); eq_ax.set_yticks([])
        eq_button = MPLButton(eq_ax, "Show Equations Used")

        img_button.on_clicked(self.save_img)

        if energy_button:
            eq_button.on_clicked(self.clicked_energy)
        else:
            eq_button.on_clicked(self.clicked_motion)

        fig.eq_button, fig.img_button = eq_button, img_button

        ax.plot(xdata, y_data, color="red", linewidth=3)
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(True)

        if extra_text:
            for y_pos, text, color in extra_text:
                fig.text(0.5, y_pos, text, ha="left", color=color)

        plt.show()