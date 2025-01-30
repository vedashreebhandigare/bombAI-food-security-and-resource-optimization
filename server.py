from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np
from PIL import Image

app = Flask(__name__)
CORS(app)

# ✅ Check if model exists before loading
MODEL_PATH = "plant_disease_model.h5"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file '{MODEL_PATH}' not found!")

model = load_model(MODEL_PATH)

# ✅ Folder to store uploaded images
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ✅ Class names mapping (Ensure this matches your model output)
class_names = [
    "Apple_Apple_scab", "Apple_Black_rot", "Apple_Cedar_apple_rust", "Apple_healthy",
    "Blueberry_healthy", "Cherry(including_sour)_healthy", "Cherry(including_sour)_Powdery_mildew",
    "Corn(maize)_Cercospora_leaf_spot Gray_leaf_spot", "Corn(maize)_Common_rust", "Corn_(maize)_healthy",
    "Corn(maize)_Northern_Leaf_Blight", "Grape_Black_rot", "Grape_Esca(Black_Measles)", "Grape_healthy",
    "Grape_Leaf_blight(Isariopsis_Leaf_Spot)", "Orange_Haunglongbing(Citrus_greening)", "Peach_Bacterial_spot",
    "Peach_healthy", "Pepper,_bell_Bacterial_spot", "Pepper_bell_healthy", "Potato_Early_blight", "Potato_healthy",
    "Potato_Late_blight", "Raspberry_healthy", "Soybean_healthy", "Squash_Powdery_mildew", "Strawberry_healthy",
    "Strawberry_Leaf_scorch", "Tomato_Bacterial_spot", "Tomato_Early_blight", "Tomato_healthy", "Tomato_Late_blight",
    "Tomato_Leaf_Mold", "Tomato_Septoria_leaf_spot", "Tomato_Spider_mites Two-spotted_spider_mite",
    "Tomato_Target_Spot", "Tomato_Tomato_mosaic_virus", "Tomato_Tomato_Yellow_Leaf_Curl_Virus"
]

