from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import calendar
import os

app = Flask(__name__)

# Konfigurasi database
if os.environ.get('VERCEL'):
    # Untuk Vercel, gunakan PostgreSQL
    database_uri = os.environ.get('DATABASE_URL')
    
    # Pastikan sslmode=require ada di URI
    if 'sslmode=require' not in database_uri:
        if '?' in database_uri:
            database_uri += '&sslmode=require'
        else:
            database_uri += '?sslmode=require'
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
else:
    # Untuk lokal, gunakan SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pelanggaran.db'

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'kunci_rahasia_default')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Import models
from models import User, JenisPelanggaran, Pelanggaran

# Inisialisasi database
with app.app_context():
    try:
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
    except Exception as e:
        print(f"Database error: {e}")

# Routes tetap sama...
