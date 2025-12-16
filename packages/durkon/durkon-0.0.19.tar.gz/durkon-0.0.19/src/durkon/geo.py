import pandas as pd
import numpy as np
import math

centralLondon = ["E", "EC", "N", "NW", "SE", "SW", "W", "WC"]
greaterLondon = ["BR", "CM", "CR", "DA", "EN", "HA", "IG", "KT", "RM", "SM", "UB", "WD", "TN", "TW"]
otherMajorCity = ["B","LS","G","M", "S","BD","EH","L","BS", "CF", "LE","CV","WF", "NG", "NE","DN","MK","SR","BN","WV", "HU","PL","DE","ST", "SU", "SA","AB","PE","PO", "YO"] #Major here means >200k residents in the city part of the city
nIreland = ["BT"]
islands = ["IM","JE","GY"]#,"FI"]

def extract_postcode_area(postcodeCol):
    return postcodeCol.str.extract(r'^([A-Z]{1,2})\d')

def easy_geo(areaCol):
 geoCat = pd.Series(["Elsewhere"]*len(areaCol))
 geoCat[areaCol.isin(centralLondon)] = "Central London"
 geoCat[areaCol.isin(greaterLondon)] = "Greater London"
 geoCat[areaCol.isin(otherMajorCity)] = "Other Major City"
 geoCat[areaCol.isin(nIreland)] = "Northern Ireland"
 geoCat[areaCol.isin(islands)] = "Isles"
 return geoCat

if __name__ == '__main__':
 df=pd.DataFrame({"Rowno":[0,1,2,3,4,5], "PostCode":["HP21 6AA", "WA7 9ME",None,"Not actually a postcode", "BT12 1EE", "EC44EC"]})
 df["Area"] = extract_postcode_area(df["PostCode"])
 df["Geo"] = easy_geo(df["Area"])
 print(df)
