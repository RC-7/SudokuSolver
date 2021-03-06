import numpy as np
import tensorflow as tf
from sklearn.preprocessing import LabelBinarizer
import pandas as pd


class DigitClassifier:
    def __init__(self, training=False):
        if training:
            self.train_model()
        else:
            self.model = tf.keras.models.load_model('../model/CNNDigitClassifier')

    def train_model(self):
        mnist = tf.keras.datasets.mnist
        (x_train, y_train), (x_test, y_test) = mnist.load_data()

        x_train, x_test = x_train / 255.0, x_test / 255.0

        x_train = x_train.reshape(list(x_train.shape) + [1])
        x_test = x_test.reshape(list(x_test.shape) + [1])

        le = LabelBinarizer()
        y_train = le.fit_transform(y_train)
        y_test = le.transform(y_test)

        input_shape = (28, 28, 1)

        model = tf.keras.models.Sequential([
            tf.keras.layers.Conv2D(32, kernel_size=5, activation='relu', input_shape=input_shape),
            tf.keras.layers.MaxPool2D(),
            tf.keras.layers.Dropout(0.04),
            tf.keras.layers.Conv2D(64, kernel_size=5, activation='relu'),
            tf.keras.layers.MaxPool2D(),
            tf.keras.layers.Dropout(0.04),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dropout(0.04),
            tf.keras.layers.Dense(10, activation='softmax'),
        ])

        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy'],
        )

        epochs = 10
        batch_size = 128

        history = model.fit(
            x_train, y_train,
            validation_data=(x_test, y_test),
            epochs=epochs,
            batch_size=batch_size,
            verbose=0,
        )

        self.save_model(model, history)
        self.model = model

    def predict_digits(self, digit_image):
        prediction = self.model.predict(digit_image)
        return np.argmax(prediction)

    @staticmethod
    def save_model(model, history):
        model.save("../model/CNNDigitClassifier", save_format="h5")

        history_frame = pd.DataFrame(history.history)
        fig_loss = history_frame.loc[:, ['loss', 'val_loss']].plot(title='Loss plot').get_figure()
        fig_loss.savefig('../model/loss')
        fig_accuracy =history_frame.loc[:, ['accuracy', 'val_accuracy']].plot(title='Accuracy plot').get_figure()
        fig_accuracy.savefig('../model/accuracy')

        history_frame.to_csv('../model/CNN_history.txt', mode='a')

        with open('../model/CNN_history.txt', 'a') as fh:
            model.summary(print_fn=lambda x: fh.write(x + '\n'))
