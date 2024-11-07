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

        const images = [data.image_url, data.landcover_image_url];
        let currentIndex = 0;

        const imageElement = document.getElementById('satellite-image');
        imageElement.src = images[currentIndex];

        document.getElementById('header').style.display = 'none';
        document.getElementById('coordinates-input').style.display = 'none';
        document.getElementById('satellite-image-section').style.display = 'flex';

        document.getElementById('next-button').addEventListener('click', () => {
            currentIndex = (currentIndex + 1) % images.length;
            imageElement.src = images[currentIndex];
        });

        document.getElementById('prev-button').addEventListener('click', () => {
            currentIndex = (currentIndex - 1 + images.length) % images.length;
            imageElement.src = images[currentIndex];
        });

    } catch (error) {
        console.error('Error:', error);
    }
});

