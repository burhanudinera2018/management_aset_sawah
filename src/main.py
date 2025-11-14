# src/main.py (VERSION FINAL BERSIH DAN STABIL)

import os
import requests 
from datetime import date
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, SubmitField, IntegerField, TextAreaField, DateField
from wtforms.validators import DataRequired, Length
from sqlalchemy.exc import SQLAlchemyError
from geoalchemy2 import Geometry
from decimal import Decimal # <--- BARIS INI WAJIB DITAMBAHKAN

# ===============================================
# KONSTANTA MICROSERVICE
# ===============================================
PRICING_SERVICE_URL = "http://localhost:5001" # <--- Tempatkan di sini

# ---------------------------------------------------
# 1. SETUP APLIKASI DAN DATABASE (WAJIB DI AWAL)
# ---------------------------------------------------

load_dotenv()
app = Flask(__name__)

# Konfigurasi
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret')

db = SQLAlchemy(app)

# ---------------------------------------------------
# 2. DEFINISI MODEL DATABASE
# ---------------------------------------------------

class AsetSawah(db.Model):
    __tablename__ = 'aset_sawah'
    aset_id = db.Column(db.Integer, primary_key=True)
    nama_sebutan = db.Column(db.String(255), nullable=False)
    nomor_sertifikat = db.Column(db.String(100), unique=True, nullable=False)
    luas_m2 = db.Column(db.Numeric(10, 2), nullable=False)
    luas_boto = db.Column(db.Numeric(10, 2))
    lokasi = db.Column(Geometry('POINT', 4326)) 
    tanaman_saat_ini = db.Column(db.String(100))
    status_sewa = db.Column(db.String(50), nullable=False, default='Tersedia')

class Penyewa(db.Model):
    __tablename__ = 'penyewa'
    penyewa_id = db.Column(db.Integer, primary_key=True)
    nama_lengkap = db.Column(db.String(255), nullable=False)
    nik = db.Column(db.String(20), unique=True, nullable=False)
    alamat = db.Column(db.Text)
    nomor_kontak = db.Column(db.String(50))

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
    aset = db.relationship('AsetSawah', backref='transaksi')
    penyewa = db.relationship('Penyewa', backref='transaksi')

class HargaSewa(db.Model):
    __tablename__ = 'harga_sewa'
    id = db.Column(db.Integer, primary_key=True)
    # Harga sewa per boto (Numeric untuk presisi)
    harga_per_boto = db.Column(db.Numeric(10, 2), nullable=False) 
    tanggal_diperbarui = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

# --- Tambahkan Form untuk Pengaturan Harga ---
class HargaForm(FlaskForm):
    harga_per_boto = DecimalField('Harga Sewa per Boto (Rp)', validators=[DataRequired()])
    submit = SubmitField('Simpan Pengaturan')


# ---------------------------------------------------
# 3. FUNGSI KONVERSI DAN DEFINISI FORMS
# ---------------------------------------------------

BOTO_PER_M2 = 14.0 

def convert_m2_to_boto(m2):
    if m2 is not None:
        try:
            return float(m2) / BOTO_PER_M2
        except (TypeError, ZeroDivisionError):
            return None
    return None

class AsetForm(FlaskForm):
    nama_sebutan = StringField('Nama Sebutan', validators=[DataRequired()])
    nomor_sertifikat = StringField('Nomor Sertifikat', validators=[DataRequired()])
    luas_m2 = DecimalField('Luas (m²)', validators=[DataRequired()])
    # HAPUS FIELD LUAS BOTO DARI FORM (Otomatis Dihitung)
    lokasi = StringField('Lokasi (Koordinat / Deskripsi)', 
        description='Format: Longitude,Latitude (Contoh: 112.062692,-7.73961)')
    tanaman_saat_ini = StringField('Tanaman Saat Ini')
    status_sewa = SelectField('Status Sewa', choices=[('Tersedia', 'Tersedia'), ('Disewa', 'Disewa')])
    submit = SubmitField('Simpan')

