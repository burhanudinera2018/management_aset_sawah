-- Mengaktifkan ekstensi PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;

-- 1. Tabel ASET_SAWAH (Properti Lahan)
CREATE TABLE IF NOT EXISTS ASET_SAWAH (
    aset_id SERIAL PRIMARY KEY,
    nama_sebutan VARCHAR(255) NOT NULL,
    nomor_sertifikat VARCHAR(100) UNIQUE NOT NULL,
    luas_m2 NUMERIC(10, 2) NOT NULL,
    luas_boto NUMERIC(10, 2), -- Akan dihitung oleh Python
    -- PostGIS: Menggunakan tipe data GEOMETRY untuk menyimpan koordinat lokasi
    lokasi GEOMETRY(POINT, 4326) NOT NULL, 
    tanaman_saat_ini VARCHAR(100),
    status_sewa VARCHAR(50) NOT NULL DEFAULT 'Tersedia',
    tanggal_dibuat TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabel PENYEWA (Data Identitas Penyewa)
CREATE TABLE IF NOT EXISTS PENYEWA (
    penyewa_id SERIAL PRIMARY KEY,
    nama_lengkap VARCHAR(255) NOT NULL,
    nik VARCHAR(20) UNIQUE,
    alamat TEXT,
    nomor_kontak VARCHAR(50)
);

-- 3. Tabel TRANSAKSI_SEWA (Detail Sewa)
CREATE TABLE IF NOT EXISTS TRANSAKSI_SEWA (
    sewa_id SERIAL PRIMARY KEY,
    aset_id INTEGER REFERENCES ASET_SAWAH(aset_id) ON DELETE CASCADE,
    penyewa_id INTEGER REFERENCES PENYEWA(penyewa_id) ON DELETE CASCADE,
    tanggal_mulai DATE NOT NULL,
    tanggal_akhir DATE NOT NULL,
    durasi_bulan INTEGER NOT NULL,
    nilai_sewa NUMERIC(15, 2) NOT NULL,
    jenis_tanaman_disepakati VARCHAR(100),
    tanggal_transaksi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
