from itertools import count
import os
from re import T
import sys
import numpy
import tensorflow
from statistics import mode
import matplotlib.pyplot as plt
from numpy import array
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dense
from numpy import hstack

import traci
import traci.constants as tc
import random
import Pedestrian as ped

class Rnn:
    def __init__(self, data):
        self.data=data
        self.X, self.Y="",""
        self.n_features = 1
        self.model = Sequential()
    
    def getDataFromExcel(self):
        X,Y=list(),list()
        for i in range(10):
            x=list()
            x.append(self.data['genre'][i])
            x.append(self.data['jeune'][i])
            x.append(self.data['tps_patience'][i])
            x.append(self.data['vitesse'][i])
            x.append(self.data['distance'][i])
            x.append(self.data['pieton_engage'][i])
            X.append(x)
            Y.append(self.data['engagement'][i])
        return array(X), array(Y)

    def initializeLSTM(self):
        self.X, self.Y = self.getDataFromExcel()
        for i in range (len(self.X)):
            print(self.X, self.Y)
        print(self.data.shape)

        self.X = self.X.reshape((self.X.shape[0], self.X.shape[1], self.n_features))
        self.model.add(LSTM(50, activation='relu', input_shape=(None, self.n_features)))
        self.model.add(Dense(1))
        self.model.compile(optimizer='adam', loss='mse')
        self.model.summary()
        self.model.fit(self.X, self.Y, epochs=200, verbose=0)

    def predictPassage(self, x_input):
        x_input = x_input.reshape(1,6, self.n_features)
        yhat = self.model.predict(x_input, verbose=0)

        return yhat

        


