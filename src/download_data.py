import kagglehub
import shutil
import os

def download_dataset():
    print("Mengunduh dataset dari Kaggle...")
    # Unduh dataset menggunakan kagglehub
    path = kagglehub.dataset_download("hashimatulzaria/nomor-plat-kendaraan")
    print(f"Dataset berhasil diunduh ke cache Kaggle: {path}")

    # Tentukan direktori tujuan
    target_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    
    if os.path.exists(target_dir):
        print(f"Direktori {target_dir} sudah ada, menghapus yang lama...")
        shutil.rmtree(target_dir)
        
    print(f"Menyalin data ke direktori proyek: {target_dir}...")
    shutil.copytree(path, target_dir)
    print("Selesai! Data siap digunakan.")

if __name__ == "__main__":
    download_dataset()
