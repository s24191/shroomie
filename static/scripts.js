const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const capturedImageInput = document.getElementById('captured-image');
const captureForm = document.getElementById('capture-form');
const resultModal = document.getElementById('resultModal');
const resultContent = document.getElementById('resultContent');
const latitudeUploadInput = document.getElementById('latitude-upload');
const longitudeUploadInput = document.getElementById('longitude-upload');
const latitudeCaptureInput = document.getElementById('latitude-capture');
const longitudeCaptureInput = document.getElementById('longitude-capture');
let flashEnabled = false;

// Access the device camera and stream to video element
navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
    .then(stream => {
        const video = document.getElementById('video');
        if (video.srcObject !== stream) {
            video.srcObject = stream; // Set the stream only if it's not already set
        }
        return video.play(); // Return the play promise
    })
    .catch(err => {
        console.error("Error accessing the camera: ", err);
    });


// Fetch user's GPS location
function fetchLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            position => {
                const { latitude, longitude } = position.coords;
                // Populate hidden fields for both forms
                latitudeUploadInput.value = latitude;
                longitudeUploadInput.value = longitude;
                latitudeCaptureInput.value = latitude;
                longitudeCaptureInput.value = longitude;
                console.log(`Location fetched: ${latitude}, ${longitude}`);
            },
            error => {
                console.warn("Geolocation not available. Setting coordinates to null.");
                // Set to null if geolocation is not available
                latitudeUploadInput.value = null;
                longitudeUploadInput.value = null;
                latitudeCaptureInput.value = null;
                longitudeCaptureInput.value = null;
            }
        );
    } else {
        alert("Geolocation is not supported by your browser.");
        latitudeUploadInput.value = null;
        longitudeUploadInput.value = null;
        latitudeCaptureInput.value = null;
        longitudeCaptureInput.value = null;
    }
}
// Call fetchLocation on page load to populate GPS fields
window.onload = fetchLocation;

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

function openHistory() {
    fetchHistory();
    document.getElementById('historyModal').style.display = 'block';
}

function closeHistory() {
    document.getElementById('historyModal').style.display = 'none';
}

function fetchHistory() {
    fetch('/history')
        .then(response => response.json())
        .then(data => {
            displayHistory(data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function displayHistory(history) {
    const historyContent = document.getElementById('historyContent');
    historyContent.innerHTML = '';

    if (history.length === 0) {
        historyContent.innerHTML = '<p>No history available.</p>';
        return;
    }

    // Initialize the map
    const map = L.map('map').setView([0, 0], 2); // Centered at (0, 0) with zoom level 2
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    history.forEach(entry => {
        const entryDiv = document.createElement('div');
        entryDiv.classList.add('history-entry');

        const image = document.createElement('img');
        image.src = `data:image/jpeg;base64,${entry.user_image}`;
        image.classList.add('history-image');

        const details = document.createElement('div');
        details.classList.add('history-details');
        details.innerHTML = `
            <p><strong>Mushroom:</strong> ${entry.mushroom_name}</p>
            <p><strong>Date:</strong> ${entry.date}</p>
        `;

        entryDiv.appendChild(image);
        entryDiv.appendChild(details);
        historyContent.appendChild(entryDiv);

        // Add marker to the map
        if (entry.latitude && entry.longitude) {
            L.marker([entry.latitude, entry.longitude])
                .addTo(map)
                .bindPopup(`<strong>${entry.mushroom_name}</strong><br>${entry.date}`)
                .openPopup();
        }
    });
}