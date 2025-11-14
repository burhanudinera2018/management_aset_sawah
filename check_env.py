"""
check_env.py
--------------
Cek apakah environment proyek Flask + SQLAlchemy + PostGIS sudah lengkap.
"""

import importlib

# Daftar modul yang perlu dicek
modules = [
    "flask",
    "flask_wtf",
    "sqlalchemy",
    "geoalchemy2",
    "psycopg2",
    "wtforms",
]

print("🔍 Mengecek environment Python...\n")

for module_name in modules:
    try:
        mod = importlib.import_module(module_name)
        version = getattr(mod, "__version__", "Tidak diketahui")
        print(f"✅ {module_name:15} terinstal (versi: {version})")
    except ImportError:
        print(f"❌ {module_name:15} TIDAK ditemukan. Install dengan:")
        print(f"   pip install {module_name}\n")

print("\n🚀 Pemeriksaan selesai.")
print("Jika ada tanda ❌, jalankan perintah pip install yang ditampilkan di atas.")
