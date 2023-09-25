import sqlite3              #images with metadata
import pydicom
import io
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

conn = sqlite3.connect('dicom_metadata.db')
cursor = conn.cursor()

cursor.execute('SELECT DISTINCT id FROM DICOM')
unique_ids = cursor.fetchall()

root = tk.Tk()
root.title("DICOM Image Viewer")

frame = ttk.Frame(root)
frame.pack(padx=10, pady=10)

selected_id = tk.StringVar()
id_dropdown = ttk.Combobox(frame, textvariable=selected_id)
id_dropdown['values'] = [str(id_[0]) for id_ in unique_ids]
id_dropdown.grid(row=0, column=0, padx=10, pady=10)

metadata_label = ttk.Label(frame, text="")
metadata_label.grid(row=0, column=1, padx=10, pady=10)

def update_image_and_metadata():
    selected_value = selected_id.get()
    if selected_value:
        try:
            selected_id_int = int(selected_value)

            cursor.execute('SELECT dicom_data FROM DICOM WHERE id = ?', (selected_id_int,))
            dicom_blob = cursor.fetchone()[0]

            cursor.execute('SELECT tag_name, tag_value FROM Metadata WHERE dicom_id = ?', (selected_id_int,))
            metadata_rows = cursor.fetchall()

            metadata_text = "\n".join([f"{row[0]}: {row[1]}" for row in metadata_rows])

            metadata_label.config(text=metadata_text)

            dicom_bytes = io.BytesIO(dicom_blob)

            ds = pydicom.dcmread(dicom_bytes)

            pixel_data = ds.pixel_array

            pil_image = Image.fromarray(pixel_data)

            pil_image = pil_image.convert('L')

            pil_image = pil_image.resize((400, 300), Image.LANCZOS)

            tk_image = ImageTk.PhotoImage(pil_image)


            canvas.config(width=pil_image.width, height=pil_image.height)
            canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)
            canvas.photo = tk_image

        except Exception as e:      # Handling exceptions occuring during image conversion or display
            error_message = f"Error: {str(e)}"
            metadata_label.config(text=error_message)
            print(error_message)

update_button = ttk.Button(frame, text="Update Image and Metadata", command=update_image_and_metadata)
update_button.grid(row=0, column=2, padx=10, pady=10)

canvas = tk.Canvas(frame)
canvas.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

root.mainloop()

conn.close()
