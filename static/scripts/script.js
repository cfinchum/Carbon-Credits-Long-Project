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

        // Display the coordinates
        document.getElementById('coordinates-display').innerHTML = `
            <h3>Coordinates:</h3>
            <p>Top-Left: (${data.top_left_latitude}, ${data.top_left_longitude})</p>
            <p>Bottom-Right: (${data.bottom_right_latitude}, ${data.bottom_right_longitude})</p>
        `;

        // Update the image sources with the generated image URLs
        document.getElementById('satellite-image').src = data.true_color_url;
        document.getElementById('classified-image').src = data.classified_image_url;

        // Display area statistics
        const areaStats = data.area_stats;

        // Map class IDs to land cover names
        const classNames = {
            0: 'Urban',
            1: 'Bare Land',
            2: 'Water',
            3: 'Vegetation'
        };

        let statsHtml = '<h3>Area Statistics (in hectares):</h3><ul>';
        for (const [classId, area] of Object.entries(areaStats)) {
            const className = classNames[classId] || `Class ${classId}`;
            statsHtml += `<li><strong>${className}:</strong> ${area.toFixed(2)} ha</li>`;
        }
        statsHtml += '</ul>';
        document.getElementById('area-stats').innerHTML = statsHtml;

        // Hide the input section and display the results section
        document.getElementById('header').style.display = 'none';
        document.getElementById('coordinates-input').style.display = 'none';
        document.getElementById('results-section').style.display = 'flex';

    } catch (error) {
        console.error('Error:', error);
    }
});
