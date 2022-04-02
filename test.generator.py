#!/usr/bin/python
# - - coding: latin-1 - -

import random

old_vTypes = '\n<vType id="DakarDemDikk" accel="2.6" decel="4.5" sigma="0" length="10" minGap="10" maxSpeed="25" color="240,230,140" guiShape="bus" emissionClass="HBEFA3/PC_G_EU4" laneChangeModel="LC2013" lcStrategic="1000" lcSpeedGain="100"/>\
	\n<vType id="TATA" accel="2.6" decel="4.5" sigma="0" length="9" minGap="10" maxSpeed="25" color="255,255,255"   guiShape="bus"  emissionClass="HBEFA3/PC_G_EU4" laneChangeModel="LC2013" lcStrategic="1000" lcSpeedGain="100"/>\
	\n<vType id="Taxi"  accel="2.6" decel="4.5" sigma="0" length="5" minGap="10" maxSpeed="25" color="255,255,0" emissionClass="HBEFA3/PC_G_EU4" laneChangeModel="LC2013" lcStrategic="1000"  lcSpeedGain="100"/>\
	\n<vType id="CarRapide" accel="2.6" decel="4.5" sigma="0" length="8" minGap="10" maxSpeed="25" color="255,127,80"  emissionClass="HBEFA3/PC_G_EU4" laneChangeModel="LC2013" lcStrategic="1000"  lcSpeedGain="100"/>\
	\n<vType id="Particulier"  accel="2" color="0,0,255" decel="4" guiShape="passenger"  length="4.5" maxSpeed="36" sigma="0" minGap="10" />'

vTypes = '<vType id="DakarDemDikk" accel="2.6" decel="4" sigma="0" length="12" width="2.6" minGap="2.5" maxSpeed="20" color="240,230,140" guiShape="bus" personCapacity="85" emissionClass="HBEFA3/HDV_D_EU4" laneChangeModel="LC2013" lcStrategic="1" lcSpeedGain="1" lcOvertakeRight="1" lcOpposite="0"/>\
\n<vType id="TATA" accel="2" decel="4" sigma="0.3" length="9" minGap="1.5" width="2.4" maxSpeed="17" color="255,255,255"   guiShape="bus" personCapacity="42"  emissionClass="HBEFA3/HDV_D_EU4" laneChangeModel="LC2013" lcStrategic="3" lcSpeedGain="3" lcOvertakeRight="3" lcOpposite="3" lcImpatience="0.1" />\
\n<vType id="Taxi"  accel="2.6" decel="4.5" sigma="0.4" length="4.5"  minGap="1" maxSpeed="20" color="255,255,0" guiShape="passenger" personCapacity="5"  emissionClass="HBEFA3/PC_D_EU3" laneChangeModel="LC2013" lcStrategic="5"  lcSpeedGain="5" lcOvertakeRight="0.5" lcOpposite="5" lcImpatience="0.5" />\
\n<vType id="CarRapide" accel="1.2" decel="3.5" sigma="0.6" length="7" width="2.1" minGap="1" maxSpeed="14" color="255,127,80" guiShape="bus" personCapacity="28" emissionClass="HBEFA3/LDV_G_EU1" laneChangeModel="LC2013" lcStrategic="3"  lcSpeedGain="3" lcOvertakeRight="0.1" lcOpposite="3" lcImpatience="1"/>\
\n<vType id="Particulier"  accel="3.5" color="0,0,255" decel="4.5" guiShape="passenger"  length="4.5" maxSpeed="25" sigma="0.1" minGap="1.5" personCapacity="5" emissionClass="HBEFA3/PC" laneChangeModel="LC2013" lcStrategic="2"  lcSpeedGain="2" lcOvertakeRight="0.3" lcOpposite="3"/>'

