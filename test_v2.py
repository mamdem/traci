#!/usr/bin/python
# -*- coding: latin-1 -*-
# See: https://sumo.dlr.de/docs/TraCI/Interfacing_TraCI_from_Python.html

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

if 'SUMO_HOME' in os.environ:
	tools = os.path.join(os.environ['SUMO_Home'], 'tools')
	sys.path.append(tools)
else:
	sys.exit("please declare environment variable 'SUMO_HOME' ")

sumoBinary = "C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo-gui.exe"
sumoCmd = [sumoBinary, "-c", "C:\\Users\MHD\\Desktop\\traciTests\\SUMO.sumo.cfg"]

import traci
import traci.constants as tc
import random

class PedestrianManager(traci.StepListener):
	def __init__(self, fromEdge, toEdge, pedestrianPrefixedID = 'person.1.', pedestrianProbability = 1.0, pedestrianNumberByStep = [1, 5]):
		# traci.StepListener.__init__(self)
		self.model = Sequential()
		self.data = pd.read_excel("C:/Users/MHD/Desktop/traciTests/traci.xlsx")
		self.fromEdge = fromEdge
		self.toEdge = toEdge
		self.pedestrianPrefixedID = pedestrianPrefixedID
		self.pedestrianProbability = pedestrianProbability
		self.pedestrianNumberByStep = pedestrianNumberByStep
		self.vehicles = {}
		self.waitPedestrian=[]
		self.nbArrived = 0
		self.count = 0
		self.n_features = 1
		self.X, self.Y="",""
		self.initializeLSTM()
		self.te=0
		
	
	def initializeLSTM(self):
		self.X, self.Y = self.sampling()
		for i in range(len(self.X)):
			print(self.X[i], self.Y[i])
		print(self.data.shape)

		self.n_features = 1

		self.X = self.X.reshape((self.X.shape[0], self.X.shape[1], self.n_features))
		
		self.model.add(LSTM(50, activation='relu', input_shape=(None, self.n_features)))
		self.model.add(Dense(1))
		self.model.compile(optimizer='adam', loss='mse')

		# reshape from [samples, timesteps] into [samples, timesteps, features]
		self.model.summary()

		# fit model
		self.model.fit(self.X, self.Y, epochs=200, verbose=0)


	def step(self, t = 0):
		# Listening simulation's evolution
		#The list of ids of vehicles which arrived (have reached their destination and are removed from the road network) in this time step.
		#La liste des identifiants des véhicules qui sont arrivés (ont atteint leur destination et sont retirés du réseau routier) dans ce pas de temps.
		arrivedIDList = traci.simulation.getArrivedIDList()
		# The list of ids of vehicles which departed (were inserted into the road network) in this time step.
		# La liste des identifiants des véhicules qui sont partis (ont été insérés dans le réseau routier) à ce pas de temps.
		departedIDList = traci.simulation.getDepartedIDList()
		# The list of ids of vehicles which were loaded in this time step.
		# La liste des identifiants des véhicules qui ont été chargés à ce pas de temps.
		loadedIDList = traci.simulation.getLoadedIDList()
		# The list of all vehicle ids waiting for insertion (with depart delay)
		#pendingVehicles = traci.simulation.getPendingVehicles()
		#print(str(arrivedIDList) + ' -- ' + str(departedIDList) + ' -- ' + str(loadedIDList) + ' -- ' + str(pendingVehicles) + ' -- ' + str(teleportIDList))
		
		for id in loadedIDList:
			v = {}
			v['depart'] = traci.simulation.getTime()
			v['personNumber'] = traci.vehicle.getPersonNumber(id)
			v['driverImperfection'] = traci.vehicle.getImperfection(id)
			v['eclass'] = traci.vehicle.getEmissionClass(id)
			v['vType'] = traci.vehicle.getTypeID(id)
			v['idRoute'] = traci.vehicle.getRouteID(id)
			v['Co2'] = 0
			v['Co'] = 0
			v['Hc'] = 0
			v['NOx'] = 0
			v['PMx'] = 0
			v['fuel'] = 0
			v['noise'] = 0
			v['waiting'] = 0
			v['timeLoss'] = 0
			v['pos'] = 0
			self.vehicles[id] = v
		
		for id in departedIDList:
			if(not id in self.vehicles):
				v = {}
				v['personNumber'] = traci.vehicle.getPersonNumber(id)
				v['driverImperfection'] = traci.vehicle.getImperfection(id)
				v['eclass'] = traci.vehicle.getEmissionClass(id)
				v['vType'] = traci.vehicle.getTypeID(id)
				v['idRoute'] = traci.vehicle.getRouteID(id)
				v['Co2'] = 0
				v['Co'] = 0
				v['Hc'] = 0
				v['NOx'] = 0
				v['PMx'] = 0
				v['fuel'] = 0
				v['noise'] = 0
				v['waiting'] = 0
				v['timeLoss'] = 0
				v['pos'] = 0
				self.vehicles[id] = v
			else:
				v = self.vehicles[id]
			v['depart'] = traci.simulation.getTime()
			v['speed'] = traci.vehicle.getSpeed(id)
			if(not 'departSpeed' in v):
				v['departSpeed'] = traci.vehicle.getSpeed(id)
			v['speedWithoutTraCI'] = traci.vehicle.getSpeedWithoutTraCI(id)
			v['Co2'] += traci.vehicle.getCO2Emission(id)
			v['Co'] += traci.vehicle.getCOEmission(id)
			v['Hc'] += traci.vehicle.getHCEmission(id)
			v['NOx'] += traci.vehicle.getNOxEmission(id)
			v['PMx'] += traci.vehicle.getPMxEmission(id)
			v['fuel'] += traci.vehicle.getFuelConsumption(id)
			v['noise'] += traci.vehicle.getNoiseEmission(id)
			v['waiting'] = traci.vehicle.getAccumulatedWaitingTime(id)
			v['timeLoss'] = 0 #traci.vehicle.getTimeLoss(id)
			v['pos'] = traci.vehicle.getPosition(id)
		
		for id in arrivedIDList:
			self.nbArrived += 1
			v = self.vehicles[id]
			_id = id.replace('v', '')
			depart = v['depart']
			arrival = traci.simulation.getTime()
			departSpeed = v['departSpeed']
			speed = v['speed']
			personNumber = v['personNumber']
			eclass = v['eclass']
			Co2 = v['Co2']
			Co = v['Co']
			Hc = v['Hc']
			NOx = v['NOx']
			PMx = v['PMx']
			fuel = v['fuel']
			noise = v['noise']
			idRoute = v['idRoute']
			vType = v['vType']
			waiting = v['waiting']
			timeLoss = v['timeLoss']
			pos = v['pos']
			speedWithoutTraCI = v['speedWithoutTraCI']
			driverImperfection = v['driverImperfection']
			#print(' --> ', id, ' : ', _id, ', eclass = ', eclass, ', Co2 = ', Co2, ', ',Co, ', ',Hc, ', ',NOx, ', ',PMx, ', ',fuel, ', ',noise, ', idRoute = ',idRoute, ', vType = ',vType, ', waiting = ',waiting, ', timeLoss = ',timeLoss, ', ',pos, ', speed = ',speed, ', speedWithoutTraCI = ',speedWithoutTraCI, ', depart = ',depart, ', arrival = ',arrival, ', departSpeed = ',departSpeed, ', personNumber = ',personNumber, ', driverImperfection = ',driverImperfection)
			self.vehicles.pop(id, None)
		# Adding new pedestrians
		self.generatePedestrians()
		
		# indicate that the step listener should stay active in the next step
		return True
	
	def sampling(self):    
		X, Y = list(), list()

		for i in range(5):
			x= list()
			x.append(self.data['genre'][i])
			x.append(self.data['jeune'][i])
			x.append(self.data['tps_patience'][i])
			x.append(self.data['vitesse'][i])
			x.append(self.data['distance'][i])
			x.append(self.data['pieton_engage'][i])

			X.append(x)
			Y.append(self.data['engagement'][i])
		return array(X), array(Y)
	
	def generatePedestrians(self):
		# Adding new pedestrians
		#return
		self.te+=1
		try:
			rand = random.random()
			
			if((rand < self.pedestrianProbability) and ((self.pedestrianPrefixedID != None) and (len(self.pedestrianPrefixedID)>0) and (self.pedestrianNumberByStep != None) and (len(self.pedestrianNumberByStep)>0))):
				if(len(self.pedestrianNumberByStep) == 1):
					#nb = self.pedestrianNumberByStep[0]
					nb = random.randint(self.pedestrianNumberByStep[0], self.pedestrianNumberByStep[1])
				else:
					nb = random.randint(self.pedestrianNumberByStep[0], self.pedestrianNumberByStep[1])
				if(nb <= 0):
					return
				for i in range(nb):
					self.count += 1
					personID = self.pedestrianPrefixedID + str(self.count)
					value = numpy.random.random(1)[0]
					
					traci.person.add(personID, self.fromEdge, 0)
					traci.person.appendWalkingStage(personID, [self.fromEdge, self.toEdge], tc.ARRIVALFLAG_POS_MAX)
					# traci.person.appendWaitingStage(personID, 22)
					if(value>0.5):
						traci.person.setType(personID, "homme-adulte")
					else:
						traci.person.setType(personID, "femme-adulte")
					self.waitPedestrian.append(personID)
					
			# Liste de tous les vehicule
			vehicles = traci.edge.getLastStepVehicleIDs("gneE0")
			# Le vehicule le plus proche
			nearest_vehicle = vehicles[len(vehicles)-1]
			# print(nearest_vehicle)
			
			# Distance entre le vehicule (le plus proche du pieton) et le piéton
			dist = 174.68-traci.vehicle.getDistance(nearest_vehicle)  
			# Vitesse du véhicule le plus proche des piétons
			speed = traci.vehicle.getSpeed(nearest_vehicle)

			# print(vehicles)
			# print(nearest_vehicle)
			# print(dist)
			# print(speed)
			# print("-----------")
			for i in range(len(self.waitPedestrian)):
				if (traci.person.getLanePosition(self.waitPedestrian[i])>=18.0):
					traci.person.setSpeed(self.waitPedestrian[i],0.0)

			if (traci.person.getLanePosition(self.waitPedestrian[0])>=18.0):
				genre = random.randint(0,1)
				age = random.randint(1,3)
				x_input = array([genre,age, self.te,speed,dist, 0])
				print(1,2,self.te,speed, dist,0)
				x_input = x_input.reshape((1, 6, self.n_features))
				yhat = self.model.predict(x_input, verbose=0)
				print(yhat)
				print("\n\n================================")
				if(yhat[0][0]>0.5):
					for i in range(len(self.waitPedestrian)):
						traci.person.setSpeed(self.waitPedestrian[i],4.0)
						# print("#######################  TIME WAITING  ################################")
						# print(traci.person.getWaitingTime(self.waitPedestrian[i]))
					self.waitPedestrian.clear()
					self.te=0
			# if(traci.person.getLanePosition(self.pedestrianPrefixedID + str(self.count-1))>13.0):
			# 	traci.person.setSpeed(self.pedestrianPrefixedID + str(self.count - 1),0.0)
			# 	self.waitPedestrian.append(self.pedestrianPrefixedID + str(self.count - 1))
		except Exception as exc:
			print(exc)

