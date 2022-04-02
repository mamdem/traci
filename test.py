#!/usr/bin/python
# -*- coding: latin-1 -*-

# See: https://sumo.dlr.de/docs/TraCI/Interfacing_TraCI_from_Python.html

import os
import sys
# import optparse

if 'SUMO_HOME' in os.environ:
	tools = os.path.join(os.environ['SUMO_Home'], 'tools')
	sys.path.append(tools)
else:
	sys.exit("please declare environment variable 'SUMO_HOME' ")

sumoBinary = "C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo-gui.exe"
# sumoCmd = [sumoBinary, "-c", "C:\\test SUMO\\Simulation\\SUMO.sumo.cfg"]
sumoCmd = [sumoBinary, "-c", "C:\\test SUMO\\traciTests\\SUMO.sumo.cfg"]
# sumoCmd = [sumoBinary, "-c", "yourConfiguration.sumocfg"]

import traci
import traci.constants as tc

def vehicleSubscription():
	traci.start(sumoCmd)
	vehID = 'v1'
	traci.vehicle.subscribe(vehID, (tc.VAR_ROAD_ID, tc.VAR_LANEPOSITION))
	print(traci.vehicle.getSubscriptionResults(vehID))
	step = 0
	while step < 100:
		traci.simulationStep()
		print(step, ' : ', traci.vehicle.getSubscriptionResults(vehID))
		step += 1
	traci.close()

def junctionSubscription():
	traci.start(sumoCmd)
	junctionID = '1133849117'
	traci.junction.subscribeContext(junctionID, tc.CMD_GET_VEHICLE_VARIABLE, 42, [tc.VAR_SPEED, tc.VAR_WAITING_TIME])
	print(traci.junction.getContextSubscriptionResults(junctionID))
	step = 0
	while step < 100:
		traci.simulationStep()
		print(step, ' : ', traci.junction.getContextSubscriptionResults(junctionID))
		step += 1
	traci.close()

def edgeSubscription():
	traci.start(sumoCmd)
	edgeID = 'gneE98.24'
	# traci.edge.subscribeContext(edgeID, tc.CMD_GET_VEHICLE_VARIABLE, 42, [tc.VAR_SPEED, tc.VAR_WAITING_TIME, tc.VAR_ACCUMULATED_WAITING_TIME])
	traci.edge.subscribeContext(edgeID, tc.CMD_GET_EDGE_VARIABLE, 42, [tc.LAST_STEP_MEAN_SPEED, tc.LAST_STEP_OCCUPANCY])
	print(traci.edge.getContextSubscriptionResults(edgeID))
	step = 0
	while step < 100:
		traci.simulationStep()
		print(step, ' : ', traci.edge.getContextSubscriptionResults(edgeID))
		step += 1
	traci.close()

class ExampleListener(traci.StepListener):
	def __init__(self, edgeID):
		# traci.StepListener.__init__(self)
		self.edgeID = edgeID
		self.step_ = 0
	
	def step(self, t):
		print(self.step_, ' : ', traci.edge.getContextSubscriptionResults(self.edgeID))
		self.step_ += 1
		# do something after every call to simulationStep
		# print("ExampleListener called with parameter %s." % t)
		# indicate that the step listener should stay active in the next step
		return True

def edgeSubscriptionListener():
	sumoBinary = "C:\\Program Files (x86)\\Eclipse\\Sumo\\bin\\sumo.exe"
	sumoCmd = [sumoBinary, "-c", "C:\\test SUMO\\Simulation\\SUMO.sumo.cfg"]
	traci.start(sumoCmd)
	
	edgeID = 'gneE98.24'
	# traci.edge.subscribeContext(edgeID, tc.CMD_GET_VEHICLE_VARIABLE, 42, [tc.VAR_SPEED, tc.VAR_WAITING_TIME, tc.VAR_ACCUMULATED_WAITING_TIME])
	traci.edge.subscribeContext(edgeID, tc.CMD_GET_EDGE_VARIABLE, 42, [tc.LAST_STEP_MEAN_SPEED, tc.LAST_STEP_OCCUPANCY])
	print(traci.edge.getContextSubscriptionResults(edgeID))
	
	listener = ExampleListener(edgeID)
	traci.addStepListener(listener)
	
	step = 0
	while step < 100:
		traci.simulationStep()
		step += 1
	traci.close()

def pedestrianTesting():
	traci.start(sumoCmd)
	step = 0
	count = 5000
	while step < 1000:
		traci.simulationStep()
		for i in range(4):
			personID = "person." + str(count)
			traci.person.add(personID, "gneE13", 0)
			count += 1
			traci.person.appendWalkingStage(personID, ["gneE13", "gneE13.43"], tc.ARRIVALFLAG_POS_MAX)
		step += 1
	traci.close()


# vehicleSubscription()
# junctionSubscription()
# edgeSubscription()
# edgeSubscriptionListener()
pedestrianTesting()