class PenyewaForm(FlaskForm):
    nama_lengkap = StringField('Nama Lengkap', validators=[DataRequired()])
    nik = StringField('NIK', validators=[DataRequired(), Length(min=16, max=20)])
    alamat = TextAreaField('Alamat')
    nomor_kontak = StringField('Nomor Kontak')
    submit = SubmitField('Simpan')

class TransaksiForm(FlaskForm):
    aset_id = SelectField('Aset Sawah', coerce=int, validators=[DataRequired()])
    penyewa_id = SelectField('Penyewa', coerce=int, validators=[DataRequired()])
    tanggal_mulai = DateField('Tanggal Mulai', validators=[DataRequired()])
    tanggal_akhir = DateField('Tanggal Akhir', validators=[DataRequired()])
    durasi_bulan = IntegerField('Durasi (bulan)', validators=[DataRequired()])
    # HAPUS BARIS INI: nilai_sewa = DecimalField('Nilai Sewa (Rp)', validators=[DataRequired()])
    jenis_tanaman_disepakati = StringField('Jenis Tanaman Disepakati')
    submit = SubmitField('Simpan')


# ---------------------------------------------------
# 4. DEFINISI ROUTES
# ---------------------------------------------------

@app.route('/')
def index():
    return redirect(url_for('list_aset'))

# --------- ASET ROUTES ----------
@app.route('/aset')
def list_aset():
    data = AsetSawah.query.all()
    return render_template('list_aset.html', data=data)

@app.route('/aset/tambah', methods=['GET', 'POST'])
def tambah_aset():
    form = AsetForm()
    if form.validate_on_submit():
        data_aset = form.data.copy()
        data_aset.pop('submit', None)
        data_aset.pop('csrf_token', None)

        # KOREKSI 1A: HITUNG DAN SIMPAN LUAS BOTO
        if 'luas_m2' in data_aset and data_aset['luas_m2']:
            luas_m2_decimal = data_aset['luas_m2'] 
            data_aset['luas_boto'] = convert_m2_to_boto(luas_m2_decimal)
        
        try:
            # 1. Tangani kolom lokasi (konversi ke POINT geometry)
            if 'lokasi' in data_aset and data_aset['lokasi']:
                parts = [p.strip() for p in data_aset['lokasi'].split(',')]
                lon, lat = map(float, parts)
                data_aset['lokasi'] = f'SRID=4326;POINT({lon} {lat})' 
            
            # 2. Simpan ke DB
            new_aset = AsetSawah(**data_aset)
            db.session.add(new_aset)
            db.session.commit()

            flash('Aset baru berhasil ditambahkan.', 'success')
            return redirect(url_for('list_aset'))

        except (ValueError, SQLAlchemyError) as e: 
            db.session.rollback()
            flash(f'Gagal menyimpan aset: {e}', 'danger')
            print(f"Error Detail: {e}") 

    return render_template('form_aset.html', form=form, title='Tambah Aset Sawah')

@app.route('/aset/edit/<int:aset_id>', methods=['GET', 'POST'])
def edit_aset(aset_id):
    aset = AsetSawah.query.get_or_404(aset_id)
    form = AsetForm(obj=aset)
    if form.validate_on_submit():
        
        # HITUNG ULANG LUAS BOTO SAAT EDIT
        if form.luas_m2.data:
            aset.luas_boto = convert_m2_to_boto(form.luas_m2.data)
            
        form.populate_obj(aset)
        db.session.commit()
        flash('Data aset berhasil diperbarui.', 'success')
        return redirect(url_for('list_aset'))
    return render_template('form_aset.html', form=form, title='Edit Aset')

@app.route('/aset/delete/<int:aset_id>', methods=['POST'])
def delete_aset(aset_id):
    aset = AsetSawah.query.get_or_404(aset_id)
    try:
        db.session.delete(aset)
        db.session.commit()
        flash(f'Aset "{aset.nama_sebutan}" berhasil dihapus.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Gagal menghapus aset: {e}', 'danger')
        
    return redirect(url_for('list_aset'))

