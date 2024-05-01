import tensorflow as tf
import cv2
import numpy as np
import sys
sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

# Load the saved model
saved_model_path =r'D:\code\projects\rice_disease_nn\model_1\rice_disease_model.h5'
model = tf.keras.models.load_model(saved_model_path)

# Load and preprocess the image
img_path = r'D:\code\projects\rice_disease_nn\model_3\dataset_m3\train\tungro\tungro1738.jpg'
img = cv2.imread(img_path)
img = cv2.resize(img, (224, 224))
img = img.astype(np.float32) / 255.0
img = np.expand_dims(img, axis=0)

# Make predictions
predictions = model.predict(img)

# Get the predicted class label
predicted_class = np.argmax(predictions)
labels = ['bacterial blight', 'blast', 'brown spot', 'tungro']

print('Predicted class:', labels[predicted_class])