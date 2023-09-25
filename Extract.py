import sqlite3
import pydicom
import os

import warnings
warnings.filterwarnings("ignore")

def create_database():
    conn = sqlite3.connect('dicom_metadata.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS DICOM (
        id INTEGER PRIMARY KEY,
        dicom_data BLOB
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Metadata (
        id INTEGER PRIMARY KEY,
        dicom_id INTEGER,
        tag_name TEXT,
        tag_value TEXT,
        FOREIGN KEY(dicom_id) REFERENCES DICOM(id)
    )
    ''')

    conn.commit()
    conn.close()

def store_dicom_data(dicom_file):
    with open(dicom_file, 'rb') as file:
        dicom_data = file.read()

    conn = sqlite3.connect('dicom_metadata.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO DICOM (dicom_data) VALUES (?)", (sqlite3.Binary(dicom_data),))
    dicom_id = cursor.lastrowid

    ds = pydicom.dcmread(dicom_file)

    for elem in ds:
        tag_name = str(elem.tag)
        tag_value = str(elem.value)
        cursor.execute("INSERT INTO Metadata (dicom_id, tag_name, tag_value) VALUES (?, ?, ?)", (dicom_id, tag_name, tag_value))

    conn.commit()
    conn.close()

def process_directory(directory_path):
    for filename in os.listdir(directory_path):
        if filename.endswith(".dcm"):
            file_path = os.path.join(directory_path, filename)
            store_dicom_data(file_path)

if __name__ == "__main__":
    create_database()
    
    dicom_directory = "C:\\Users\\prana\\Desktop\\archive"
    
    process_directory(dicom_directory)
