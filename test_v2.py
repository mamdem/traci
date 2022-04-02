#!/usr/bin/python
# -*- coding: latin-1 -*-

# See: https://sumo.dlr.de/docs/TraCI/Interfacing_TraCI_from_Python.html

from itertools import count
import os
from re import T
import sys
# import optparse

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
		self.fromEdge = fromEdge
		self.toEdge = toEdge
		self.pedestrianPrefixedID = pedestrianPrefixedID
		self.pedestrianProbability = pedestrianProbability
		self.pedestrianNumberByStep = pedestrianNumberByStep
		self.vehicles = {}
		self.nbArrived = 0
		self.count = 0
	
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
	
	def generatePedestrians(self):
		# Adding new pedestrians
		#return
		print("yess")
		try:
			rand = random.random()
			if((rand < self.pedestrianProbability) and ((self.pedestrianPrefixedID != None) and (len(self.pedestrianPrefixedID)>0) and (self.pedestrianNumberByStep != None) and (len(self.pedestrianNumberByStep)>0))):
				if(len(self.pedestrianNumberByStep) == 1):
					nb = self.pedestrianNumberByStep[0]
				else:
					nb = random.randint(self.pedestrianNumberByStep[0], self.pedestrianNumberByStep[1])
				if(nb <= 0):
					return
				for i in range(nb):
					self.count += 1
					personID = self.pedestrianPrefixedID + str(self.count)
					traci.person.add(personID, self.fromEdge, 0)
					traci.person.appendWalkingStage(personID, [self.fromEdge, self.toEdge], tc.ARRIVALFLAG_POS_MAX)
					#### C'EST LA OU ON GENERE LES PIETONS UN A UN
					print(self.count)
		except Exception as exc:
			print(exc)

def main():
	traci.start(sumoCmd)
	# Set the current zoom factor for the given view.
	zoom = traci.gui.getZoom('View #0')
	traci.gui.setZoom('View #0', zoom*2.0)
	# Defining the edges for the pedestrians walk
	fromEdge = "gneE13"
	toEdge = "gneE13.43"
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
