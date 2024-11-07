from flask import Flask, request, jsonify, render_template
import ee

app = Flask(__name__)

# Initialize Earth Engine
try:
    ee.Initialize(project='vital-invention-439317-b6')
except ee.EEException as e:
    print("Google Earth Engine initialization error:", e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_coordinates', methods=['POST'])
def submit_coordinates():
    data = request.get_json()

    try:
        # Extract coordinates from user input
        top_left_lat = float(data['top_left_latitude'])
        top_left_lon = float(data['top_left_longitude'])
        bottom_right_lat = float(data['bottom_right_latitude'])
        bottom_right_lon = float(data['bottom_right_longitude'])

        # Determine the correct top, bottom, left, right coordinates
        top_lat = max(top_left_lat, bottom_right_lat)
        bottom_lat = min(top_left_lat, bottom_right_lat)
        left_lon = min(top_left_lon, bottom_right_lon)
        right_lon = max(top_left_lon, bottom_right_lon)

        print(f"Coordinates for rectangle: top_lat={top_lat}, bottom_lat={bottom_lat}, left_lon={left_lon}, right_lon={right_lon}")

        # Create the Rectangle geometry
        rectangle = ee.Geometry.Rectangle([left_lon, bottom_lat, right_lon, top_lat])
        print("Rectangle created successfully.")

        # Fetch and process the satellite image using GEE
        s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30)) \
            .filter(ee.Filter.date('2020-01-01', '2020-12-31')) \
            .filterBounds(rectangle)

        print("Filtered ImageCollection created.")

        # Take a median composite of the image
        composite = s2.median()

        # Visualization parameters for the true color image
        true_color_vis = {
            'bands': ['B4', 'B3', 'B2'],
            'min': 0,
            'max': 3000
        }

        # Generate the URL for the true color image
        true_color_url = composite.clip(rectangle).getThumbURL({
            'region': rectangle,
            'dimensions': 500,
            **true_color_vis
        })
        print(f"True color image URL generated: {true_color_url}")

        # --- Land Cover Classification using ESA WorldCover ---

        # Import the ESA WorldCover dataset
        worldcover = ee.Image('ESA/WorldCover/v100/2020').select('Map')

        # Define your classes based on WorldCover legends
        # 0: Urban (Class 50)
        # 1: Bare Land (Class 40)
        # 2: Water (Class 80)
        # 3: Vegetation (Classes 10, 20, 30, 60, 70, 90, 100)

        # Create masks for each class
        urban_mask = worldcover.eq(50)
        bare_mask = worldcover.eq(40)
        water_mask = worldcover.eq(80)
        vegetation_mask = worldcover.remap(
            [10, 20, 30, 60, 70, 90, 100],
            [1, 1, 1, 1, 1, 1, 1]
        )

        # Sample points for each class
        urban_points = urban_mask.selfMask().sample(
            region=rectangle, scale=10, numPixels=500, seed=0, geometries=True
        ).map(lambda f: f.set('landcover', 0))

        bare_points = bare_mask.selfMask().sample(
            region=rectangle, scale=10, numPixels=500, seed=1, geometries=True
        ).map(lambda f: f.set('landcover', 1))

        water_points = water_mask.selfMask().sample(
            region=rectangle, scale=10, numPixels=500, seed=2, geometries=True
        ).map(lambda f: f.set('landcover', 2))

        vegetation_points = vegetation_mask.selfMask().sample(
            region=rectangle, scale=10, numPixels=500, seed=3, geometries=True
        ).map(lambda f: f.set('landcover', 3))

        # Merge all samples into one FeatureCollection
        training_samples = urban_points.merge(bare_points).merge(water_points).merge(vegetation_points)

        print("Training samples collected.")

        # Sample the composite image at the locations of the training samples
        training = composite.sampleRegions(
            collection=training_samples,
            properties=['landcover'],
            scale=10
        )

        # Train a Random Forest classifier
        classifier = ee.Classifier.smileRandomForest(50).train(
            features=training,
            classProperty='landcover',
            inputProperties=composite.bandNames()
        )

        # Classify the composite image
        classified = composite.classify(classifier)

        # Define a color palette for visualization
        palette = ['#cc6d8f', '#ffc107', '#1e88e5', '#004d40']

        # Visualization parameters for the classified image
        classified_vis = {
            'min': 0,
            'max': 3,
            'palette': palette
        }

        # Generate the URL for the classified image
        classified_image_url = classified.clip(rectangle).getThumbURL({
            'region': rectangle,
            'dimensions': 500,
            **classified_vis
        })
        print(f"Classified image URL generated: {classified_image_url}")

        # Calculate area statistics
        # First, reproject the classified image to a fixed scale
        classified_proj = classified.clip(rectangle).reproject('EPSG:3857', None, 30)

        # Calculate pixel area in square meters
        pixel_area = ee.Image.pixelArea()

        # Calculate the area for each class
        class_areas = pixel_area.addBands(classified_proj).reduceRegion(
            reducer=ee.Reducer.sum().group(
                groupField=1,
                groupName='landcover'
            ),
            geometry=rectangle,
            scale=30,
            maxPixels=1e9
        )

        # Extract the area results
        group_dict = class_areas.get('groups').getInfo()

        # Map land cover class IDs to area in hectares
        area_stats = {}
        for group in group_dict:
            class_id = int(group['landcover'])
            area_m2 = group['sum']
            area_ha = area_m2 / 10000  # Convert square meters to hectares
            area_stats[class_id] = area_ha

        print(f"Area statistics: {area_stats}")

        # Return the data to the frontend
        return jsonify({
            'true_color_url': true_color_url,
            'classified_image_url': classified_image_url,
            'area_stats': area_stats,
            'top_left_latitude': top_lat,
            'top_left_longitude': left_lon,
            'bottom_right_latitude': bottom_lat,
            'bottom_right_longitude': right_lon
        })

    except Exception as e:
        print("Error processing coordinates:", e)
        return jsonify({'error': 'An error occurred while processing the coordinates.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
