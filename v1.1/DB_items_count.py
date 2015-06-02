#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('C:\\Python27\ArcGIS10.2\\lib')
sys.path.append('C:\\Python27\ArcGIS10.2\\DLLs')
sys.path.append('C:\\Python27\ArcGIS10.2\\lib\site-packages')
sys.path.append('C:\\Program Files (x86)\\ArcGIS\\Desktop10.2\\arcpy')
sys.path.append('C:\\Program Files (x86)\\ArcGIS\\Desktop10.2\\bin')
sys.path.append('C:\\Program Files (x86)\\ArcGIS\\Desktop10.2\\ArcToolbox\\Scripts')
sys.path.append('C:\\Python27\\Lib\\site-packages\\')

import arcpy

### definicja katalogu, plikow polaczenia do bazy, projektu mxd
myPath = "D:\\_exportDM\\"
baza4Connector = myPath + "baza4_dzaw.sde"
baza4HydroConnector = myPath + "baza4Hydro.sde"
oracleConnector = myPath + "oracle_dzaw.sde"
oracleGISPIG2Connector = myPath + "oracle_gis_pig2.sde"
oracle_hydro_sdo = myPath + "oracle_hydro_sdo.sde"

baza4 = [baza4Connector+"\\sde.SDE.ZLOZA_GRANICE", baza4Connector+"\\sde.SDE.ZLOZA_OBSZARY", baza4Connector+"\\sde.SDE.ZLOZA_TERENY", baza4Connector+"\\sde.SDE.OTWORY", baza4Connector+"\\sde.SDE.JASKINIE", baza4HydroConnector+"\\sde.HYDRO.HYDRO_MWP", baza4HydroConnector+"\\sde.HYDRO.HYDRO_OTWORY"]

oracle = [oracleGISPIG2Connector+"\\GIS_PIG2.ZLOZA_GRANICE", oracleGISPIG2Connector+"\\GIS_PIG2.ZLOZA_OBSZARY", oracleGISPIG2Connector+"\\GIS_PIG2.ZLOZA_TERENY", oracleGISPIG2Connector+"\\GIS_PIG2.OTWORY", oracleGISPIG2Connector+"\\GIS_PIG2.JASKINIE", oracle_hydro_sdo+"\\HYDRO_SDO.HYDRO_MWP", oracle_hydro_sdo+"\\HYDRO_SDO.HYDRO_OTWORY"]

### sprawdzenie liczby obiektów

print "\nSprawdzenie liczby obiektow w warstwach BAZA4: "
i = 0
for n in baza4:
    print n[28:] + " : " + str(arcpy.GetCount_management(n))
    i=i+1

print "\nSprawdzenie liczby obiektow w warstwach ORACLE: "
j = 0
for n in oracle:
    print n[33:] + " : " + str(arcpy.GetCount_management(n))
    j=j+1