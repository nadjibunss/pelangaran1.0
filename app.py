from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import calendar
import os

app = Flask(__name__)

# Konfigurasi database
if os.environ.get('VERCEL'):
    # Untuk Vercel, gunakan PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
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

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tambah_pelanggaran', methods=['GET', 'POST'])
def tambah_pelanggaran():
    if request.method == 'POST':
        user_id = request.form['user_id']
        jenis_pelanggaran_id = request.form['jenis_pelanggaran_id']
        tanggal = datetime.strptime(request.form['tanggal'], '%Y-%m-%d').date()
        catatan = request.form['catatan']
        
        pelanggaran = Pelanggaran(
            user_id=user_id,
            jenis_pelanggaran_id=jenis_pelanggaran_id,
            tanggal=tanggal,
            catatan=catatan
        )
        db.session.add(pelanggaran)
        db.session.commit()
        flash('Pelanggaran berhasil dicatat!', 'success')
        return redirect(url_for('tambah_pelanggaran'))
    
    users = User.query.all()
    jenis_pelanggaran = JenisPelanggaran.query.all()
    return render_template('tambah_pelanggaran.html', users=users, jenis_pelanggaran=jenis_pelanggaran)

@app.route('/laporan_bulanan/<int:tahun>/<int:bulan>')
def laporan_bulanan(tahun, bulan):
    pelanggaran_list = Pelanggaran.query.filter(
        db.extract('year', Pelanggaran.tanggal) == tahun,
        db.extract('month', Pelanggaran.tanggal) == bulan
    ).all()
    
    user_poin = {}
    for p in pelanggaran_list:
        nama_user = p.user.nama
        poin = p.jenis_pelanggaran.poin
        user_poin[nama_user] = user_poin.get(nama_user, 0) + poin
    
    sorted_users = sorted(user_poin.items(), key=lambda x: x[1], reverse=True)
    nama_bulan = calendar.month_name[bulan]
    
    return render_template('laporan_bulanan.html', 
                          tahun=tahun, 
                          nama_bulan=nama_bulan,
                          user_poin=sorted_users)

# Handler untuk Vercel
def handler(event=None, context=None):
    return app

if __name__ == '__main__':
    app.run(debug=True)
