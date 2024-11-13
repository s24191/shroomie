const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const capturedImageInput = document.getElementById('captured-image');
const captureForm = document.getElementById('capture-form');
const resultModal = document.getElementById('resultModal');
const resultContent = document.getElementById('resultContent');
let flashEnabled = false;

// Access the device camera and stream to video element
navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(err => {
        console.error("Error accessing the camera: ", err);
    });

// Capture image from video stream
function captureImage() {
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL('image/jpeg');
    capturedImageInput.value = dataUrl;
    captureForm.submit();
}

// Toggle flash
function toggleFlash() {
    flashEnabled = !flashEnabled;
    // Implement flash toggle logic here
    console.log("Flash toggled: ", flashEnabled);
}

// Upload image and display result
function uploadImage(input) {
    const formData = new FormData(document.getElementById('upload-form'));
    fetch(predictUrl, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        displayResult(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Display result in modal
function displayResult(data) {
    if (data.error) {
        resultContent.innerHTML = `<div class="alert alert-danger"><strong>Error:</strong> ${data.error}</div>`;
    } else {
        const edibilityClass = data.edibility.toLowerCase() === 'edible' ? 'edible' : 'poisonous';
        resultContent.innerHTML = `
            <div class="result-name">${data.name}</div>
            ${data.image ? `<img src="data:image/jpeg;base64,${data.image}" class="mushroom-image" alt="Mushroom Image">` : '<p>No image available</p>'}
            <div class="edibility ${edibilityClass}">${data.edibility.toUpperCase()}</div>
            <div class="description">${data.description}</div>
            <div class="regions"><strong>Regions:</strong><br>${data.regions}</div>
        `;
    }
    resultModal.style.display = "block";
}

// Open Settings modal
function openSettings() {
    document.getElementById('settingsModal').style.display = 'block';
}

// Close Settings modal
function closeSettings() {
    document.getElementById('settingsModal').style.display = 'none';
}

// Close modal when clicking outside of it
window.onclick = function(event) {
    if (event.target == resultModal) {
        resultModal.style.display = 'none';
    } else if (event.target == settingsModal) {
        settingsModal.style.display = 'none';
    }
};

// Close modal
function closeModal() {
    resultModal.style.display = "none";
}

// Close modal when clicking outside of it
window.onclick = function(event) {
    if (event.target == resultModal) {
        resultModal.style.display = "none";
    }
};