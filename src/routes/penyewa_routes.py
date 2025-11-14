from flask import Blueprint, render_template, redirect, url_for, flash
from models.aset_model import db, Penyewa
from src.forms import PenyewaForm

penyewa_bp = Blueprint('penyewa', __name__, url_prefix='/penyewa')

@penyewa_bp.route('/list')
def list_penyewa():
    data = Penyewa.query.order_by(Penyewa.penyewa_id.desc()).all()
    return render_template('list_penyewa.html', data=data)

@penyewa_bp.route('/tambah', methods=['GET', 'POST'])
def tambah_penyewa():
    form = PenyewaForm()
    if form.validate_on_submit():
        p = Penyewa(
            nama_lengkap=form.nama_lengkap.data,
            nik=form.nik.data,
            alamat=form.alamat.data,
            nomor_kontak=form.nomor_kontak.data
        )
        db.session.add(p)
        db.session.commit()
        flash('Penyewa berhasil ditambahkan', 'success')
        return redirect(url_for('list_penyewa'))
    return render_template('form_penyewa.html', form=form)
