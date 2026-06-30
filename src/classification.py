import re

def check_plate_standard(plate_text):
    """
    Mengecek apakah teks plat nomor sesuai dengan standar Indonesia.
    Standar umum: 1-2 Huruf (Wilayah), 1-4 Angka, 0-3 Huruf (Seri Belakang).
    Contoh: H 2830 FK -> H2830FK
    """
    # Bersihkan spasi dari hasil teks jika ada
    clean_text = plate_text.replace(" ", "").upper()
    
    # Regex:
    # ^[A-Z]{1,2} : Diawali 1 atau 2 huruf kapital
    # \d{1,4}     : Diikuti 1 hingga 4 angka
    # [A-Z]{0,3}$ : Diakhiri 0 hingga 3 huruf kapital
    pattern = r"^[A-Z]{1,2}\d{1,4}[A-Z]{0,3}$"
    
    if re.match(pattern, clean_text):
        return "Plat Standar"
    else:
        return "Plat Variasi"
