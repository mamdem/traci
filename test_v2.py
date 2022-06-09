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
import Pedestrian as ped

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
		self.allPedestrians=[]
		self.dictAllPedestrian={}
		self.waitPedestrians=[]
		self.dictWaitPedestrian={}
		self.engagePedestrians=[]
		self.dictEngagePedestrians={}
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
		print("###################### Etape "+str(self.te)+"  ##################################")
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
					randGenre = random.randint(0,1)
					randAge = random.randint(1,5)
					traci.person.add(personID, self.fromEdge, 0)
									
					traci.person.appendWalkingStage(personID, [self.fromEdge, self.toEdge], tc.ARRIVALFLAG_POS_MAX)
					# traci.person.appendWaitingStage(personID, 22)
				
					if(randGenre==1 and randAge>1 and randAge<5):
						traci.person.setType(personID, "homme-adulte")
					elif (randGenre==0 and randAge>1 and randAge<5):
						traci.person.setType(personID, "femme-adulte")
					elif (randGenre==0 and randAge==1):
						traci.person.setType(personID, "jeune-femme")
					elif (randGenre==1 and randAge==1):
						traci.person.setType(personID, "jeune-homme")
					elif (randGenre==0 and randAge==5):
						traci.person.setType(personID, "vielle-femme")
					elif (randGenre==1 and randAge==5):
						traci.person.setType(personID, "vieux-homme")
					

					self.dictAllPedestrian[personID]=ped.Pedestrian(personID, randGenre, randAge, 0,2.0)
					# On ajoute le piéton avec ses propriétés dans la liste des Pedestians
					# self.allPedestrians.append(ped.Pedestrian(personID, genre, ))
					
					
			

			self.waitPedestrians.clear()
			self.dictWaitPedestrian={}
			for key, value in self.dictAllPedestrian.items():
				if(traci.person.getLanePosition(key)>=18.0):
					traci.person.setSpeed(key, 0.0)
					self.dictWaitPedestrian[key]=value
			# for i in range(len(self.allPedestrians)):
			# 	if (traci.person.getLanePosition(self.allPedestrians[i])>=18.0):
			# 		traci.person.setSpeed(self.allPedestrians[i],0.0)
			# 		self.waitPedestrians.append(self.allPedestrians[i])
				
			# # On supprime les piétons en attentes dans la liste de tous les piétons


			engaged=0			
			for key, value in self.dictWaitPedestrian.items():
				# print(str(len(self.waitPedestrians))+" sont en attentes")
				self.dictWaitPedestrian[key].setWaitingTime(value.getWaitingTime()+1)
				if (traci.person.getLanePosition(key)>=18.0):
					genre = random.randint(0,1)
					age = random.randint(1,3)
					# Liste de tous les vehicule
					vehicles = traci.edge.getLastStepVehicleIDs("gneE0")
					# Le vehicule le plus proche
					nearest_vehicle = vehicles[len(vehicles)-1]
					# Distance entre le vehicule (le plus proche du pieton) et le piéton
					dist = 174.68-traci.vehicle.getDistance(nearest_vehicle)  
					# Vitesse du véhicule le plus proche des piétons
					speed_vehicle = traci.vehicle.getSpeed(nearest_vehicle)
					x_input = array([genre,value.age, value.waitingTime,speed_vehicle,dist, len(self.dictEngagePedestrians)])
					print(genre,value.age, value.waitingTime,value.travelSpeed,dist, engaged)
					x_input = x_input.reshape((1, 6, self.n_features))
					yhat = self.model.predict(x_input, verbose=0)
					print(yhat)
					print("\n\n-------")
					if(yhat[0][0]>0.5):
						traci.person.setSpeed(key,3.0)
						# self.dictEngagePedestrians[key]=value
						del self.dictAllPedestrian[key]
						engaged+=1
						
			# On supprime les piétons déjà enagés dans la liste des piétons en attente
			for key, value in self.dictEngagePedestrians.items():
				if(key in self.dictWaitPedestrian):
					del self.dictWaitPedestrian[key]

			# # On supprime les piétons qui ont atteint leurs destinations dans la liste des piétons engagés
			# for key, value in self.dictEngagePedestrians.items():
			# 	if(traci.person.getLanePosition(key)>25):
			# 		traci.person.setSpeed(key, 0.0)


			# for i in range(len(self.waitPedestrians)):
			# 	if(self.waitPedestrians[i]==self.allPedestrians[i]):

			# 		for i in range(len(self.waitPedestrians)):
			# 			# print(str(len(self.waitPedestrians))+" sont en attentes")
			# 			if (traci.person.getLanePosition(self.waitPedestrians[i])>=18.0):
			# 				genre = random.randint(0,1)
			# 				age = random.randint(1,3)
			# 				# Liste de tous les vehicule
			# 				vehicles = traci.edge.getLastStepVehicleIDs("gneE0")
			# 				# Le vehicule le plus proche
			# 				nearest_vehicle = vehicles[len(vehicles)-1]
			# 				# Distance entre le vehicule (le plus proche du pieton) et le piéton
			# 				dist = 174.68-traci.vehicle.getDistance(nearest_vehicle)  
			# 				# Vitesse du véhicule le plus proche des piétons
			# 				speed = traci.vehicle.getSpeed(nearest_vehicle)
			# 				x_input = array([genre,2, 9,speed,dist, 0])
			# 				print(genre,2,9,speed, dist,3)
			# 				x_input = x_input.reshape((1, 6, self.n_features))
			# 				yhat = self.model.predict(x_input, verbose=0)
			# 				print(yhat)
			# 				print("\n\n-------")
			# 				if(yhat[0][0]>0.5):
			# 					# for i in range(len(self.allPedestrians)):
			# 					traci.person.setSpeed(self.waitPedestrians[i],4.0)
			# 					self.allPedestrians.remove(self.waitPedestrians[i])
								
			# for i in range(self.engagePedestrians):
			# 	if(self.engagePedestrians[i]==self.waitPedestrians[i]):
			# 		self.waitPedestrians.remove(self.engagePedestrians[i])
			# 		self.allPedestrians.remove(self.engagePedestrians[i])

			# if(traci.person.getLanePosition(self.pedestrianPrefixedID + str(self.count-1))>13.0):
			# 	traci.person.setSpeed(self.pedestrianPrefixedID + str(self.count - 1),0.0)
			# 	self.allPedestrians.append(self.pedestrianPrefixedID + str(self.count - 1))
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