# Custom recommendations for each plant and disease
recommendation_dict = {
    "Apple_Apple_scab": [
        "✅ Disease: Apple Scab. This fungal disease causes dark, sunken lesions on leaves, fruit, and stems.",
        "💧 Watering: Ensure the soil is well-drained and avoid overhead watering to prevent fungal spores from splashing.",
        "🌿 Nutrients: Ensure balanced fertilization, particularly focusing on nitrogen. Soil amendments may be necessary to increase soil pH.",
        "🦠 Pest Control: Monitor for aphids and spider mites, which can spread the disease. Apply appropriate insecticides if necessary.",
        "🧴 Treatment: Apply fungicides like neem oil or sulfur-based fungicides in early spring to prevent scab development."
    ],
    "Apple_Black_rot": [
        "✅ Disease: Black Rot. This bacterial infection causes black lesions on the fruit and can lead to fruit drop.",
        "💧 Watering: Ensure soil has good drainage, as over-watering can increase susceptibility to bacterial rot.",
        "🌿 Nutrients: Maintain high soil organic matter and balanced nitrogen levels. Avoid high phosphorus levels.",
        "🦠 Pest Control: Aphids can spread black rot. Consider using insecticidal soap or horticultural oils to manage pest populations.",
        "🧴 Treatment: Use copper-based fungicides for bacterial control and prune infected plant parts regularly to reduce disease spread."
    ],
    "Apple_Cedar_apple_rust": [
        "✅ Disease: Cedar Apple Rust. This disease results in orange lesions on leaves and fruit.",
        "💧 Watering: Keep the soil evenly moist but avoid excessive watering, which encourages fungal growth.",
        "🌿 Nutrients: Fertilize the plant with a balanced mix, emphasizing potassium to help with disease resistance.",
        "🦠 Pest Control: The disease is spread by cedar trees. Removing nearby cedar trees can help limit infection.",
        "🧴 Treatment: Apply fungicides like mancozeb or chlorothalonil during the growing season to prevent infection."
    ],
    "Apple_healthy": [
        "✅ Healthy Apple Tree: Ensure proper watering and sunlight exposure for optimal fruit growth.",
        "💧 Watering: Water deeply but infrequently to encourage strong root growth. Mulch around the base to conserve moisture.",
        "🌿 Nutrients: Apply a balanced fertilizer in early spring to support growth and fruit development.",
        "🦠 Pest Control: Regularly inspect for common pests like codling moths and aphids. Use organic controls like neem oil as needed.",
        "⚖️ Maintenance: Prune regularly to maintain shape and remove dead or diseased branches."
    ],
    "Blueberry_healthy": [
        "✅ Healthy Blueberry: Blueberries thrive in acidic soil and require proper care for optimal yield.",
        "💧 Watering: Blueberries need consistent moisture. Use a drip irrigation system to keep the soil evenly moist.",
        "🌿 Nutrients: Use fertilizers designed for acid-loving plants. Avoid high-nitrogen fertilizers.",
        "🦠 Pest Control: Keep an eye out for aphids and spider mites. Apply insecticidal soap or neem oil as needed.",
        "⚖️ Maintenance: Mulch around the base to maintain soil acidity and prevent weeds."
    ],
    "Cherry(including_sour)_healthy": [
        "✅ Healthy Cherry Tree: Cherries need a sunny spot and well-drained soil to thrive.",
        "💧 Watering: Water regularly, especially during dry spells, but avoid waterlogging as it can lead to root rot.",
        "🌿 Nutrients: Apply a balanced fertilizer with adequate nitrogen, phosphorus, and potassium. Keep soil slightly acidic.",
        "🦠 Pest Control: Monitor for pests like aphids and fruit flies. Consider using row covers to protect fruit.",
        "⚖️ Maintenance: Prune in late winter to maintain shape and remove dead or diseased branches."
    ],
    "Cherry(including_sour)_Powdery_mildew": [
        "✅ Disease: Powdery Mildew. This fungal disease appears as a white, powdery coating on leaves and stems.",
        "💧 Watering: Avoid wetting the leaves while watering. Water at the base to reduce fungal spore spread.",
        "🌿 Nutrients: Apply a balanced fertilizer with sufficient nitrogen and potassium to promote plant health.",
        "🦠 Pest Control: Powdery mildew can be spread by aphids. Apply horticultural oils or insecticidal soap if necessary.",
        "🧴 Treatment: Use sulfur-based fungicides or neem oil for early-stage control."
    ],
    "Corn(maize)_Cercospora_leaf_spot Gray_leaf_spot": [
        "✅ Disease: Cercospora Leaf Spot. This fungal disease causes irregular gray spots with dark borders.",
        "💧 Watering: Water early in the day to allow the leaves to dry before nightfall. Avoid wetting the foliage.",
        "🌿 Nutrients: Ensure proper nitrogen levels in the soil. Use organic matter to improve soil texture and drainage.",
        "🦠 Pest Control: Aphids and other pests can spread the disease. Monitor closely and apply insecticidal soap if needed.",
        "🧴 Treatment: Use fungicides like chlorothalonil or copper-based treatments to reduce fungal growth."
    ],
    "Corn(maize)_Common_rust": [
        "✅ Disease: Common Rust. This fungal infection causes orange, pustular growths on the leaves and stems.",
        "💧 Watering: Ensure even watering to prevent drought stress, but avoid excessive moisture which can promote fungal growth.",
        "🌿 Nutrients: Fertilize with a balanced nitrogen-phosphorus-potassium mix. Ensure soil is not excessively compacted.",
        "🦠 Pest Control: Corn borers and aphids can spread rust. Apply appropriate insecticides as necessary.",
        "🧴 Treatment: Fungicides like tebuconazole can be used to manage common rust in corn."
    ],
    # Add recommendations for other plants and diseases...
}

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)

@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        # ✅ Save uploaded image
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        # ✅ Open and preprocess image
        img = Image.open(filepath)
        img = img.resize((224, 224))  # Adjust to match model's input size
        img_array = np.array(img) / 255.0  # Normalize
        img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension

        # ✅ Predict
        predictions = model.predict(img_array)
        predicted_class = np.argmax(predictions, axis=1)[0]

        # ✅ Get plant & disease name
        if 0 <= predicted_class < len(class_names):
            plant_disease = class_names[predicted_class].split("_")
            plant_name = plant_disease[0]
            disease_name = "_".join(plant_disease[1:]) if len(plant_disease) > 1 else "Healthy"
        else:
            plant_name, disease_name = "Unknown", "Unknown"

        confidence = float(np.max(predictions) * 100)

        # Get the relevant recommendations based on the predicted disease
        recommendations = recommendation_dict.get(f"{plant_name}_{disease_name}", [
            "✅ Ensure proper watering and sunlight.",
            "✅ Apply appropriate pesticides/fungicides.",
            "✅ Maintain proper soil health and nutrients."
        ])

        return jsonify({
            "plant": plant_name,
            "disease": disease_name,
            "confidence": confidence,
            "recommendations": recommendations
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
