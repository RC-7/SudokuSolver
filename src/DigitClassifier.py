import tensorflow as tf
from sklearn.preprocessing import LabelBinarizer
import pandas as pd


class DigitClassifier:
    def __init__(self, training=False):
        if training:
            self.train_model()
        else:
            self.load_model()
            self.model.summary()

    def train_model(self):
        mnist = tf.keras.datasets.mnist
        (x_train, y_train), (x_test, y_test) = mnist.load_data()

        x_train, x_test = x_train / 255.0, x_test / 255.0

        x_train = x_train.reshape(list(x_train.shape) + [1])
        x_test = x_test.reshape(list(x_test.shape) + [1])

        le = LabelBinarizer()

        input_shape = (28, 28, 1)

        y_train = le.fit_transform(y_train)
        y_test = le.transform(y_test)
        model = tf.keras.models.Sequential([
            tf.keras.layers.Conv2D(32, kernel_size=5, activation='relu', input_shape=input_shape),
            tf.keras.layers.MaxPool2D(),
            tf.keras.layers.Dropout(0.04),
            tf.keras.layers.Conv2D(64, kernel_size=5, activation='relu'),
            tf.keras.layers.MaxPool2D(),
            tf.keras.layers.Dropout(0.04),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dropout(0.04),
            tf.keras.layers.Dense(10, activation='softmax'),
        ])

        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy'],
        )

        EPOCHS = 10
        BATCH_SIZE = 128

        history = model.fit(
            x_train, y_train,
            validation_data=(x_test, y_test),
            epochs=EPOCHS,
            batch_size=BATCH_SIZE,
            verbose=0,
        )

        self.save_model(model, history)

    def load_model(self):
        self.model = tf.keras.models.load_model('../model/CNNDigitClassifier')

    def save_model(self, model, history):
        model.save("../model/CNNDigitClassifier", save_format="h5")

        history_frame = pd.DataFrame(history.history)
        fig_loss = history_frame.loc[:, ['loss', 'val_loss']].plot(title='Loss plot').get_figure()
        fig_loss.savefig('../model/loss')
        fig_accuracy =history_frame.loc[:, ['accuracy', 'val_accuracy']].plot(title='Accuracy plot').get_figure()
        fig_accuracy.savefig('../model/accuracy')

        history_frame.to_csv('../model/CNN_history.txt', mode='a')

        with open('../model/CNN_history.txt', 'a') as fh:
            model.summary(print_fn=lambda x: fh.write(x + '\n'))
