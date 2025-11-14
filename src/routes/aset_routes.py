from flask import Blueprint, render_template, redirect, url_for, flash
from models.aset_model import db, AsetSawah
from src.forms import AsetForm

aset_bp = Blueprint('aset', __name__, url_prefix='/aset')

@aset_bp.route('/list')
def list_aset():
    data = AsetSawah.query.order_by(AsetSawah.aset_id.desc()).all()
    return render_template('list_aset.html', data=data)

@aset_bp.route('/tambah', methods=['GET', 'POST'])
def tambah_aset():
    form = AsetForm()
    if form.validate_on_submit():
        aset = AsetSawah(
            nama_sebutan=form.nama_sebutan.data,
            nomor_sertifikat=form.nomor_sertifikat.data,
            luas_m2=form.luas_m2.data,
            luas_boto=form.luas_boto.data,
            lokasi=form.lokasi.data,
            tanaman_saat_ini=form.tanaman_saat_ini.data,
            status_sewa=form.status_sewa.data
        )
        db.session.add(aset)
        db.session.commit()
        flash('Aset berhasil ditambahkan', 'success')
        return redirect(url_for('list_aset'))
    return render_template('form_aset.html', form=form)

@aset_bp.route('/edit/<int:aset_id>', methods=['GET', 'POST'])
def edit_aset(aset_id):
    aset = AsetSawah.query.get_or_404(aset_id)
    form = AsetForm(obj=aset)
    if form.validate_on_submit():
        form.populate_obj(aset)
        db.session.commit()
        flash('Aset berhasil diperbarui', 'info')
        return redirect(url_for('list_aset'))
    return render_template('form_aset.html', form=form, aset=aset)
