import numpy as np
import tensorflow as tf
from sklearn.preprocessing import LabelBinarizer
import pandas as pd


class DigitClassifier:
    def __init__(self, training=False):
        if training:
            self.model = self.train_model()
        else:
            self.model = self.load_model()

    def train_model(self):
        mnist = tf.keras.datasets.mnist
        (x_train, y_train), (x_test, y_test) = mnist.load_data()
        x_train, x_test = x_train / 255.0, x_test / 255.0
        le = LabelBinarizer()
        y_train = le.fit_transform(y_train)
        y_test = le.transform(y_test)
        model = tf.keras.models.Sequential([
            tf.keras.layers.Conv2D(32, kernel_size=5, activation='relu', input_shape=(28, 28, 1)),
            tf.keras.layers.MaxPool2D(),
            tf.keras.layers.Dropout(0.04),
            tf.keras.layers.Conv2D(64, kernel_size=5, activation='relu'),
            tf.keras.layers.MaxPool2D(),
            tf.keras.layers.Dropout(0.04),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dropout(0.04),
            tf.keras.layers.Dense(128, activation='softmax'),
        ])

        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy'],
        )

        EPOCHS = 1
        BATCH_SIZE = 128

        history = model.fit(
            x_train, y_train,
            validation_data=(x_test, y_test),
            epochs=EPOCHS,
            verbose=BATCH_SIZE,
        )

        self.save_model(model, history)

    def load_model(self):
        pass

    def save_model(self, model, history):
        model.save("../model/CNN", save_format="h5")

        history_frame = pd.DataFrame(history.history)
        history_frame.loc[:, ['loss', 'val_loss']].plot()
        history_frame.loc[:, ['binary_accuracy', 'val_binary_accuracy']].plot()

        history_frame.to_csv('../model/CNN_history')
