document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadContent = document.querySelector('.upload-content');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
    const btnClear = document.getElementById('btn-clear');
    const btnScan = document.getElementById('btn-scan');
    const spinner = document.getElementById('spinner');
    const resultsSection = document.getElementById('results-section');
    const resultsGrid = document.getElementById('results-grid');

    let currentFile = null;

    // Drag and Drop Events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    dropZone.addEventListener('drop', handleDrop, false);
    fileInput.addEventListener('change', handleFileSelect, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const file = dt.files[0];
        handleFile(file);
    }

    function handleFileSelect(e) {
        const file = e.target.files[0];
        handleFile(file);
    }

    function handleFile(file) {
        if (!file || !file.type.startsWith('image/')) {
            alert('Harap unggah file gambar yang valid.');
            return;
        }

        currentFile = file;
        const reader = new FileReader();

        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            uploadContent.classList.add('hidden');
            previewContainer.classList.remove('hidden');
            resultsSection.classList.add('hidden');
            resultsGrid.innerHTML = '';
        }

        reader.readAsDataURL(file);
    }

    btnClear.addEventListener('click', (e) => {
        e.stopPropagation(); // Mencegah klik menyebar ke upload section
        currentFile = null;
        fileInput.value = '';
        imagePreview.src = '';
        uploadContent.classList.remove('hidden');
        previewContainer.classList.add('hidden');
        resultsSection.classList.add('hidden');
    });

    btnScan.addEventListener('click', async () => {
        if (!currentFile) return;

        // UI State: Loading
        btnScan.disabled = true;
        spinner.classList.remove('hidden');
        btnScan.innerHTML = 'Menganalisis... <span class="spinner" id="spinner"></span>';
        resultsSection.classList.add('hidden');
        resultsGrid.innerHTML = '';

        const formData = new FormData();
        formData.append('image', currentFile);

        try {
            const response = await fetch('/detect', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Terjadi kesalahan pada server.');
            }

            displayResults(data);

        } catch (error) {
            alert('Error: ' + error.message);
        } finally {
            // UI State: Reset
            btnScan.disabled = false;
            btnScan.innerHTML = 'Mulai Deteksi <span class="spinner hidden" id="spinner"></span>';
        }
    });

    function displayResults(data) {
        if (!data.detections || data.detections.length === 0) {
            resultsGrid.innerHTML = '<p style="text-align: center; width: 100%; color: var(--text-muted);">Tidak ada plat nomor yang terdeteksi pada gambar ini.</p>';
            resultsSection.classList.remove('hidden');
            return;
        }

        data.detections.forEach(det => {
            const isStandard = det.status === 'Plat Standar';
            const badgeClass = isStandard ? 'status-standar' : 'status-variasi';

            const card = document.createElement('div');
            card.className = 'result-card';
            card.innerHTML = `
                <div class="result-images">
                    <img src="${det.plate_img}" alt="Plat Asli" title="Potongan Plat">
                    <img src="${det.prep_img}" alt="Preprocessed" title="Hasil Preprocessing OCR">
                </div>
                <div class="result-info">
                    <div class="plate-text">${det.text || '-'}</div>
                    <div class="${badgeClass} status-badge">${det.status}</div>
                </div>
            `;
            resultsGrid.appendChild(card);
        });

        resultsSection.classList.remove('hidden');
        
        // Scroll mulus ke hasil
        setTimeout(() => {
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }
});
