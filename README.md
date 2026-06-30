---
title: Deteksi Plat Kendaraan
emoji: 🚗
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# Deteksi Plat Kendaraan

Aplikasi deteksi plat kendaraan menggunakan YOLOv8, OpenCV, dan EasyOCR.

# Sistem Deteksi dan Pengenalan Plat Nomor Kendaraan Menggunakan Metode YOLO dan OCR

Proyek ini bertujuan untuk mendeteksi plat nomor kendaraan, mengenali karakter menggunakan OCR, dan mengklasifikasikan apakah plat nomor tersebut mengikuti standar Indonesia atau merupakan variasi.

## Struktur Proyek
- `data/` : Folder untuk dataset gambar/video plat nomor.
- `models/` : Folder untuk menyimpan model YOLO dan OCR yang telah dilatih/diunduh.
- `src/` : Folder utama untuk source code (deteksi, pengenalan, klasifikasi).
- `notebooks/` : Folder untuk eksperimen Jupyter Notebook.
