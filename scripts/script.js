document.getElementById('coordinate-form').addEventListener('submit', function (event) {
    event.preventDefault();

    document.getElementById('header').style.display = 'none';
    document.getElementById('coordinates-input').style.display = 'none';

    document.getElementById('satellite-image-section').style.display = 'flex';
});
