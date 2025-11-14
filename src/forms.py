from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField, SelectField, TextAreaField, DateField, IntegerField
from wtforms.validators import DataRequired, ValidationError, NumberRange, Length
import re

class AsetForm(FlaskForm):
    nama_sebutan = StringField('Nama Sebutan', validators=[DataRequired()])
    nomor_sertifikat = StringField('Nomor Sertifikat', validators=[DataRequired()])
    luas_m2 = DecimalField('Luas (m²)', validators=[DataRequired(), NumberRange(min=0)])
    luas_boto = DecimalField('Luas (boto)', validators=[DataRequired(), NumberRange(min=0)])
    lokasi = StringField('Lokasi (longitude,latitude)', validators=[DataRequired()])
    tanaman_saat_ini = StringField('Tanaman Saat Ini', validators=[DataRequired()])
    status_sewa = SelectField('Status Sewa', choices=[
        ('Disewa', 'Disewa'),
        ('Tidak Disewa', 'Tidak Disewa')
    ], validators=[DataRequired()])

    submit = SubmitField('Simpan')

    # 🔍 Custom validator untuk field lokasi
    def validate_lokasi(self, field):
        """
        Validasi format lokasi harus "lon,lat" dengan nilai numerik valid.
        Contoh valid: 112.062692,-7.73961
        """
        pattern = r'^\s*-?\d{1,3}\.\d+,\s*-?\d{1,2}\.\d+\s*$'
        if not re.match(pattern, field.data):
            raise ValidationError(
                "Format lokasi tidak valid. Gunakan format: 112.062692,-7.73961 (longitude,latitude)"
            )

        # Validasi rentang geografis dasar
        try:
            lon, lat = map(float, field.data.split(','))
            if not (-180 <= lon <= 180 and -90 <= lat <= 90):
                raise ValidationError("Koordinat di luar rentang valid bumi.")
        except ValueError:
            raise ValidationError("Koordinat harus berupa angka desimal valid.")

class PenyewaForm(FlaskForm):
    nama_lengkap = StringField('Nama Lengkap', validators=[DataRequired(), Length(max=255)])
    nik = StringField('NIK', validators=[DataRequired(), Length(max=20)])
    alamat = TextAreaField('Alamat')
    nomor_kontak = StringField('Nomor Kontak', validators=[Length(max=50)])
    submit = SubmitField('Simpan')

class TransaksiForm(FlaskForm):
    aset_id = SelectField('Aset', coerce=int, validators=[DataRequired()])
    penyewa_id = SelectField('Penyewa', coerce=int, validators=[DataRequired()])
    tanggal_mulai = DateField('Tanggal Mulai', validators=[DataRequired()])
    tanggal_akhir = DateField('Tanggal Akhir', validators=[DataRequired()])
    durasi_bulan = IntegerField('Durasi (bulan)', validators=[DataRequired(), NumberRange(min=1)])
    nilai_sewa = DecimalField('Nilai Sewa', validators=[DataRequired(), NumberRange(min=0)], places=2)
    jenis_tanaman_disepakati = StringField('Jenis Tanaman Disepakati', validators=[Length(max=100)])
    submit = SubmitField('Simpan')
