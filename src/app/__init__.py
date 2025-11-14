from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # contoh
db = SQLAlchemy(app)

from src.routes import aset_routes, penyewa_routes, transaksi_routes

