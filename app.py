from flask import Flask, request, jsonify, render_template
import ee

app = Flask(__name__)

# Set up Earth Engine authentication
try:
    ee.Initialize()
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

        # Determine top, bottom, left, and right coordinates so it works with GEE
        top_lat = max(top_left_lat, bottom_right_lat)
        bottom_lat = min(top_left_lat, bottom_right_lat)
        left_lon = min(top_left_lon, bottom_right_lon)
        right_lon = max(top_left_lon, bottom_right_lon)

        # Create the Rectangle geometry
        rectangle = ee.Geometry.Rectangle([left_lon, bottom_lat, right_lon, top_lat])

        # Fetch and process the satellite image using GEE 
        s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30)) \
            .filter(ee.Filter.date('2021-01-01', '2021-12-31')) \
            .filterBounds(rectangle)
        
        # Take a median composite of the image and visualize it
        composite = s2.median().visualize(bands=['B4', 'B3', 'B2'], min=0, max=3000)
        image_url = composite.getThumbURL({'region': rectangle, 'dimensions': 500})

        # Load and visualize the ESA WorldCover data
        landcover = ee.Image('ESA/WorldCover/v100/2020')
        landcoverVis = {
            'min': 10,
            'max': 90,
            'palette': [
                '006400', 'ffbb22', 'ffff4c', 'f096ff', 'fa0000', 
                'b4b4b4', 'f0f0f0', '0064c8', '0096a0', '00cf75', 'fae6a0'
            ]
        }
        landcover_image = landcover.clip(rectangle).visualize(**landcoverVis)
        landcover_image_url = landcover_image.getThumbURL({'region': rectangle, 'dimensions': 500})

        return jsonify({
            'image_url': image_url,
            'landcover_image_url': landcover_image_url,
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

