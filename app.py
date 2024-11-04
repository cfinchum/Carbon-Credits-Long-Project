
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

    # Define the area as a bounding box around the coordinates
    region = ee.Geometry.Rectangle([lon1, lat1, lon2, lat2])

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
    stats = classified.reduceRegion(
        reducer=ee.Reducer.frequencyHistogram(),
        geometry=region,
        scale=10,
        maxPixels=1e9
    ).getInfo()

    # Extract class areas as percentages
    vegetation_area = stats.get(0, 0) / sum(stats.values()) * 100
    water_area = stats.get(1, 0) / sum(stats.values()) * 100

    return jsonify({
        'vegetation_percentage': vegetation_area,
        'water_percentage': water_area
    })

if __name__ == '__main__':
    app.run(debug=True)