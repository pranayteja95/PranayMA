import sqlite3                  #Updating images based on unique id selection
import pydicom
import io
import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

conn = sqlite3.connect('dicom_metadata.db')
cursor = conn.cursor()

cursor.execute('SELECT DISTINCT id FROM DICOM')
unique_ids = cursor.fetchall()

root = tk.Tk()
root.title("Visualization")

selected_id = tk.StringVar()
id_dropdown = ttk.Combobox(root, textvariable=selected_id)
id_dropdown['values'] = [str(id_[0]) for id_ in unique_ids]
id_dropdown.grid(row=0, column=0, padx=10, pady=10)

figure = Figure(figsize=(6, 6))
image_canvas = FigureCanvasTkAgg(figure, master=root)
image_canvas.get_tk_widget().grid(row=1, column=0, padx=10, pady=10)

def update_image():
    selected_value = selected_id.get()
    if selected_value:
        selected_id_int = int(selected_value)

        cursor.execute('SELECT dicom_data FROM DICOM WHERE id = ?', (selected_id_int,))
        dicom_blob = cursor.fetchone()[0]

        dicom_bytes = io.BytesIO(dicom_blob)

        ds = pydicom.dcmread(dicom_bytes)

        pixel_data = ds.pixel_array

        figure.clear()
        ax = figure.add_subplot(111)
        ax.imshow(pixel_data, cmap='gray')
        ax.set_title(f'DICOM Image for ID {selected_id_int}')
        image_canvas.draw()

update_button = tk.Button(root, text="Update Image", command=update_image)
update_button.grid(row=0, column=1, padx=10, pady=10)

root.mainloop()

conn.close()
