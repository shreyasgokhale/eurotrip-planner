# EuroTrip Planner

Eurotrip planner is a Python script for planning the cheapest (euro)trip using SkyScanner API. 

For more info, have a look at The EuroTrip Planner Blog:
[Part 1](https://shreyasgokhale.com/tech-blog/eurotrip-planner-part-1/) and [Part 2](https://shreyasgokhale.com/tech-blog/eurotrip-planner-part-2/)

## Requirements

- Python3
- Docker

## Usage
First install all the requirements:

```pip3 install -r requirements.txt```


If docker is already installed, run following command to start a MongoDB server locally on default port

```docker run --name eurotrip-planner-mongo -d mongo:latest```

Then, edit first 5 variables in ```planner.py``` as according to your proposed trip and then run

``` python3 planner.py``` 

> #### Note: You will require a RapidAPI licence key. Please don't abuse mine :-)

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[GPL](https://choosealicense.com/licenses/gpl-3.0/)
