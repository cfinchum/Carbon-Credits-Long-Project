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

        if (data.error) {
            alert(data.error);
            return;
        }

        document.getElementById('coordinates-display').innerHTML = `
            <h3>Coordinates:</h3>
            <p>Top-Left: (${data.top_left_latitude.toFixed(6)}, ${data.top_left_longitude.toFixed(6)})</p>
            <p>Bottom-Right: (${data.bottom_right_latitude.toFixed(6)}, ${data.bottom_right_longitude.toFixed(6)})</p>
        `;

        const images = [data.image_url, data.landcover_image_url];
        let currentIndex = 0;

        const imageElement = document.getElementById('satellite-image');
        imageElement.src = images[currentIndex];

        // Generate Legend
        const legendContainer = document.getElementById('legend-items');
        legendContainer.innerHTML = ''; // Clear any existing legend

        // Sort the classes by key to maintain order
        const sortedClasses = Object.keys(data.landcover_classes).sort((a, b) => a - b);

        sortedClasses.forEach(key => {
            const classInfo = data.landcover_classes[key];
            const legendItem = document.createElement('div');
            legendItem.classList.add('legend-item');

            const colorBox = document.createElement('span');
            colorBox.classList.add('legend-color');
            colorBox.style.backgroundColor = classInfo.color;

            const label = document.createElement('span');
            label.classList.add('legend-label');
            label.textContent = classInfo.name;

            legendItem.appendChild(colorBox);
            legendItem.appendChild(label);
            legendContainer.appendChild(legendItem);
        });

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
        alert('An error occurred while processing your request.');
    }
});