def main():
	traci.start(sumoCmd)
	# Set the current zoom factor for the given view.
	zoom = traci.gui.getZoom('View #0')
	traci.gui.setZoom('View #0', zoom*2.0)
	# Defining the edges for the pedestrians walk
	fromEdge = "gneE13"
	toEdge = "gneE13.25"
	data = pd.read_excel("C:/Users/MHD/Desktop/traciTests/traci.xlsx")
	# Initializing a PedestrianManager object
	# pedestrianManager = PedestrianManager(fromEdge, toEdge, pedestrianPrefixedID = 'person.', pedestrianProbability = 0.1, pedestrianNumberByStep = [1, 5])
	pedestrianManager = PedestrianManager(fromEdge, toEdge, pedestrianPrefixedID = 'person.', pedestrianProbability = 0.1, pedestrianNumberByStep = [0, 2])
	traci.addStepListener(pedestrianManager)
	# Starting the simulation
	step = 0
	while(True):
		traci.simulationStep()
		if((step > 3) and (traci.simulation.getMinExpectedNumber() == 0)):
			break
		step += 1
	# Ending the simulation
	print(' -- nbArrived = ', pedestrianManager.nbArrived)
	try:
		traci.close()
	except Exception as exc:
		print(exc)

main()

#https://sumo.dlr.de/pydoc/traci._person.html#PersonDomain-replaceStage
