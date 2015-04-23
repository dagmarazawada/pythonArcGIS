#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

driver = webdriver.Firefox()

DMlayers = []

def openLogin():
    driver.get("http://dm.pgi.gov.pl/dmadmin/LogOn.aspx")
    elem = driver.find_element_by_name("tbxLogin")
    elem.send_keys("dzaw")
    elem = driver.find_element_by_name("iptHaslo")
    elem.send_keys("R_ZOr3X123")
    elem.send_keys(Keys.RETURN)


def fillNames():  
    openLogin() # konsola czesto wylogowuje co powoduje bledy dlatego otwieram logowanie co warstwe
    elem = driver.find_element_by_name("btnPlikiBezOpisu")
    elem.send_keys(Keys.RETURN)
        
    elem = driver.find_element_by_id("Repeater1_ctl00_lblNazwa")
    filename = elem.get_attribute("innerHTML")
    elem = driver.find_element_by_name("Repeater1$ctl00$btnEdytuj")
    elem.send_keys(Keys.RETURN)
    print filename

    if "kontury" in filename:
        elem = driver.find_element_by_name("iptOpis")
        elem.send_keys(u'MIDAS - złoża kopalin (shp)')
        elem = driver.find_element_by_name("iptOpis_en")
        elem.send_keys("MIDAS - mineral raw materials deposits (shp)")
        elem.send_keys(Keys.RETURN)
        DMlayers.append(filename)
        
    if "obszary" in filename:
        elem = driver.find_element_by_name("iptOpis")
        elem.send_keys(u'MIDAS - obszary górnicze (shp)')
        elem = driver.find_element_by_name("iptOpis_en")
        elem.send_keys("MIDAS - mining areas (shp)")
        elem = driver.find_element_by_name("btnZatwierdz")
        elem.send_keys(Keys.RETURN)
        DMlayers.append(filename)
        
    if "tereny" in filename:
        elem = driver.find_element_by_name("iptOpis")
        elem.send_keys(u'MIDAS - tereny górnicze (shp)')
        elem = driver.find_element_by_name("iptOpis_en")
        elem.send_keys("MIDAS - mining countries (shp)")
        elem = driver.find_element_by_name("btnZatwierdz")
        elem.send_keys(Keys.RETURN)
        DMlayers.append(filename)
        
    if "otwory_badania" in filename:
        elem = driver.find_element_by_name("iptOpis")
        elem.send_keys(u'Otwory wiertnicze z wynikami badań w CBDG (shp)')
        elem = driver.find_element_by_name("iptOpis_en")
        elem.send_keys("Boreholes - well-log data in CBDG (shp)")
        elem = driver.find_element_by_name("btnZatwierdz")
        elem.send_keys(Keys.RETURN)
        DMlayers.append(filename)
        
    if "otwory_2" in filename:
        elem = driver.find_element_by_name("iptOpis")
        elem.send_keys(u'Otwory wiertnicze (shp)')
        elem = driver.find_element_by_name("iptOpis_en")
        elem.send_keys("Boreholes (shp)")
        elem = driver.find_element_by_name("btnZatwierdz")
        elem.send_keys(Keys.RETURN)
        DMlayers.append(filename)
        
    if "jaskinie" in filename:
        elem = driver.find_element_by_name("iptOpis")
        elem.send_keys(u'Środowisko - jaskinie (shp)')
        elem = driver.find_element_by_name("iptOpis_en")
        elem.send_keys("Environment - caves (shp)")
        elem = driver.find_element_by_name("btnZatwierdz")
        elem.send_keys(Keys.RETURN)
        DMlayers.append(filename)
        

# skrypt bedzie lecial dopoki do tablicy nie dodadza sie wszystkie warstwy (zabezpieczenie przed wylogowywaniem przez konsole)
while len(DMlayers) != 6:
    try:
        fillNames()
    except: pass

driver.close()

print DMlayers
print len(DMlayers)
