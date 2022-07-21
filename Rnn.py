from itertools import count
import os
from re import T
import sys
import numpy
import tensorflow
from statistics import mode
import matplotlib.pyplot as plt
from numpy import array
import keras.models as km
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
        for i in range(len(self.data)):
            x=list()
            genre,age,crossing_risk, ped_influence, ped_impatience = self.transformData(
                self.data['genre'][i],
                self.data['age'][i],
                self.data['tps_patience'][i],
                self.data['vitesse'][i],
                self.data['distance'][i],
                self.data['pieton_engage'][i]
            )
            x.append(genre)
            x.append(age)
            x.append(crossing_risk)
            x.append(ped_influence)
            x.append(ped_impatience)
            # print(genre)
            # print(age)
            # print(crossing_risk)
            # print(ped_influence)
            # print(ped_impatience)
            # print("Engagement : ", self.data['pieton_engage'][i])

            X.append(x)
            Y.append(self.data['engagement'][i])
        return array(X), array(Y)
    
    def transformData(self,genre, age, tps_patience, vitesse, distance, pieton_engage):
        # Calcul du rique detraversée pieton
        ped_crossing_time=0
        ped_max_impatience_time=0
        if(age==1):
            if(genre==0):  # Jeune-fille
                ped_crossing_time = random.uniform(3,4.5)
                ped_max_impatience_time=32
            else:          # Jeune-garçon
                ped_crossing_time = random.uniform(3.5,5)
                ped_max_impatience_time=30
        elif(age==2):
            if(genre==0):  # Homme-adulte
                ped_crossing_time = random.uniform(4,5)
                ped_max_impatience_time=25
            else:          # Femme-adulte
                ped_crossing_time = random.uniform(5,6.5)
                ped_max_impatience_time=30
        else:
            if(genre==0):  # Vieux-homme
                ped_crossing_time = random.uniform(1.5,3)
                ped_max_impatience_time=35
            else:          # Vielle-femme
                ped_crossing_time = random.uniform(2,4)
                ped_max_impatience_time=45

        vhcle_arrival_time = distance/vitesse

        neural_crossing_risk = min(1,(vhcle_arrival_time/ped_crossing_time))  # Risque de traversée

        neural_ped_influence = min(1,(pieton_engage/5)) # Influence piéton
        
        neural_ped_impatience = min(1,(tps_patience/ped_max_impatience_time))  # Impatience piéton

        return genre,age,neural_crossing_risk, neural_ped_influence, neural_ped_impatience

    def initializeLSTM(self):
        self.X, self.Y = self.getDataFromExcel()
        for i in range (len(self.X)):
             print(self.X, self.Y)
        print(self.data.shape)
        #self.X = self.X.reshape((self.X.shape[0], self.X.shape[1], self.n_features))
        #self.model.add(LSTM(50, activation='relu', input_shape=(None, self.n_features)))
        #self.model.add(Dense(1))
        #self.model.compile(optimizer='adam', loss='mse')
        #self.model.summary()
        #self.model.fit(self.X, self.Y, epochs=200, verbose=0)

        #Pour enregistrer un modèle
        #self.model.save("my_model")
        #Pour charger un modèle

        self.model = km.load_model("my_model")
        self.model.summary()

    def predictPassage(self, x_input):
        x_input = x_input.reshape(1,5, self.n_features)
        yhat = self.model.predict(x_input, verbose=0)

        return yhat

        


