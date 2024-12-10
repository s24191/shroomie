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
if (video) {
    navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
        .then(stream => {
            if (!video.srcObject) {
                video.srcObject = stream; // Set the stream if not already set
            }
            return video.play();
        })
        .catch(err => {
            console.error("Error accessing the camera: ", err);
        });
} else {
    console.warn("Video element not found. Camera functionality will not be available.");
}


// Fetch user's GPS location
function fetchLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            position => {
                const { latitude, longitude } = position.coords;
                // Populate hidden fields for both forms
                latitudeUploadInput.value = latitude;
                longitudeUploadInput.value = longitude;
                console.log(`Location fetched: ${latitude}, ${longitude}`);
            },
            error => {
                console.warn(`Geolocation error (${error.code}): ${error.message}`);
                // Set to null if geolocation is not available
                latitudeUploadInput.value = '';
                longitudeUploadInput.value = '';
            }
        );
    } else {
        alert("Geolocation is not supported by your browser.");
        latitudeUploadInput.value = '';
        longitudeUploadInput.value = '';
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
    capturedImageInput.value = canvas.toDataURL('image/jpeg');

    // Include latitude and longitude in the form data
    const latitude = latitudeCaptureInput.value;
    const longitude = longitudeCaptureInput.value;
    const formData = new FormData(captureForm);
    formData.append('latitude', latitude);
    formData.append('longitude', longitude);

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


function uploadImage(input) {
    const formData = new FormData(document.getElementById('upload-form'));

    // Validate and append file from the input parameter
    if (input.files.length > 0) {
        formData.append('file', input.files[0]);
    } else {
        console.error('No file selected.');
        return;
    }

    // Ensure latitude and longitude inputs are not null
    if (latitudeUploadInput && longitudeUploadInput) {
        const latitude = latitudeUploadInput.value;
        const longitude = longitudeUploadInput.value;
        formData.append('latitude', latitude);
        formData.append('longitude', longitude);
    } else {
        console.error('Latitude or Longitude input is missing.');
    }

    // Make the POST request
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

// Toggle flash
function toggleFlash() {
    flashEnabled = !flashEnabled;
    //TODO: Implement flash toggle logic here
    console.log("Flash toggled: ", flashEnabled);
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
    fetch('/user_info')
        .then(response => response.json())
        .then(data => {
            if (data.login) {
                document.getElementById('user-login').textContent = data.login;
            } else {
                document.getElementById('user-login').textContent = 'Error fetching user login';
            }
        })
        .catch(error => {
            console.error('Error fetching user info:', error);
            document.getElementById('user-login').textContent = 'Error fetching user login';
        });

    document.getElementById('settingsModal').style.display = 'block';
}

// Close Settings modal
function closeSettings() {
    document.getElementById('settingsModal').style.display = 'none';
}

// Close modal when clicking outside of it
window.onclick = function(event) {
    if (event.target === resultModal) {
        resultModal.style.display = 'none';
    } else if (event.target === settingsModal) {
        settingsModal.style.display = 'none';
    }
};

// Close modal
function closeModal() {
    resultModal.style.display = "none";
}

// Close modal when clicking outside of it
window.onclick = function(event) {
    if (event.target === resultModal) {
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

let map; // Declare a global variable to hold the map instance

function displayHistory(history) {
    const historyContent = document.getElementById('historyContent');
    historyContent.innerHTML = '';

    if (history.length === 0) {
        historyContent.innerHTML = '<p>No history available.</p>';
        return;
    }

    // Check if the map is already initialized
    if (map) {
        map.remove(); // Remove the existing map instance
    }

    // Initialize the map
    map = L.map('map').setView([0, 0], 2); // Centered at (0, 0) with zoom level 2
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