routes = '\n<route edges="gneE0 gneE10 gneE8.45 gneE7 gneE7.47 gneE2.120" color="yellow" id="cices_citeKG"/>\
    \n<route edges="gneE0 gneE0.81 gneE0.329" color="green" id="cices_fann"/>\
    \n<route edges="gneE0 gneE10 gneE8.45 -gneE2.115" color="yellow" id="cices_mermoz"/>\
    \n<route edges="-gneE2 gneE11 gneE1.309" color="blue" id="citeKG_cices"/>\
    \n<route edges="-gneE2 gneE8 gneE8.45 gneE12 gneE0.329" color="yellow" id="citeKG_fann"/>\
    \n<route edges="-gneE2 gneE8 gneE8.45 -gneE2.115" color="magenta" id="citeKG_mermoz"/>\
    \n<route edges="gneE1 gneE1.30 gneE1.309" color="cyan" id="fann_cices"/>\
    \n<route edges="gneE1 gneE9 gneE7.47 gneE2.120" color="red" id="fann_citeKG"/>\
    \n<route edges="gneE1 gneE9 gneE7.47 gneE8 gneE8.45 -gneE2.115" color="yellow" id="fann_mermoz"/>\
    \n<route edges="gneE2 gneE7 gneE7.47 gneE11 gneE1.309" color="yellow" id="mermoz_cices"/>\
    \n<route edges="gneE2 gneE7 gneE7.47 gneE2.120" color="yellow" id="mermoz_citeKG"/>\
    \n<route edges="gneE2 gneE12 gneE0.329" color="yellow" id="mermoz_fann"/>\
    \n<route edges="gneE0 gneE10 gneE8.45 gneE12 gneE0.329" color="255,114,0" id="cices_fann_DDD"/>\
    \n<route edges="gneE1 gneE9 gneE7.47 gneE11 gneE1.309" color="255,78,0" id="fann_cices_DDD"/>\
    \n<route edges="gneE13 gneE13.25 gneE13.43" color="255,70,0" id="pietons_citeKG"/>'

# busStops = { 'cices_fann' : { 'TATA' : ['busStop_1'], 'Taxi' : ['busStop_1'], 'CarRapide' : ['busStop_1'] }, 
busStops = { 'cices_fann' : { 'TATA' : ['busStop_1'], 'CarRapide' : ['busStop_1'] }, 
'cices_fann_DDD' : { 'DakarDemDikk' : ['busStop_2', 'busStop_3'] }, 
'cices_citeKG' : { 'Taxi' : ['busStop_2'] }, 
'cices_mermoz' : { 'Taxi' : ['busStop_2'] },
# 'fann_cices' : { 'TATA' : ['busStop_6'], 'Taxi' : ['busStop_6'], 'CarRapide' : ['busStop_6'] }, 
'fann_cices' : { 'TATA' : ['busStop_6'], 'CarRapide' : ['busStop_6'] }, 
'fann_cices_DDD' : { 'DakarDemDikk' : ['busStop_4', 'busStop_5'] }, 
'fann_citeKG' : { 'Taxi' : ['busStop_4'] }, 
'fann_mermoz' : { 'Taxi' : ['busStop_4'] } }

data = { 'cices_fann' : { 'DakarDemDikk' : 0, 'TATA' : 86, 'Taxi' : 417, 'CarRapide' : 83, 'Particulier' : 3430 }, 
'cices_fann_DDD' : { 'DakarDemDikk' : 22, 'TATA' : 0, 'Taxi' : 0, 'CarRapide' : 0, 'Particulier' : 0 }, 
'cices_citeKG' : { 'DakarDemDikk' : 0, 'TATA' : 0, 'Taxi' : 42, 'CarRapide' : 0, 'Particulier' : 250 }, 
'cices_mermoz' : { 'DakarDemDikk' : 0, 'TATA' : 0, 'Taxi' : 17, 'CarRapide' : 0, 'Particulier' : 137 }, 
'citeKG_cices' : { 'DakarDemDikk' : 0, 'TATA' : 0, 'Taxi' : 3, 'CarRapide' : 0, 'Particulier' : 21 }, 
'citeKG_fann' : { 'DakarDemDikk' : 0, 'TATA' : 0, 'Taxi' : 32, 'CarRapide' : 0, 'Particulier' : 263 }, 
'citeKG_mermoz' : { 'DakarDemDikk' : 0, 'TATA' : 0, 'Taxi' : 6, 'CarRapide' : 0, 'Particulier' : 46 }, 
'fann_cices' : { 'DakarDemDikk' : 0, 'TATA' : 12, 'Taxi' : 19, 'CarRapide' : 13, 'Particulier' : 105 }, 
'fann_cices_DDD' : { 'DakarDemDikk' : 3, 'TATA' : 0, 'Taxi' : 0, 'CarRapide' : 0, 'Particulier' : 0 }, 
'fann_citeKG' : { 'DakarDemDikk' : 0, 'TATA' : 0, 'Taxi' : 4, 'CarRapide' : 0, 'Particulier' : 32 }, 
'fann_mermoz' : { 'DakarDemDikk' : 0, 'TATA' : 0, 'Taxi' : 6, 'CarRapide' : 0, 'Particulier' : 53 }, 
'mermoz_cices' : { 'DakarDemDikk' : 0, 'TATA' : 0, 'Taxi' : 19, 'CarRapide' : 0, 'Particulier' : 158 }, 
'mermoz_citeKG' : { 'DakarDemDikk' : 0, 'TATA' : 0, 'Taxi' : 19, 'CarRapide' : 0, 'Particulier' : 160 }, 
'mermoz_fann' : { 'DakarDemDikk' : 0, 'TATA' : 0, 'Taxi' : 3, 'CarRapide' : 0, 'Particulier' : 21 } }

