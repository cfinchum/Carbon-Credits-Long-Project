from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_coordinates', methods=['POST'])
def submit_coordinates():
    data = request.json
    top_left_latitude = data['top_left_latitude']
    top_left_longitude = data['top_left_longitude']
    bottom_right_latitude = data['bottom_right_latitude']
    bottom_right_longitude = data['bottom_right_longitude']

    return jsonify({
        'top_left_latitude': top_left_latitude,
        'top_left_longitude': top_left_longitude,
        'bottom_right_latitude': bottom_right_latitude,
        'bottom_right_longitude': bottom_right_longitude
    })

if __name__ == '__main__':
    app.run(debug=True)
