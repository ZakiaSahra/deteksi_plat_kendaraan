import easyocr
import re
import cv2
import numpy as np

# Inisialisasi reader OCR (hanya dilakukan sekali agar tidak lambat)
# Menggunakan model bahasa Inggris karena plat nomor terdiri dari A-Z dan 0-9
reader = easyocr.Reader(['en'], gpu=False)

def _run_ocr_on(image):
    """Jalankan OCR pada satu gambar dan kembalikan teks yang terbaca."""
    results = reader.readtext(image, 
                              allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
                              min_size=3,
                              text_threshold=0.2, # Diturunkan agar huruf yang agak blur tetap masuk
                              contrast_ths=0.1,
                              adjust_contrast=0.7,
                              width_ths=0.7, # Jarak spasi antar huruf diperlebar sedikit
                              mag_ratio=1.5) # Gambar diperbesar sedikit secara internal oleh EasyOCR
    sorted_results = sorted(results, key=lambda r: r[0][0][0])
    return ''.join([text for (_, text, _) in sorted_results]).replace(" ", "").upper()

def extract_text(image):
    """
    Ekstraksi teks dari gambar plat nomor menggunakan EasyOCR.
    Mencoba dua versi gambar (normal & inverted) dan mengambil hasil terpanjang
    agar bisa membaca plat gelap (teks terang) maupun plat terang (teks gelap).
    """
    if image is None:
        return ""
    
    # Versi 1: Gambar normal
    text_normal = _run_ocr_on(image)
    
    # Versi 2: Gambar dibalik warnanya (untuk plat variasi gelap dengan teks terang)
    inverted = cv2.bitwise_not(image)
    text_inverted = _run_ocr_on(inverted)
    
    # Pilih hasil yang lebih lengkap (lebih banyak karakter)
    if len(text_inverted) > len(text_normal):
        return text_inverted
    return text_normal

from src.classification import check_plate_standard

def classify_plate(text):
    """
    Mengklasifikasikan apakah plat nomor termasuk standar Indonesia atau variasi.
    """
    cleaned_text = re.sub(r'[^A-Z0-9]', '', text)
    status = check_plate_standard(cleaned_text)
    return status, cleaned_text

def run_ocr_pipeline(preprocessed_image):
    """
    Menjalankan proses ekstraksi teks dan klasifikasi.
    """
    text = extract_text(preprocessed_image)
    if not text:
        return "Tidak Terdeteksi", "Tidak Terdeteksi"
        
    status, formatted_text = classify_plate(text)
    return status, formatted_text
