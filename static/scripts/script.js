document.getElementById('coordinate-form').addEventListener('submit', async function (event) {
    event.preventDefault();

    const topLeftLatitude = document.getElementById('top-left-latitude').value;
    const topLeftLongitude = document.getElementById('top-left-longitude').value;
    const bottomRightLatitude = document.getElementById('bottom-right-latitude').value;
    const bottomRightLongitude = document.getElementById('bottom-right-longitude').value;

    // Prepare the data to be sent to the backend
    const coordinatesData = {
        top_left_latitude: topLeftLatitude,
        top_left_longitude: topLeftLongitude,
        bottom_right_latitude: bottomRightLatitude,
        bottom_right_longitude: bottomRightLongitude
    };

    try {
        // Send the coordinates to the Flask backend
        const response = await fetch('/submit_coordinates', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(coordinatesData)
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();

        // Display coordinates above the satellite image
        const coordinatesDisplay = document.getElementById('coordinates-display');
        coordinatesDisplay.innerHTML = `
            <h3>Coordinates:</h3>
            <p>Top-Left: (${data.top_left_latitude}, ${data.top_left_longitude})</p>
            <p>Bottom-Right: (${data.bottom_right_latitude}, ${data.bottom_right_longitude})</p>
        `;

        // Hide the input and show the image section
        document.getElementById('header').style.display = 'none';
        document.getElementById('coordinates-input').style.display = 'none';
        document.getElementById('satellite-image-section').style.display = 'flex';
    } catch (error) {
        console.error('Error:', error);
    }
});

