import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import tensorflow as tf
import tensorflow_hub as hub

from nnfs.datasets import spiral_data
from sklearn import model_selection

inputs, classifications = spiral_data(samples=1000, classes=3)

oneHotClassifications = np.zeros((len(classifications), 3))

for i in range(len(classifications)):
    oneHotClassifications[i][classifications[i]] = 1
    
trainingInputs, tempInputs, trainingClassifications, tempClassifications = model_selection.train_test_split(inputs, oneHotClassifications, test_size=0.4, random_state=0)
testInputs, validationInputs, testClassifications, validationClassifications = model_selection.train_test_split(tempInputs, tempClassifications, test_size=0.5, random_state=0)

model = tf.keras.Sequential([
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(3, activation='softmax')
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss=tf.keras.losses.CategoricalCrossentropy(),
    metrics=['accuracy'])

model.fit(
    trainingInputs,
    trainingClassifications,
    batch_size=10,
    epochs=60,
    validation_data=(validationInputs, validationClassifications)
)

print("\nEvaluate on test data\n")

model.evaluate(testInputs, testClassifications)