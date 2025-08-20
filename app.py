from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import calendar
import os
import io
from vercel_blob import put, get, del_

app = Flask(__name__)

# Konfigurasi untuk Vercel Blob
if os.environ.get('VERCEL'):
    # Gunakan Vercel Blob untuk menyimpan database
    BLOB_TOKEN = os.environ.get('BLOB_READ_WRITE_TOKEN')
    
    # Coba download database dari Blob
    try:
        blob_data = get('pelanggaran.db', token=BLOB_TOKEN)
        with open('pelanggaran.db', 'wb') as f:
            f.write(blob_data)
    except:
        # Jika tidak ada, buat database baru
        pass
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pelanggaran.db'
else:
    # Untuk lokal, gunakan SQLite biasa
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pelanggaran.db'

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'kunci_rahasia_default')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Import models
from models import User, JenisPelanggaran, Pelanggaran

# Fungsi untuk menyimpan database ke Blob
def save_database_to_blob():
    if os.environ.get('VERCEL'):
        with open('pelanggaran.db', 'rb') as f:
            blob_data = f.read()
        put('pelanggaran.db', blob_data, token=BLOB_TOKEN)

# Inisialisasi database
with app.app_context():
    db.create_all()
    
    # Tambah data sample hanya jika database kosong
    if User.query.count() == 0:
        users = [
            User(nama='Ahmad'),
            User(nama='Budi'),
            User(nama='Citra')
        ]
        db.session.bulk_save_objects(users)
        
        jenis_pelanggaran = [
            JenisPelanggaran(nama='Terlambat', poin=5),
            JenisPelanggaran(nama='Tidak Memakai Seragam', poin=3),
            JenisPelanggaran(nama='Meninggalkan Tugas', poin=10)
        ]
        db.session.bulk_save_objects(jenis_pelanggaran)
        db.session.commit()
        save_database_to_blob()

# Routes tetap sama...

# Tambahkan fungsi untuk menyimpan database setiap ada perubahan
@app.after_request
def after_request(response):
    if request.method in ['POST', 'PUT', 'DELETE']:
        save_database_to_blob()
    return response

# Handler untuk Vercel
def handler(event=None, context=None):
    return app

if __name__ == '__main__':
    app.run(debug=True)
