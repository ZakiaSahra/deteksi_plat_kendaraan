from ultralytics import YOLO
import os

def train_yolo_model(data_yaml_path, epochs=50, imgsz=640, batch=16):
    """
    Melatih model YOLOv8 untuk mendeteksi plat nomor.
    :param data_yaml_path: path ke file data.yaml dari dataset
    """
    print(f"Mempersiapkan pelatihan YOLOv8 dengan dataset: {data_yaml_path}")
    
    # Inisialisasi model (menggunakan YOLOv8n sebagai baseline)
    model = YOLO('yolov8n.pt') 
    
    # Jalankan pelatihan
    results = model.train(
        data=data_yaml_path,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        project='runs/train',
        name='license_plate_detector',
        patience=5 # Menggunakan early stopping dengan patience 5
    )
    print("Pelatihan selesai!")
    return results

if __name__ == "__main__":
    # Ganti path di bawah sesuai dengan letak file data.yaml dari dataset yang diunduh
    base_dir = os.path.dirname(os.path.dirname(__file__))
    dataset_yaml = os.path.join(base_dir, "data", "Deteksi", "data.yaml")
    
    if not os.path.exists(dataset_yaml):
        print(f"Error: file konfigurasi {dataset_yaml} tidak ditemukan.")
        print("Pastikan struktur dataset Kaggle memiliki file YAML konfigurasi YOLO.")
    else:
        train_yolo_model(dataset_yaml, epochs=15) # Mengurangi epoch agar lebih cepat
