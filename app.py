<<<<<<< HEAD
from flask import Flask, render_template, request, jsonify, send_file
import ee

# Initialize Earth Engine
ee.Initialize(project='vital-invention-439317-b6')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('getimage.html')

@app.route('/classify', methods=['POST'])
def classify_area():
    data = request.get_json()
    lat1, lon1 = float(data['lat1']), float(data['lon1'])
    lat2, lon2 = float(data['lat2']), float(data['lon2'])
=======

from flask import Flask, request, jsonify
import ee

# Initialize Earth Engine
ee.Initialize()

app = Flask(__name__)

@app.route('/classify', methods=['POST'])
def classify_area():
    data = request.get_json()
    lat1, lon1 = data['lat1'], data['lon1']
    lat2, lon2 = data['lat2'], data['lon2']
>>>>>>> 38ae3dd0a7d39acf811b64f9960bd8817cf75be2

    # Define the area as a bounding box around the coordinates
    region = ee.Geometry.Rectangle([lon1, lat1, lon2, lat2])

<<<<<<< HEAD
    # Load satellite imagery and classify
    image = ee.ImageCollection("COPERNICUS/S2").filterBounds(region).filterDate('2022-01-01', '2022-12-31').median()

    # Sample vegetation and water as dummy training points
    vegetation = ee.Feature(region.centroid(), {'landcover': 0})
    water = ee.Feature(region.centroid().translate(0.01, 0.01), {'landcover': 1})
    training_data = ee.FeatureCollection([vegetation, water])

    # Train classifier and classify
    classifier = ee.Classifier.smileCart().train(features=training_data, classProperty='landcover', inputProperties=['B4', 'B3', 'B2'])
    classified = image.select(['B4', 'B3', 'B2']).classify(classifier).clip(region)

    # Calculate area for each class
=======
    # Load satellite imagery 
    image = ee.ImageCollection("COPERNICUS/S2") \
        .filterBounds(region) \
        .filterDate('2022-01-01', '2022-12-31') \
        .median()  # Use median to reduce cloud interference

    # Define training samples manually 
    vegetation = ee.Feature(region.centroid(), {'landcover': 0})  # Vegetation label
    water = ee.Feature(region.centroid().translate(0.01, 0.01), {'landcover': 1})  # Water label
    training_data = ee.FeatureCollection([vegetation, water])

    # Train a classifier
    classifier = ee.Classifier.smileCart().train(
        features=training_data,
        classProperty='landcover',
        inputProperties=['B4', 'B3', 'B2']
    )

    # Classify the region
    classified = image.select(['B4', 'B3', 'B2']).classify(classifier).clip(region)

    # Calculate area for each class within the region
>>>>>>> 38ae3dd0a7d39acf811b64f9960bd8817cf75be2
    stats = classified.reduceRegion(
        reducer=ee.Reducer.frequencyHistogram(),
        geometry=region,
        scale=10,
        maxPixels=1e9
    ).getInfo()

    # Extract class areas as percentages
<<<<<<< HEAD
    vegetation_area = stats.get(0, 0) / sum(stats.values()) * 100 if stats else 0
    water_area = stats.get(1, 0) / sum(stats.values()) * 100 if stats else 0
=======
    vegetation_area = stats.get(0, 0) / sum(stats.values()) * 100
    water_area = stats.get(1, 0) / sum(stats.values()) * 100
>>>>>>> 38ae3dd0a7d39acf811b64f9960bd8817cf75be2

    return jsonify({
        'vegetation_percentage': vegetation_area,
        'water_percentage': water_area
    })

if __name__ == '__main__':
<<<<<<< HEAD
    app.run(debug=True)
=======
    app.run(debug=True)
>>>>>>> 38ae3dd0a7d39acf811b64f9960bd8817cf75be2
