import ee

try:
    ee.Initialize(project='vital-invention-439317-b6')
    print("Earth Engine API initialized successfully!")
except Exception as e:
    print(f"Failed to initialize Earth Engine API: {e}")