# --------- PENYEWA ROUTES ----------
@app.route('/penyewa')
def list_penyewa():
    data = Penyewa.query.all()
    return render_template('list_penyewa.html', data=data)

@app.route('/penyewa/tambah', methods=['GET', 'POST'])
def tambah_penyewa():
    form = PenyewaForm()
    if form.validate_on_submit():
        penyewa_baru = Penyewa(
            nama_lengkap=form.nama_lengkap.data,
            nik=form.nik.data,
            alamat=form.alamat.data,
            nomor_kontak=form.nomor_kontak.data
        )
        db.session.add(penyewa_baru)
        db.session.commit()
        flash('Penyewa baru ditambahkan.', 'success')
        return redirect(url_for('list_penyewa'))
    return render_template('form_penyewa.html', form=form, title='Tambah Penyewa')

@app.route('/penyewa/edit/<int:penyewa_id>', methods=['GET', 'POST'])
def edit_penyewa(penyewa_id):
    penyewa = db.session.get(Penyewa, penyewa_id)
    if penyewa is None:
        return "Penyewa tidak ditemukan", 404
    form = PenyewaForm(obj=penyewa)
    if form.validate_on_submit():
        data_update = form.data.copy()
        data_update.pop('submit', None)
        data_update.pop('csrf_token', None)
        for field, value in data_update.items():
            setattr(penyewa, field, value)
        db.session.commit()
        flash('Data Penyewa berhasil diperbarui!', 'success')
        return redirect(url_for('list_penyewa')) 
    return render_template('form_penyewa.html', form=form, title='Edit Data Penyewa')

@app.route('/penyewa/delete/<int:penyewa_id>', methods=['POST'])
def delete_penyewa(penyewa_id):
    penyewa = db.session.get(Penyewa, penyewa_id)
    if penyewa is None:
        flash('Penyewa tidak ditemukan.', 'danger')
        return redirect(url_for('list_penyewa'))
    try:
        db.session.delete(penyewa)
        db.session.commit()
        flash(f'Penyewa "{penyewa.nama_lengkap}" berhasil dihapus.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Gagal menghapus Penyewa: {e}', 'danger')
    return redirect(url_for('list_penyewa'))


# --------- TRANSAKSI ROUTES ----------
@app.route('/transaksi')
def list_transaksi():
    data = TransaksiSewa.query.all()
    return render_template('list_transaksi.html', data=data)

