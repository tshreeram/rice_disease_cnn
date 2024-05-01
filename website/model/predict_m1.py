import tensorflow as tf
import numpy as np
import cv2
import sys
sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

def predict_disease_m1(img_path):
    # Load the saved model
    from keras.applications import DenseNet121
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import BatchNormalization, Flatten, Dense

    # Load the pre-trained DenseNet121 model
    conv_1 = DenseNet121(weights='imagenet', include_top=False, input_shape=(256, 256, 3))
    conv_1.trainable = False

    # Create the model architecture
    model = Sequential()
    model.add(conv_1)
    model.add(BatchNormalization())
    model.add(Flatten())
    model.add(Dense(256, activation='relu'))
    model.add(BatchNormalization())
    model.add(Dense(10, activation='softmax'))

    # Create a dummy input tensor
    dummy_input = tf.zeros((1, 256, 256, 3))

    # Call the model on the dummy input tensor
    _ = model(dummy_input)

    # Load the saved model weights
    model.load_weights(r"D:\code\projects\rice_disease_nn\website\model\my_model_transfer_new.keras")

    # Load and preprocess the image
    img = cv2.imread(img_path)
    img = cv2.resize(img,(256, 256))
    img = img.astype(np.float32) / 255.0
    img = np.expand_dims(img, axis=0)  # Add batch dimension

    # Predict using the model
    pred = model.predict(img)
    print(pred)
    # Normalize probabilities
    pred /= np.sum(pred)

    # Print normalized probabilities
    # print("Normalized Probabilities:", pred)

    true_labels = ['bacterial leaf blight', 'brown spot', 'healthy', 'leaf blast', 'leaf scald', 'narrow brown spot', 'neck blast', 'rice hispa', 'sheath blight', 'tungro']
    # Get the index of the maximum probability (predicted class)
    predicted_class = true_labels[np.argmax(pred)]
    print("Predicted Class:", predicted_class)

    return predicted_class