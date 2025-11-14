from flask import Blueprint, render_template, redirect, url_for, flash
from models.aset_model import db, TransaksiSewa, AsetSawah, Penyewa
from src.forms import TransaksiForm

transaksi_bp = Blueprint('transaksi', __name__, url_prefix='/transaksi')

@transaksi_bp.route('/list')
def list_transaksi():
    data = TransaksiSewa.query.order_by(TransaksiSewa.sewa_id.desc()).all()
    return render_template('list_transaksi.html', data=data)

@transaksi_bp.route('/tambah', methods=['GET', 'POST'])
def tambah_transaksi():
    form = TransaksiForm()
    form.aset_id.choices = [(a.aset_id, a.nama_sebutan) for a in AsetSawah.query.order_by(AsetSawah.aset_id).all()]
    form.penyewa_id.choices = [(p.penyewa_id, p.nama_lengkap) for p in Penyewa.query.order_by(Penyewa.penyewa_id).all()]

    if form.validate_on_submit():
        tr = TransaksiSewa(
            aset_id=form.aset_id.data,
            penyewa_id=form.penyewa_id.data,
            tanggal_mulai=form.tanggal_mulai.data,
            tanggal_akhir=form.tanggal_akhir.data,
            durasi_bulan=form.durasi_bulan.data,
            nilai_sewa=form.nilai_sewa.data,
            jenis_tanaman_disepakati=form.jenis_tanaman_disepakati.data
        )
        aset = AsetSawah.query.get(form.aset_id.data)
        if aset:
            aset.status_sewa = 'Disewa'
        db.session.add(tr)
        db.session.commit()
        flash('Transaksi berhasil dibuat', 'success')
        return redirect(url_for('list_transaksi'))
    return render_template('form_transaksi.html', form=form)
