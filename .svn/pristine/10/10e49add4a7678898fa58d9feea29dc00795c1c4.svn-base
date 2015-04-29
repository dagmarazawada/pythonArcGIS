#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('C:\\Python27\ArcGIS10.2\\lib')
sys.path.append('C:\\Python27\ArcGIS10.2\\DLLs')
sys.path.append('C:\\Python27\ArcGIS10.2\\lib\site-packages')
sys.path.append('C:\\Program Files (x86)\\ArcGIS\\Desktop10.2\\arcpy')
sys.path.append('C:\\Program Files (x86)\\ArcGIS\\Desktop10.2\\bin')
sys.path.append('C:\\Program Files (x86)\\ArcGIS\\Desktop10.2\\ArcToolbox\\Scripts')

import arcpy
import os
import datetime
import time


myPath = "D:\\_exportDM\\"
oracleConnector = myPath + "oracle_dzaw.sde"
baza4Connector = myPath + "baza4_dzaw.sde"
baza4HydroConnector = myPath + "baza4Hydro.sde"

#mxd = arcpy.mapping.MapDocument(myPath+"psh_test.mxd")
#layers = arcpy.mapping.ListLayers(mxd)

prjFile = os.path.join(arcpy.GetInstallInfo()["InstallDir"],"Coordinate Systems/Projected Coordinate Systems/National Grids/Europe/ETRS 1989 Poland CS92.prj")
spatialRef = arcpy.SpatialReference(prjFile)

startTime = time.time()
now = datetime.datetime.now()

def createGDB(tempdb_name):
    tmpDatabase = myPath+tempdb_name
    if os.path.exists(tmpDatabase):
        arcpy.Delete_management(tmpDatabase) #os.remove(tmpDatabase)
    arcpy.CreateFileGDB_management(myPath, tempdb_name)

createGDB("tempGDB.gdb")

arcpy.env.overwriteOutput = True


def oracleXY2baza4(sourceLyr, tempName, targetLyr):
    now = datetime.datetime.now()
    arcpy.AddMessage('--- Przetwarzanie zasilania Baza4 [' + now.strftime("%Y/%m/%d %H:%M:%S") + '] ---')

    inputs = [oracleConnector + "\\" + sourceLyr]
    temps = [myPath + "tempGDB.gdb\\" + tempName]
    #targets = [baza4Connector + "\\" + targetLyr]
    targets = [baza4HydroConnector + "\\" + targetLyr]
    fieldX = ["X"]
    fieldY = ["Y"]
    events = ["tempLyr"]
    
    i = 0
    for n in inputs:
        arcpy.AddMessage('  --> Usuwanie danych z '+targets[i])
        arcpy.DeleteRows_management(targets[i]) 
        
        arcpy.AddMessage('  --> Tworzenie warstwy przestrzennej ' + temps[i])
        arcpy.MakeXYEventLayer_management(n, fieldX[i], fieldY[i], events[i], spatialRef, "")
        arcpy.FeatureClassToFeatureClass_conversion (events[i], myPath+"tempGDB.gdb\\", tempName)
       
        arcpy.AddMessage('  --> Zasilanie danych do ' + targets[i])
        arcpy.Append_management(temps[i], targets[i], "NO_TEST", "", "")
  
        i=i+1

### WYWOLANIE FUNKCJI
###oracleXY2baza4(sourceLyr, tempName, targetLyr)

## SPR MONITORING STANU CHEMICZNEGO ?? za długa kolumna??

oracleXY2baza4("HYDRO.MV_MONITORING_V62", "MV_MONITORING_V62", "sde.HYDRO.HYDRO_MONITORING")

exportTime = time.time()-startTime
print("wykonanie wszystkiego trwalo [s]: %.2f" % round(exportTime,2))
