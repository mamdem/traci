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



def sampling(data):    
    X, Y = list(), list()

    for i in range(5):
        x= list()
        x.append(data['a'][i])
        x.append(data['b'][i])
        x.append(data['c'][i])
        x.append(data['d'][i])
        x.append(data['e'][i])

        X.append(x)
        Y.append(data['result'][i])
    return array(X), array(Y)

data = pd.read_excel("C:/Users/MHD/Desktop/traciTests/traci.xlsx")
X, Y = sampling(data)
for i in range(len(X)):
    print(X[i], Y[i])
print(data.shape)

n_features = 1

X = X.reshape((X.shape[0], X.shape[1], n_features))

model = Sequential()
model.add(LSTM(50, activation='relu', input_shape=(None, n_features)))
model.add(Dense(1))
model.compile(optimizer='adam', loss='mse')

# reshape from [samples, timesteps] into [samples, timesteps, features]
model.summary()

# fit model
model.fit(X, Y, epochs=200, verbose=0)

# demonstrate prediction
x_input = array([7, 3, 48,12,5])
x_input = x_input.reshape((1, 5, n_features))
yhat = model.predict(x_input, verbose=0)

if(yhat[0][0]>0.8):
    print("YESS passer")
else:
    print("Noo ne passe  pas")
print(yhat)

# https://analyticsindiamag.com/tutorial-on-univariate-single-step-style-lstm-in-time-series-forecasting/
# kaggle.com/code/andkul/deep-lstm-to-predict-rainfall/notebook
# machinelearningmastery.com/how-to-develop-lstm-models-for-time-series-forecasting/
# https://fr.dll-files.com/download/463f36ccae2309704fba7e88860b03ad/nvcuda.dll.html?c=WEF4Vk5vZ0xzM25FeVNUTTdhWUptZz09
