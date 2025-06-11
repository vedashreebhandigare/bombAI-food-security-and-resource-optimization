# bombAI-food-security-and-resource-optimization

# 🌾 bombAI – Food Security and Resource Optimization

Empowered Multilingual AI Platform for Agriculture & Surplus Food Redistribution

## 🧠 Overview

**bombAI** is a full-stack, AI-powered platform that bridges two crucial aspects of the food ecosystem:

1. **Plant Disease Detection** using deep learning
2. **NGO & Food Bank Locator** for smart surplus food redistribution

The platform combines agricultural innovation and real-time connectivity to optimize food production and minimize food waste.

---

## 💡 Key Features

### 🧪 Plant Disease Detector

* Built using **Flask**, **TensorFlow**, and **OpenCV**
* Trained on a large dataset with **50,000+ images** covering **38+ plant diseases** (sourced from Kaggle)
* Predicts plant type, disease name, and confidence score
* Offers **personalized recommendations**: watering needs, nutrient deficiencies, pest control, and treatment methods
* **Multilingual UI** support (Hindi, Marathi, English) for accessibility

### 🥘 NGO & Food Bank Locator

* Real-time, **location-based interface** to connect food donors with nearby NGOs/food banks
* Donors input food type, quantity, and freshness date to ensure only viable food is redistributed
* Generates a **Certificate of Appreciation** for users after successful submission
* Helps reduce food waste while addressing hunger and resource gaps

---

## 🔧 Tech Stack

| Category    | Tools Used                |
| ----------- | ------------------------- |
| Frontend    | HTML, CSS                 |
| Backend     | Flask (Python)            |
| ML/DL Model | TensorFlow, OpenCV        |
| Dataset     | PlantVillage (via Kaggle) |
| Geolocation | Browser Geolocation APIs  |

---

## 📹 Project Preview

A complete walkthrough of the project is available here:
https://drive.google.com/file/d/1FoCHOxBudGnHJIaV7I5xMS_24tRUpc05/view?usp=drive_link

## 📁 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/vedashreebhandigare/bombAI-food-security-and-resource-optimization.git
cd bombAI-food-security-and-resource-optimization
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### 4. Launch the App

```bash
python app.py
```

Then open `http://localhost:5000` in your browser.

