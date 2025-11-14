# src/export_kml.py
from lxml import etree
from shapely.wkt import loads # Untuk parsing format WKT dari PostGIS

def generate_kml(sawah_data):
    """Membuat file KML dari data sawah dan menyimpannya."""
    
    # Namespace KML
    kml_ns = "http://www.opengis.net/kml/2.2"
    
    # Elemen KML Dasar
    kml = etree.Element("kml", nsmap={None: kml_ns})
    document = etree.SubElement(kml, "Document")
    name = etree.SubElement(document, "name")
    name.text = "Data Aset Lahan Sawah"

    for data in sawah_data:
        # Parsing POINT WKT ke objek Shapely untuk mendapatkan koordinat
        point_obj = loads(data['wkt_point'])
        longitude = point_obj.x
        latitude = point_obj.y
        
        # Membuat Placemark (Marker) untuk setiap sawah
        placemark = etree.SubElement(document, "Placemark")
        
        # Nama
        name_kml = etree.SubElement(placemark, "name")
        name_kml.text = data['nama']
        
        # Deskripsi (Informasi Sewa dan Properti)
        description = etree.SubElement(placemark, "description")
        description.text = (
            f"Nomor Sertifikat: {data['sertifikat']}\n"
            f"Luas: {data['luas_m2']} m2\n"
            f"Status Sewa: {data['status_sewa']}\n"
            f"Jenis Tanaman: {data['tanaman_sewa']}\n"
            f"Sewa Berakhir: {data['sewa_akhir']}"
        )
        
        # Geometri: Point
        point_kml = etree.SubElement(placemark, "Point")
        coordinates = etree.SubElement(point_kml, "coordinates")
        # Format KML: Longitude, Latitude, Ketinggian (0 untuk 2D)
        coordinates.text = f"{longitude},{latitude},0"

    # Membuat pohon XML menjadi string yang terstruktur
    tree = etree.ElementTree(kml)
    kml_string = etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding='UTF-8')
    
    # Menyimpan ke file
    file_path = "output_sawah_aset.kml"
    with open(file_path, "wb") as f:
        f.write(kml_string)
        
    return file_path

# --- Contoh Penggunaan di main.py ---
# from src.export_kml import generate_kml
# if __name__ == "__main__":
#     # ... (code record data) ...
#     
#     # Ekspor ke KML
#     sawah_data_to_export = get_sawah_data_for_export()
#     kml_file = generate_kml(sawah_data_to_export)
#     print(f"✅ Data berhasil diekspor ke {kml_file}. Buka file ini di Google Earth.")