def generate(filename, firstDepart = 1, lastDepart = 3600, minStopDuration = 5, maxStopDuration = 20):
	global vTypes
	global routes
	global data
	global busStops
	
	# nbVehicules = 0
	# for r in data:
		# for t in data[r]:
			# nbVehicules += data[r][t]q 
	
	# depart_plage = lastDepart - firstDepart
	duree = (lastDepart - firstDepart + 1)
	durationPlage = maxStopDuration - minStopDuration
	id = 0
	vehicules = []
	for r in data:
		# nbVehicules = 0
		# for t in data[r]:
			# nbVehicules += data[r][t]
		# pas_des_departs = max(1, duree / nbVehicules)
		
		for t in data[r]:
			nbVehicules = data[r][t]
			if(nbVehicules == 0):
				continue
			nbBusStops = 0
			if((r in busStops) and (t in busStops[r])):
				nbBusStops = len(busStops[r][t])
			pas_des_departs = max(1, duree / nbVehicules)
			for k in range(data[r][t]):
				id += 1
				depart = firstDepart + ((k * pas_des_departs) % duree)
				xml = '\n<vehicle id="v' + str(id) + '" type="' + t + '" route="' + r + '" depart="' + str(depart) + '" departSpeed="speedLimit"'
				if(t == 'Particulier'):
					xml += ' personNumber="' + str(random.randint(1, 2)) +'"/>'
				elif(t == 'Taxi'):
					if(nbBusStops > 0):
						xml += ' personNumber="' + str(random.randint(1, 3)) +'">'
						if(random.random() < 0.4):
							pos = min(nbBusStops-1, random.randint(0, 1))
							# duration = minStopDuration + random.randint(0, durationPlage)
							duration = random.randint(3, 10)
							xml += '\n\t<stop busStop="' + busStops[r][t][pos] + '" duration="' + str(duration) + '" parking="true"/>'
						xml += "\n</vehicle>"
					else:
						xml += "/>"
				elif(t == 'DakarDemDikk'):
					if(nbBusStops > 0):
						xml += ' personNumber="' + str(random.randint(70, 82)) +'">'
						if(random.random() < 0.85):
							pos = min(nbBusStops-1, random.randint(0, 1))
							# duration = minStopDuration + random.randint(0, durationPlage)
							duration = 5 + random.randint(0, 10)
							xml += '\n\t<stop busStop="' + busStops[r][t][pos] + '" duration="' + str(duration) + '" parking="true"/>'
							if(pos == 0 and random.random() < 0.75):
								duration = minStopDuration + random.randint(0, durationPlage)
								xml += '\n\t<stop busStop="' + busStops[r][t][1] + '" duration="' + str(duration) + '" parking="true"/>'
						xml += "\n</vehicle>"
					else:
						xml += "/>"
				else: # CarRapide, NdiagaNdiaye, TATA
					if(nbBusStops > 0):
						if(t == 'TATA'):
							xml += ' personNumber="' + str(random.randint(38, 42)) +'">'
						else:
							xml += ' personNumber="' + str(random.randint(24, 28)) +'">'
						if(random.random() < 0.75):
							pos = min(nbBusStops-1, random.randint(0, 1))
							duration = minStopDuration + random.randint(0, durationPlage)
							xml += '\n\t<stop busStop="' + busStops[r][t][pos] + '" duration="' + str(duration) + '" parking="false"/>'
						xml += "\n</vehicle>"
					else:
						xml += "/>"
				vehicules.append({'xml':xml, 'depart':depart})
	
	for i in range(len(vehicules)-1):
		for j in range(i+1, len(vehicules)):
			if(vehicules[i]['depart'] > vehicules[j]['depart']):
				tmp = vehicules[i]
				vehicules[i] = vehicules[j]
				vehicules[j] = tmp
	
	file = open(filename, 'w')
	file.write('<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">')
	file.write(vTypes + "\n")
	file.write(routes + "\n")
	for v in vehicules:
		file.write(v['xml'])
	file.write('</routes>')
	file.close()

filename = './test_final.rou.xml'
firstDepart = 1
lastDepart = 3600
minStopDuration = 10
maxStopDuration = 20
generate(filename, firstDepart, lastDepart, minStopDuration, maxStopDuration)

print(' --> All tasks ended!')