from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    pelanggaran = db.relationship('Pelanggaran', backref='user', lazy=True)

class JenisPelanggaran(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    poin = db.Column(db.Integer, nullable=False)
    pelanggaran = db.relationship('Pelanggaran', backref='jenis_pelanggaran', lazy=True)

class Pelanggaran(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    jenis_pelanggaran_id = db.Column(db.Integer, db.ForeignKey('jenis_pelanggaran.id'), nullable=False)
    tanggal = db.Column(db.Date, nullable=False)
    catatan = db.Column(db.Text)
