from flask import Flask, request, jsonify, render_template
import tensorflow as tf
import numpy as np
from PIL import Image

app = Flask(__name__)
model = tf.keras.models.load_model("plant_disease_model.h5")

class_names = ["Apple__Apple_scab","Apple__Black_rot","Apple_Cedar_apple_rust", "Apple__healthy", "Blueberry__healthy","Cherry_(including_sour)__healthy","Cherry_(including_sour)__Powdery_mildew","Corn_(maize)__Cercospora_leaf_spot Gray_leaf_spot","Corn_(maize)__Common_rust_","Corn_(maize)__healthy","Corn_(maize)__Northern_Leaf_Blight","Grape__Black_rot","Grape_Esca__(Black_Measles)","Grape__healthy","Grape__Leaf_blight_(Isariopsis_Leaf_Spot)","Orange__Haunglongbing_(Citrus_greening)","Peach__Bacterial_spot","Peach__healthy","Pepper,_bell__Bacterial_spot","Pepper_bell__healthy","Potato_Early_blight","Potato__healthy","Potato__Late_blight","Raspberry__healthy","Soybean_healthy","Squash__Powdery_mildew","Strawberry__healthy","Strawberry__Leaf_scorch","Tomato__Bacterial_spot","Tomato__Early_blight","Tomato__healthy","Tomato__Late_blight","Tomato__Leaf_Mold","Tomato__Septoria_leaf_spot","Tomato__Spider_mites Two-spotted_spider_mite","Tomato__Target_Spot","Tomato__Tomato_mosaic_virus","Tomato_Tomato_Yellow_Leaf_Curl_Virus"]  # Add all classes

def predict_disease(image_path):
    img = Image.open(image_path).resize((224, 224))
    img_array = np.expand_dims(np.array(img) / 255.0, axis=0)
    predictions = model.predict(img_array)
    class_index = np.argmax(predictions)
    return class_names[class_index]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]
        file.save("uploaded_image.jpg")
        prediction = predict_disease("uploaded_image.jpg")
        return jsonify({"Prediction": prediction})
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
