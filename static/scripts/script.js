document.getElementById('coordinate-form').addEventListener('submit', async function (event) {
    event.preventDefault();

    const topLeftLatitude = document.getElementById('top-left-latitude').value;
    const topLeftLongitude = document.getElementById('top-left-longitude').value;
    const bottomRightLatitude = document.getElementById('bottom-right-latitude').value;
    const bottomRightLongitude = document.getElementById('bottom-right-longitude').value;

    const coordinatesData = {
        top_left_latitude: topLeftLatitude,
        top_left_longitude: topLeftLongitude,
        bottom_right_latitude: bottomRightLatitude,
        bottom_right_longitude: bottomRightLongitude
    };

    try {
        const response = await fetch('/submit_coordinates', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(coordinatesData)
        });

        if (!response.ok) throw new Error('Network response was not ok');

        const data = await response.json();

        document.getElementById('coordinates-display').innerHTML = `
            <h3>Coordinates:</h3>
            <p>Top-Left: (${data.top_left_latitude}, ${data.top_left_longitude})</p>
            <p>Bottom-Right: (${data.bottom_right_latitude}, ${data.bottom_right_longitude})</p>
        `;

        // Update the image source with the generated image URL
        const imageElement = document.getElementById('satellite-image');
        imageElement.src = data.image_url;

        document.getElementById('header').style.display = 'none';
        document.getElementById('coordinates-input').style.display = 'none';
        document.getElementById('satellite-image-section').style.display = 'flex';

    } catch (error) {
        console.error('Error:', error);
    }
});