@app.route('/transaksi/tambah', methods=['GET', 'POST'])
def tambah_transaksi():
    
    # 1. INISIALISASI FORM (HARUS DI AWAL)
    form = TransaksiForm()
    # =================================================================
    # KOREKSI: TAMBAH LOGIKA PENGISIAN PILIHAN DARI DATABASE
    # =================================================================
    
    # Ambil semua Aset Sawah dan Penyewa untuk mengisi SelectField
    all_aset = AsetSawah.query.all()
    all_penyewa = Penyewa.query.all()

    # Isi pilihan untuk field aset_id
    form.aset_id.choices = [(a.aset_id, a.nama_sebutan) for a in all_aset]
    
    # Isi pilihan untuk field penyewa_id
    form.penyewa_id.choices = [(p.penyewa_id, p.nama_lengkap) for p in all_penyewa]
    
    # =================================================================
    if form.validate_on_submit():
        
        # PINDAHKAN SEMUA LOGIKA API DAN PERHITUNGAN KE DALAM BLOK TRY BESAR
        try:
            # 1. Panggil API Pricing Service
            response = requests.get(f'{PRICING_SERVICE_URL}/api/v1/harga/boto/current')
            response.raise_for_status() 
            harga_data = response.json()
            harga_per_boto = Decimal(harga_data['harga_per_boto']) # Gunakan Decimal
            
            # 2. Ambil Data dan Hitung
            aset = AsetSawah.query.get(form.aset_id.data)
            luas_boto = aset.luas_boto
            durasi = form.durasi_bulan.data
            total_sewa = (luas_boto * harga_per_boto * Decimal(durasi)) # Perhitungan aman
            
            form_data = form.data.copy()
            form_data.pop('submit', None)
            form_data.pop('csrf_token', None)
            form_data['nilai_sewa'] = total_sewa
            
            # 3. Simpan ke DB
            db.session.add(TransaksiSewa(**form_data))
            db.session.commit()
            
            flash('Transaksi baru berhasil disimpan.', 'success')
            return redirect(url_for('list_transaksi')) # HANYA RETURN SUCCESS DI SINI

        except requests.exceptions.RequestException as e:
            flash(f'ERROR API: Gagal terhubung ke Layanan Harga.', 'danger')
        except (KeyError, ValueError, TypeError) as e:
            # Menangkap error konversi (Decimal) atau JSON
            flash(f'ERROR DATA: Gagal memproses data harga/perhitungan. ({e})', 'danger')
        except SQLAlchemyError as e:
            # Menangkap error DB
            db.session.rollback()
            flash(f'ERROR DB: Gagal menyimpan transaksi.', 'danger')
            
    # Jika POST gagal karena alasan apapun, atau jika GET request, render form
        return render_template('form_transaksi.html', form=form, title='Tambah Transaksi')
        
    # 2. Ambil Luas Boto Aset yang dipilih
        aset = AsetSawah.query.get(form.aset_id.data)
        luas_boto = aset.luas_boto
        
        # 3. Hitung Nilai Sewa
        durasi = form.durasi_bulan.data
        total_sewa = (luas_boto * harga_per_boto * Decimal(durasi))
        
        form_data = form.data.copy()
        form_data.pop('submit', None)
        form_data.pop('csrf_token', None)
        
        # 4. Tambahkan nilai_sewa yang sudah dihitung ke form_data
        form_data['nilai_sewa'] = total_sewa
        
        try:
            db.session.add(TransaksiSewa(**form_data))
            db.session.commit()
            # ... (Flash dan redirect tetap sama)
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal menyimpan transaksi: {e}', 'danger')
            
    # ... (Return render_template tetap sama) ...
    return render_template('form_transaksi.html', form=form, title='Tambah Transaksi')

# src/main.py (Tambahkan fungsi ini)

@app.route('/transaksi/delete/<int:sewa_id>', methods=['POST'])
def delete_transaksi(sewa_id):
    # Dapatkan objek transaksi, atau kembalikan 404 jika tidak ditemukan
    transaksi = TransaksiSewa.query.get_or_404(sewa_id)
    
    try:
        # Hapus objek dari database
        db.session.delete(transaksi)
        db.session.commit()
        flash(f'Transaksi ID {sewa_id} berhasil dihapus.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Gagal menghapus transaksi: {e}', 'danger')
        
    # Redirect kembali ke daftar transaksi
    return redirect(url_for('list_transaksi'))

# src/main.py (Tambahkan fungsi baru di bagian akhir routes)

@app.route('/pengaturan/harga', methods=['GET', 'POST'])
def pengaturan_harga():
    # Coba ambil harga yang ada (hanya row pertama)
    harga = HargaSewa.query.first()
    
    # Inisialisasi form, isi dengan data harga yang ada jika ditemukan
    form = HargaForm(obj=harga)

    if form.validate_on_submit():
        if harga:
            # Jika harga sudah ada, update nilainya
            harga.harga_per_boto = form.harga_per_boto.data
            flash('Harga sewa per boto berhasil diperbarui!', 'success')
        else:
            # Jika belum ada, buat row baru
            new_harga = HargaSewa(harga_per_boto=form.harga_per_boto.data)
            db.session.add(new_harga)
            flash('Harga sewa per boto berhasil disimpan!', 'success')
            
        db.session.commit()
        return redirect(url_for('pengaturan_harga'))

    return render_template('form_pengaturan_harga.html', form=form, title='Pengaturan Harga Sewa')

# ---------------------------------------------------
# 5. RUN APLIKASI
# ---------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)