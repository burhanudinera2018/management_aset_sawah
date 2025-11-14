from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class AsetSawah(db.Model):
    __tablename__ = 'aset_sawah'
    aset_id = db.Column(db.Integer, primary_key=True)
    nama_sebutan = db.Column(db.String(255), nullable=False)
    nomor_sertifikat = db.Column(db.String(100), unique=True, nullable=False)
    luas_m2 = db.Column(db.Numeric(10, 2), nullable=False)
    luas_boto = db.Column(db.Numeric(10, 2))
    lokasi = db.Column(db.String(200), nullable=False)
    tanaman_saat_ini = db.Column(db.String(100))
    status_sewa = db.Column(db.String(50), nullable=False, default='Tersedia')
    tanggal_dibuat = db.Column(db.DateTime, default=datetime.utcnow)

    transaksi = db.relationship('TransaksiSewa', back_populates='aset', cascade='all, delete-orphan')


class Penyewa(db.Model):
    __tablename__ = 'penyewa'
    penyewa_id = db.Column(db.Integer, primary_key=True)
    nama_lengkap = db.Column(db.String(255), nullable=False)
    nik = db.Column(db.String(20), unique=True, nullable=False)
    alamat = db.Column(db.Text)
    nomor_kontak = db.Column(db.String(50))

    transaksi = db.relationship('TransaksiSewa', back_populates='penyewa', cascade='all, delete-orphan')


class TransaksiSewa(db.Model):
    __tablename__ = 'transaksi_sewa'
    sewa_id = db.Column(db.Integer, primary_key=True)
    aset_id = db.Column(db.Integer, db.ForeignKey('aset_sawah.aset_id', ondelete='CASCADE'))
    penyewa_id = db.Column(db.Integer, db.ForeignKey('penyewa.penyewa_id', ondelete='CASCADE'))
    tanggal_mulai = db.Column(db.Date, nullable=False)
    tanggal_akhir = db.Column(db.Date, nullable=False)
    durasi_bulan = db.Column(db.Integer, nullable=False)
    nilai_sewa = db.Column(db.Numeric(15, 2), nullable=False)
    jenis_tanaman_disepakati = db.Column(db.String(100))
    tanggal_transaksi = db.Column(db.DateTime, default=datetime.utcnow)

    aset = db.relationship('AsetSawah', back_populates='transaksi')
    penyewa = db.relationship('Penyewa', back_populates='transaksi')
