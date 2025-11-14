# src/converter.py
SATUAN_BOTO_KE_M2 = 14.0 # Sesuaikan berdasarkan area

def m2_to_boto(luas_m2):
    """Mengubah luasan dari meter persegi (m2) ke boto."""
    return luas_m2 / SATUAN_BOTO_KE_M2

def boto_to_m2(luas_boto):
    """Mengubah luasan dari boto ke meter persegi (m2)."""
    return luas_boto * SATUAN_BOTO_KE_M2
