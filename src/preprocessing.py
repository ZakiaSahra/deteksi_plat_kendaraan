# pyrefly: ignore [missing-import]
import cv2
import numpy as np

def deskew(image):
    """
    Melakukan koreksi rotasi (deskewing) pada gambar plat nomor.
    (Metode sederhana berbasis momen kontur)
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    # Thresholding untuk memisahkan teks
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Cari kontur dan bounding box
    coords = np.column_stack(np.where(thresh > 0))
    angle = cv2.minAreaRect(coords)[-1]
    
    # Koreksi sudut (OpenCV versi baru mengembalikan sudut dari 0-90)
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
        
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    
    return rotated

def apply_filters(image):
    """
    Menerapkan filtering untuk mengurangi noise.
    """
    # Menggunakan Bilateral Filter karena mempertahankan tepi dengan baik
    filtered = cv2.bilateralFilter(image, 11, 17, 17)
    return filtered

def morphology_operations(image):
    """
    Operasi morfologi (dilation & erosion) untuk mempertegas karakter.
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    # Dilation untuk mempertebal karakter yang mungkin terputus
    dilated = cv2.dilate(image, kernel, iterations=1)
    # Erosion untuk mengurangi noise kecil di sekitar karakter
    eroded = cv2.erode(dilated, kernel, iterations=1)
    return eroded

def enhance_contrast(image):
    """
    Meningkatkan kontras gambar.
    """
    # CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(image)
    return enhanced

def preprocess_plate(image):
    """
    Menjalankan seluruh pipeline preprocessing secara berurutan.
    Menggunakan kombinasi Bilateral Filter + Gamma Correction + Replicate Padding 
    untuk meniadakan efek glowing/halo pada plat neon variasi.
    """
    if image is None or image.size == 0:
        return None
        
    # 1. Bilateral Filter untuk meredam noise dan pendaran glow tanpa merusak tepi huruf
    bilateral = cv2.bilateralFilter(image, 9, 75, 75)
    
    # 2. Grayscale
    gray = cv2.cvtColor(bilateral, cv2.COLOR_BGR2GRAY) if len(bilateral.shape) == 3 else bilateral
    
    # 3. Gamma Correction (gamma = 2.0) untuk meningkatkan kontras mid-tone huruf neon
    gamma = 2.0
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    gamma_img = cv2.LUT(gray, table)
    
    # 4. Resize: Perbesar 3x menggunakan Cubic interpolation
    height, width = gamma_img.shape[:2]
    resized = cv2.resize(gamma_img, (width * 3, height * 3), interpolation=cv2.INTER_CUBIC)
    
    # 5. Constant Padding (20px) hitam agar EasyOCR memiliki margin batas yang jelas dan huruf depan tidak melekat ke tepi
    padded = cv2.copyMakeBorder(resized, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=0)
    
    return padded
