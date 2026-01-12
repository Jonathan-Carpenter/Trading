import configparser
import datetime
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import tensorflow as tf

from sklearn import model_selection

from Data.TradingDataClient import TradingDataClient
from Model.Indicators.BollingerBandsCalculator import BollingerBandsCalculator
from Model.Indicators.ExponentialMovingAverageCalculator import ExponentialMovingAverageCalculator
from Model.Indicators.SimpleMovingAverageCalculator import SimpleMovingAverageCalculator
from ModelInputDataProvider import ModelInputDataProvider

# np.set_printoptions(threshold=sys.maxsize)

def plot_loss(history):
  plt.plot(history.history['loss'], label='loss')
  plt.plot(history.history['val_loss'], label='val_loss')
  plt.xlabel('Epoch')
  plt.ylabel('Mean Squared Loss')
  plt.legend()
  plt.grid(True)


startDate = datetime.date.fromisoformat("2021-02-01")
endDate = datetime.date.fromisoformat("2023-12-01")
windowSize = 90
predictionLookAhead = 10

config = configparser.ConfigParser()
config.read('dev.ini')

modelCheckpointLocation: str = config['tensorflow']['ModelCheckpointLocation']
modelSaveLocation: str = config['tensorflow']['ModelSaveLocation']

dbFileLocation: str = config['database']['DatabaseFileLocation']

dbClient = TradingDataClient(dbFileLocation)
dbClient.ensureSeeded()

allTickerIds = dbClient.getAllDailyTickerSymbols()

normalizer = tf.keras.layers.Normalization(axis=-1)

if True:
        
    print("\n###\nWARNING: TAKE A BACK-UP OF YOUR MODEL!\n###\n")
    print(f"This will begin training a NEW model. Any existing model file at {modelCheckpointLocation} and {modelSaveLocation} will be overwritten.")
    print("If you would like to continue training an existing model, stop now!")
    print("Are you sure? (Y/N)")
    
    response = input()
    
    if response not in ["Y", "y"]:
        print("Exiting.")
        exit()

    model = tf.keras.Sequential([
        normalizer,
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(1)
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='mean_squared_error')
        
else:
    
    print(f"\n###\nContinuing training model from file at {modelSaveLocation}.\n###\n")
    
    model = tf.keras.models.load_model(modelSaveLocation)
    
tickerIds = allTickerIds
inputs, labels, _, _ = ModelInputDataProvider(
    dbClient,
    [ExponentialMovingAverageCalculator(10, "EMA 10"), ExponentialMovingAverageCalculator(30, "EMA 30")],
    [BollingerBandsCalculator(SimpleMovingAverageCalculator(20, "SMA 20"))]).getData(
        tickerIds,
        startDate,
        endDate,
        windowSize,
        predictionLookAhead,
        oversample=True,
        plotDistribution=False)

trainingInputs, tempInputs, trainingLabels, tempLabels = model_selection.train_test_split(inputs, labels, test_size=0.4, random_state=0)
testInputs, validationInputs, testLabels, validationLabels = model_selection.train_test_split(tempInputs, tempLabels, test_size=0.5, random_state=0)

normalizer.adapt(trainingInputs)
normalizer.mean.numpy()

history = model.fit(
    trainingInputs,
    trainingLabels,
    batch_size=128,
    epochs=1000,
    validation_data=(validationInputs, validationLabels),
    callbacks=[
        tf.keras.callbacks.ModelCheckpoint(
            filepath=modelCheckpointLocation,
            save_best_only=True
        )
    ]
)

plot_loss(history)
plt.show()

print("\nEvaluate on test data\n")

model.evaluate(testInputs, testLabels)

model.save(modelSaveLocation)