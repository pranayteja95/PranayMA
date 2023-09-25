import sqlite3
import pydicom
import io
import pandas as pd
import plotly.subplots as sp
import plotly.graph_objects as go

conn = sqlite3.connect('dicom_metadata.db')
cursor = conn.cursor()

cursor.execute('SELECT id, dicom_data FROM DICOM')
dicom_rows = cursor.fetchall()

cursor.execute('SELECT id, dicom_id, tag_name, tag_value FROM Metadata')
metadata_rows = cursor.fetchall()

metadata_df = pd.DataFrame(metadata_rows, columns=['metadata_id', 'dicom_id', 'tag_name', 'tag_value'])

dicom_images = []
dicom_tags = []

for dicom_row in dicom_rows:
    dicom_id, dicom_blob = dicom_row

    dicom_bytes = io.BytesIO(dicom_blob)

    ds = pydicom.dcmread(dicom_bytes)

    pixel_data = ds.pixel_array

    dicom_images.append(pixel_data)

    metadata_for_dicom = metadata_df[metadata_df['dicom_id'] == dicom_id]
    dicom_tags.append(metadata_for_dicom)

num_plots = len(dicom_tags)

fig = sp.make_subplots(rows=num_plots, cols=1, subplot_titles=[f'DICOM Tag {i + 1}' for i in range(num_plots)], shared_xaxes=True)

for i in range(num_plots):
    scatter = go.Scatter(x=dicom_tags[i]['tag_value'], y=dicom_images[i], text=dicom_tags[i]['tag_name'])
    fig.add_trace(scatter, row=i + 1, col=1)

fig.update_layout(height=400 * num_plots, showlegend=False)
fig.update_yaxes(title_text='DICOM Images', row=num_plots, col=1)
fig.update_xaxes(title_text='DICOM Tag Values', row=num_plots, col=1)
fig.update_xaxes(showticklabels=False)

fig.show()

conn.close()
