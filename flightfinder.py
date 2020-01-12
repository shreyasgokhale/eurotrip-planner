import requests, datetime, json

class finder:
    
    def __init__(self, originCountry = "DE", currency = "EUR", locale = "en-US", rootURL="https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com"):
        self.currency = currency
        self.locale =  locale
        self.rootURL = rootURL
        self.originCountry = originCountry
        self.airports = {}
        self.quotes = []
        self.places = []
        self.carriers = []

    def setHeaders(self, headers):
        self.headers =  headers
        self.createSession()

    def createSession(self):
        self.session = requests.Session() 
        self.session.headers.update(self.headers)
        return self.session
        
    def browseQuotes(self, source, destination, date, print = False):
        quoteRequestPath = "/apiservices/browsequotes/v1.0/"
        browseQuotesURL = self.rootURL + quoteRequestPath + self.originCountry + "/" + self.currency + "/" + self.locale + "/" + source + "/" + destination + "/" + date.strftime("%Y-%m-%d")
        response = self.session.get(browseQuotesURL)
        #response = requests.request("GET", url = browseQuotesURL, headers = self.headers)
        resultJSON = json.loads(response.text)
        if("Quotes" in resultJSON):
            self.quotes.append(resultJSON["Quotes"])    
            for Places in resultJSON["Places"]:
            # Add the airport in the dictionary.
                self.airports[Places["PlaceId"]] = Places["Name"] 
            if(print):
                self.printResult(resultJSON,date)
   
    def printResult(self, resultJSON,date):
        for Quotes in resultJSON["Quotes"]:
            source = Quotes["OutboundLeg"]["OriginId"]
            dest = Quotes["OutboundLeg"]["DestinationId"]
            # print("%s --> to  -->%s" %(origin,destination))
            # Look for Airports in the dictionary                
            print(date.strftime("%d-%b %a") + " | " + "%s  --> %s"%(self.airports[source],self.airports[dest]) + " | " + "%s EUR" %Quotes["MinPrice"])

    def getQuotes(self):
        return self.quotes
    
    def getAirports(self):
        return self.airports