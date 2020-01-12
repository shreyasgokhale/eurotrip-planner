import requests
import json
import timeit
import time
import datetime
import dateutil
import calendar
import pandas as pd
import wrapymongo
import concurrent.futures
import threading

import flightfinder as ff

## USER Input

# All dates are YYYY-DD-MM
source_begin_date = "2020-01-18" # The begining of your outwards journy
source_end_date = "2020-01-24" # The end of your outwards journy
destination_begin_date = "2020-01-24" # The begining of your inwards journy
destination_end_date = "2020-01-30" # The end of your inwards journy
source_array = {"BERL-sky"} # Airports you want to fly from
destination_array = {"MAD-sky", "BCN-sky", "SVQ-sky", "VLC-sky"} # Airports that you want to fly into
rapidapi_key = "ae922034c6mshbd47a2c270cbe96p127c54jsnfec4819a7799" # Your RapidAPI key


headers = {
    'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
    'x-rapidapi-key': rapidapi_key
}

rootURL = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com"
originCountry = "DE"
currancy = "EUR"
locale = "en-US"


airports = {}
daterange_source = pd.date_range(source_begin_date, source_end_date)
daterange_destination = pd.date_range(
    destination_begin_date, destination_end_date)


# Function to make MongoDBAPI object
def makeObject(link, dbName="SkyScanner", dbCollection="test"):
    mdbobject = wrapymongo.driver(link)
    mdbobject.defineDB(dbName)
    mdbobject.defineCollection(dbCollection)
    return mdbobject


# authdb = "admin"
monogdbport = "27017"
host = "localhost"
link = "mongodb://" + host + ":" + monogdbport
database = "SkyScanner"
outgoingTable = "Outgoing"
incomingTable = "Incoming"
placesTable = "Places"
mdbOutgoing = makeObject(link, dbName=database, dbCollection=outgoingTable)
mdbPlaces = makeObject(link, dbName=database, dbCollection=placesTable)
mdbIncoming = makeObject(link, dbName=database, dbCollection=incomingTable)

mdbOutgoing.dropCollection()
mdbPlaces.dropCollection()
mdbIncoming.dropCollection()

airports = {}

outgoing_flight_finder = ff.finder()
outgoing_flight_finder.setHeaders(headers)


incoming_flight_finder = ff.finder()
incoming_flight_finder.setHeaders(headers)


processing_start = time.time()

with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
    for single_date in daterange_source:
        for destination in destination_array:
            for source in source_array:
                request_start = time.time()
                executor.submit(outgoing_flight_finder.browseQuotes,
                                source, destination, single_date)

outgoingQuotes = outgoing_flight_finder.getQuotes()


for quote in outgoingQuotes:
    mdbOutgoing.insertRecords(quote)

airports.update(outgoing_flight_finder.getAirports())

# We reverse the arrays here
with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
    for single_date in daterange_destination:
        for destination in source_array:
            for source in destination_array:
                request_start = time.time()
                executor.submit(incoming_flight_finder.browseQuotes,
                                source, destination, single_date)

incomingQuotes = incoming_flight_finder.getQuotes()

for quote in incomingQuotes:
    mdbIncoming.insertRecords(quote)

airports.update(incoming_flight_finder.getAirports())


# Sort both dbs by cheapest 30 flights. In total, our code will compute for 900 flight combinations
cheapestOutgoingFlights = {}
cheapestOutgoingFlights = mdbOutgoing.sortRecords([('MinPrice', 1)], 30)

cheapestIncomingFlights = {}
cheapestIncomingFlights = mdbIncoming.sortRecords([('MinPrice', 1)], 30)

finalListElement = {}
finalList = []

for incomingQuotes in cheapestIncomingFlights:
    for outgoingQuotes in cheapestOutgoingFlights:
        finalListElement = {}
        finalListElement["TotalPrice"] = incomingQuotes["MinPrice"] + \
            outgoingQuotes["MinPrice"]
        finalListElement["TakeOff1"] = airports[outgoingQuotes["OutboundLeg"]["OriginId"]]
        finalListElement["Land1"] = airports[outgoingQuotes["OutboundLeg"]
                                             ["DestinationId"]]
        finalListElement["TakeOff2"] = airports[incomingQuotes["OutboundLeg"]["OriginId"]]
        finalListElement["Land2"] = airports[incomingQuotes["OutboundLeg"]
                                             ["DestinationId"]]
        finalListElement["Date1"] = outgoingQuotes["OutboundLeg"]["DepartureDate"]
        finalListElement["Date2"] = incomingQuotes["OutboundLeg"]["DepartureDate"]
        finalList.append(finalListElement)

mdbFinal = makeObject(link, dbName=database, dbCollection="FinalDatabase")
mdbFinal.dropCollection()
mdbFinal.insertRecords(finalList)

print("The Top ten cheapest flights are:")
topQuotes = mdbFinal.sortRecords([('TotalPrice', 1)], 10)
for quote in topQuotes:
    print("\n*****\nOnwards: " + quote["Date1"] + " " + quote["TakeOff1"] + " --> " + quote["Land1"] + " \nReturn: " +
          quote["Date2"] + " " + quote["TakeOff2"] + " --> " + quote["Land2"] + " \n \t   | " + "%s EUR" % quote["TotalPrice"])


print("\nBenchmark Stats :")
print("Time spent in program: %f seconds" % (time.time()-processing_start))
