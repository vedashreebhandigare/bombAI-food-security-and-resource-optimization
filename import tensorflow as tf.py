import tensorflow as tf
print("TensorFlow version:", tf.__version__)

# Ensure Keras works inside TensorFlow
from tensorflow.keras.models import load_model
print("Keras inside TensorFlow is working correctly!")
