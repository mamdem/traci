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
import Rnn as rnn
import csv
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
		self.arrivedVeh=[]
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
		self.rnn = rnn.Rnn(self.data)
		self.rnn.initializeLSTM()
		self.te=0

		self.co2=0
		self.co=0
		self.hc=0
		self.nox=0
		self.nox=0
		self.pmx=0
		self.noise=0
		self.fuel=0
		self.timeloss=0
		self.waitingTime=0

		self.DDDWaitingTime=0
		self.taxiWaitingTime=0
		self.tataWaitingTime=0
		self.particulierWaitingTime=0
		self.carrapideWaitingTime=0

		self.DDDNb=0
		self.taxiNb=0
		self.tataNb=0
		self.particulierNb=0
		self.carrapideNb=0

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
			v['arrivalTime']=arrival
			idRoute = v['idRoute']
			vType = v['vType']
			waiting = v['waiting']
			timeLoss = v['timeLoss']
			pos = v['pos']
			speedWithoutTraCI = v['speedWithoutTraCI']
			driverImperfection = v['driverImperfection']
			self.co2+=Co2
			self.co+=Co
			self.hc+=Hc
			self.nox+=NOx
			self.pmx+=PMx
			self.fuel+=fuel
			self.noise+=noise
			self.timeloss+=timeLoss

			if(vType=="DakarDemDikk"):
				self.DDDWaitingTime+=traci.simulation.getTime()
				self.DDDNb+=1
			elif(vType=="TATA"):
				self.tataWaitingTime+=traci.simulation.getTime()
				self.tataNb+=1
			elif(vType=="Taxi"):
				self.taxiNb+=1
				self.taxiWaitingTime+=traci.simulation.getTime()
			elif(vType=="CarRapide"):
				self.carrapideNb+=1
				self.carrapideWaitingTime+=traci.simulation.getTime()
			else:
				self.particulierNb+=1
				self.particulierWaitingTime+=traci.simulation.getTime()
			# print(' --> ', id, ' : ', _id, ', eclass = ', eclass, ', Co2 = ', Co2, ', ',Co, ', ',Hc, ', ',NOx, ', ',PMx, ', ',fuel, ', ',noise, ', idRoute = ',idRoute, ', vType = ',vType, ', waiting = ',waiting, ', timeLoss = ',timeLoss, ', ',pos, ', speed = ',speed, ', speedWithoutTraCI = ',speedWithoutTraCI, ', depart = ',depart, ', arrival = ',arrival, ', departSpeed = ',departSpeed, ', personNumber = ',personNumber, ', driverImperfection = ',driverImperfection)
			self.vehicles.pop(id, None)
		# Adding new pedestrians
		self.generatePedestrians()
		
		# indicate that the step listener should stay active in the next step
		return True
	
	
	def generatePedestrians(self):
		# Adding new pedestrians
		return
		self.te+=1
		# print("###################### Etape "+str(self.te)+"  ##################################")
		try:
			rand = random.random()
			# print("CO2 : ", self.v['co2'])
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
					# x_input = array([genre,value.age, value.waitingTime,speed_vehicle,dist, len(self.dictEngagePedestrians)])
					#print(genre,value.age, value.waitingTime,value.travelSpeed,dist, engaged)
					# x_input = x_input.reshape((1, 6, self.n_features))
					# yhat = self.model.predict(x_input, verbose=0)
					genre,age,neural_crossing_risk, neural_ped_influence, neural_ped_impatience=self.rnn.transformData(genre, age, value.waitingTime, speed_vehicle, dist,len(self.dictEngagePedestrians));
					x_input = array([genre,age,neural_crossing_risk, neural_ped_influence, neural_ped_impatience])
					yhat = self.rnn.predictPassage(x_input)
					#print(yhat)
					#print("\n\n-------")
					if(yhat[0][0]>0.8):
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
		# print(traci.simulation.getEndTime())
		# if((step > 3) and (traci.simulation.getMinExpectedNumber() == 0)):
		if(traci.simulation.getTime()==3400):
			break
		step += 1
	# Ending the simulation
	# print(' -- nbArrived = ', pedestrianManager.nbArrived)
	# print(' -- quantityCO2 = ', pedestrianManager.co2)
	# print(' -- quantityCO = ', pedestrianManager.co)
	# print(' -- quantityHC = ', pedestrianManager.hc)
	# print(' -- quantityNox = ', pedestrianManager.nox)
	# print(' -- quantityNoise = ', pedestrianManager.noise)
	# print(' -- quantityFuel = ', pedestrianManager.fuel)
	# print(' -- quantityFuel = ', pedestrianManager.fuel)
	# print(' -- quantityTimeLoss = ', pedestrianManager.timeloss)
	# print(' -- NbVehicles = ', len(pedestrianManager.vehicles))

	qCO2_DDD = 0
	qCO2_particulier=0
	qCO2_carrapide=0
	qCO2_taxi=0
	qCO2_tata=0

	qCO_DDD = 0
	qCO_particulier=0
	qCO_carrapide=0
	qCO_taxi=0
	qCO_tata=0

	qHc_DDD = 0
	qHc_particulier=0
	qHc_carrapide=0
	qHc_taxi=0
	qHc_tata=0

	qNox_DDD = 0
	qNox_particulier=0
	qNox_carrapide=0
	qNox_taxi=0
	qNox_tata=0

	qNoise_DDD=0
	qNoise_particulier=0
	qNoise_carrapide=0
	qNoise_taxi=0
	qNoise_tata=0

	qPmx_DDD=0
	qPmx_particulier=0
	qPmx_carrapide=0
	qPmx_taxi=0
	qPmx_tata=0
	
	arrival_time_DDD=0
	arrival_time_particulier=0
	arrival_time_carrapide=0
	arrival_time_taxi=0
	arrival_time_tata=0

	for key, value in pedestrianManager.vehicles.items():
		if(value['vType']=="DakarDemDikk"):
			qCO2_DDD+=value['Co2']
			qCO_DDD+=value['Co']
			qHc_DDD+=value['Hc']
			qNox_DDD+=value['NOx']
			qNoise_DDD+=value['noise']
			qPmx_DDD+=value['PMx']
		elif(value['vType']=="TATA"):
			qCO2_tata+=value['Co2']
			qCO_tata+=value['Co']
			qHc_tata+=value['Hc']
			qNox_tata+=value['NOx']
			qNoise_tata+=value['noise']
			qPmx_tata+=value['PMx']
		elif(value['vType']=="Taxi"):
			qCO2_taxi+=value['Co2']
			qCO_taxi+=value['Co']
			qHc_taxi+=value['Hc']
			qNox_taxi+=value['NOx']
			qNoise_taxi+=value['noise']
			qPmx_taxi+=value['PMx']
		elif(value['vType']=="CarRapide"):
			qCO2_carrapide+=value['Co2']
			qCO_carrapide+=value['Co']
			qHc_carrapide+=value['Hc']
			qNox_carrapide+=value['NOx']
			qNoise_carrapide+=value['noise']
			qPmx_carrapide+=value['PMx']
		else:
			qCO2_particulier+=value['Co2']
			qCO_particulier+=value['Co']
			qHc_particulier+=value['Hc']
			qNox_particulier+=value['NOx']
			qNoise_particulier+=value['noise']
			qPmx_particulier+=value['PMx']

	ped_passing=True

	header = ['id', 'vehicule', 'gaz', 'emission','ped']
	data = [
		[31,'tata','co2',int(qCO2_tata),ped_passing],
		[32,'DDD','co2',int(qCO2_DDD),ped_passing],
		[33,'taxi','co2',int(qCO2_taxi),ped_passing],
		[34,'particulier','co2',int(qCO2_particulier),ped_passing],
		[35,'carrapide','co2',int(qCO2_carrapide),ped_passing],

		[36,'tata','co',int(qCO_tata),ped_passing],
		[37,'DDD','co',int(qCO_DDD),ped_passing],
		[38,'taxi','co',int(qCO_taxi),ped_passing],
		[39,'particulier','co',int(qCO_particulier),ped_passing],
		[40,'carrapide','co',int(qCO_carrapide),ped_passing],

		[41,'tata','hc',int(qHc_tata),ped_passing],
		[42,'DDD','hc',int(qHc_DDD),ped_passing],
		[43,'taxi','hc',int(qHc_taxi),ped_passing],
		[44,'particulier','hc',int(qHc_particulier),ped_passing],
		[45,'carrapide','hc',int(qHc_carrapide),ped_passing],

		[46,'tata','nox',int(qNox_tata),ped_passing],
		[47,'DDD','nox',int(qNox_DDD),ped_passing],
		[48,'taxi','nox',int(qNox_taxi),ped_passing],
		[49,'particulier','nox',int(qNox_particulier),ped_passing],
		[50,'carrapide','nox',int(qNox_carrapide),ped_passing],

		[51,'tata','noise',int(qNoise_tata),ped_passing],
		[52,'DDD','noise',int(qNoise_DDD),ped_passing],
		[53,'taxi','noise',int(qNoise_taxi),ped_passing],
		[54,'particulier','noise',int(qNoise_particulier),ped_passing],
		[55,'carrapide','noise',int(qNoise_carrapide),ped_passing],

		[56,'tata','pmx',int(qPmx_tata),ped_passing],
		[57,'DDD','pmx',int(qPmx_DDD),ped_passing],
		[58,'taxi','pmx',int(qPmx_taxi),ped_passing],
		[59,'particulier','pmx',int(qPmx_particulier),ped_passing],
		[60,'carrapide','pmx',int(qPmx_carrapide),ped_passing]
	]

	print("TIME TRAVEL DDD : ", pedestrianManager.DDDNb)
	print("TIME TRAVEL TAXI : ", pedestrianManager.taxiNb)
	print("TIME TRAVEL PARTICULIER : ", pedestrianManager.particulierNb)
	print("TIME TRAVEL TATA : ", pedestrianManager.tataNb)
	print("TIME TRAVEL CARRAPIDE : ", pedestrianManager.carrapideNb)

	# with open('C:/csv/sumo_output.csv', 'a+', encoding='UTF8', newline='') as f:
	# 	writer = csv.writer(f)

	# 	# write the header
	# 	writer.writerow(header)

	# 	# write the data
	# 	writer.writerows(data)
	
	try:
		traci.close()
	except Exception as exc:
		print(exc)

main()

#https://sumo.dlr.de/pydoc/traci._person.html#PersonDomain-replaceStage
