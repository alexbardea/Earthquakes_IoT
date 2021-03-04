# Alex Bardea - Earthquakes IoT data Project
#
# Local software & Graph representation- Python
# Dedicated IoT platform - AWS IoT
# Notifications via SMS
# JSON Format of Exporting data
#
#   Connect to a site which generates IoT data. This data will be
# saved both locally (JSON) and online (AWS), on a dedicated IoT platform, and will be
# represented graphically. If the value of a monitored parameter exceeds a certain
# threshold (magnitude larger than 4.5), a notification will be sent to the user from
# a specific area.


import urllib.request
import json
import time
import webbrowser
from datetime import datetime
import os
import folium
import pandas as pd
import requests
from twilio.rest import Client
import numpy as np
import matplotlib.pyplot as plt


#SID_ACC = 'AC0f5fd917aec64b271fe133daeb5e2b8a'
#TOKEN_ACC = '52f96820d0d24fc2e74b418ff178c052'
#PATH_CERT = os.path.abspath(r"C:\Users\Alex's PC\Desktop\certs\34316a7d1b-certificate.pem.crt")
#PATH_KEY = os.path.abspath(r"C:\Users\Alex's PC\Desktop\certs\34316a7d1b-private.pem.key")
#ENDPOINT = 'a3frs8pwmyzazn-ats.iot.eu-west-3.amazonaws.com'
#TOPIC = 'topic_test_win'

#send the information to the AWS IOT Core
def send_iot(msg):
    #certificate
    PATH_CERT = os.path.abspath(r"C:\Users\Alex's PC\Desktop\certs\34316a7d1b-certificate.pem.crt")
    #private key
    PATH_KEY = os.path.abspath(r"C:\Users\Alex's PC\Desktop\certs\34316a7d1b-private.pem.key")
    #Endpoint of the IOT
    ENDPOINT = 'a3frs8pwmyzazn-ats.iot.eu-west-3.amazonaws.com'
    #Name of the topic on which we subscribe on AWS IOT
    TOPIC = 'earthquake_topic'
    #the URL to which the information is send to AWS IOT
    publish_url = 'https://' + ENDPOINT + ':8443/topics/' + TOPIC + '?qos=1'
    #the string which is send to the topic, incoded in UTF-8 format
    publish_msg = msg.encode('utf-8')
    #makes a POST request in order to
    requests.request('POST', publish_url, data=publish_msg, cert=[PATH_CERT, PATH_KEY])

#send SMS to the subscribers according to their location using TWILLIO
def send_sms(details):
    #array of subscribers with their corresponding location
    nb_list = ['+4074217668', 'Philippines', '+40741177161', 'Alaska', '+40757020125', 'Chile']
    #number from which the SMS is send (trial number from TWILLIO)
    from_nb = "+12513256747"
    #SID and Token for our TWILLIO account
    SID_ACC = 'ACcd677c9c6f8aff5083979e1e14b7c257'
    TOKEN_ACC = 'b7bb8be740fd7d795e509e5b78b121a2'
    #time_hr = datetime.fromtimestamp(int(tmp) / 1000).strftime("%Y-%m-%d %H:%M:%S")
    #details = "mag: " + str(mag) + "| place: " + loc + "| time: " + time_hr

    #location of the earthquacke filtered from all of the details
    loc = details.split('|')[1].split(',')[-1].split(': ')[-1].strip()

    #check if the location of the earthquack mathes a subscrierbs location and send the SMS
    if(loc in nb_list):
        #get the nb of the right subscriber
        phone_bo = nb_list.index(loc) - 1
        #print(phone_bo)

        #open the connection to Twillio, and send the SMS with all the details
        client = Client(SID_ACC, TOKEN_ACC)
        client.api.account.messages.create(
            to = nb_list[phone_bo],
            from_ = from_nb,
            body = "WARNING! Earthquake!\n" + details)
    #print(details)

#function the create the Map to display the location
def map_graph():
    #arrays needed to the Map
    lon = []
    lat = []
    mag = []
    loc = []

    #the URL from which we get the JSON data with the Earthqukes from the last week with mag larger than 4.5
    url_map = urllib.request.urlopen("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_week.geojson")
    data_map = requests.get('https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_week.geojson').json()


    #write the JSON data to a file
    with open('data_map.json', 'w') as f:
        json.dump(data_map, f)

    #decode the information to be able to use it in our script
    data_map = json.loads(url_map.read().decode())

    for elem in data_map['features']:
        lat.append(elem['geometry']['coordinates'][0])
        lon.append(elem['geometry']['coordinates'][1])
        mag.append(elem['properties']['mag'])
        loc.append(elem['properties']['place'] + "\nMag: " + str(elem['properties']['mag']))


    data = pd.DataFrame({
       'lat': lat,
       'lon': lon,
       'name': loc,
       'value': mag
    })
    data

    #m = folium.Map(location=[20, 0], zoom_start=3.5)
    m = folium.Map(location=[48.85, 2.35], tiles="OpenStreetMap", zoom_start=2)

    for i in range(0, len(data)):
        folium.Circle(
            location=[data.iloc[i]['lon'], data.iloc[i]['lat']],
            popup=data.iloc[i]['name'],
            radius=data.iloc[i]['value'] * 10000,
            color='crimson',
            fill=True,
            fill_color='crimson'
        ).add_to(m)

    # Save it as html
    m.save('Earthquake_last_month.html')
    # Open the HTML file in the browser
    webbrowser.open('file://' + os.path.realpath('Earthquake_last_month.html'))

#function for displaying the bar graph in order to disply the nb of Earthqukes in varios locations
def bar_graph():
    #location for which we display the information
    location = ('Philippines', 'Alaska', 'Chile')
    #reset the counter
    nb = [0, 0, 0]

    #the URL from which we get the JSON data with the Earthqukes from the last month with mag >= 4.5
    url_bar = urllib.request.urlopen("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_month.geojson")
    data_bar = requests.get('https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_month.geojson').json()

    #wirte to a file the JSON info
    with open('data_map.json', 'w') as f:
        json.dump(data_bar, f)

    data_map = json.loads(url_bar.read().decode())

    #go through all the Erathqukes
    for elem in data_map['features']:
        loc = elem['properties']['place'].split(',')[-1].split(': ')[-1].strip()
        #check the location and increase the counter

        if (loc in location):
            nb[location.index(loc)] += 1

    #configure the bar graph
    y_pos = np.arange(len(location))
    #plt.figure(num=None, figsize=(8, 6), dpi=80)
    plt.title('Number of Earthquakes in the last 30 days')
    plt.xlabel('Number of Earthquakes')
    plt.ylabel('Location')
    plt.barh(y_pos, nb)
    plt.yticks(y_pos, location)
    plt.figure()
    plt.show(block=False)

#display the data real time
def real_time():
    LAST_TMP = 0
    EQ_ID = 0
    #read the JSON file in every minute in order to keep the app up-to-date
    while 1:
        url_real_t = urllib.request.urlopen("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson")
        data_live = requests.get('https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson').json()

        #write the data in a file
        with open('data_live.json', 'w') as f:
            json.dump(data_live, f)

        data_real_t = json.loads(url_real_t.read().decode())
        magnitudes_real_t = []
        tmp_real_t = []
        hr_real_t = []

        #go through all the Earthqukes
        for elem in data_real_t['features']:
            #append the data in the right arrays
            magnitudes_real_t.append(elem['properties']['mag'])
            tmp_real_t.append(elem['properties']['time'])

            #format the data from Timestamp to HR
            #time_hr = datetime.fromtimestamp(int(elem['properties']['time']) / 1000).strftime("%Y-%m-%d %H:%M:%S")
            time_hr = datetime.fromtimestamp(int(elem['properties']['time']) / 1000).strftime("%H:%M:%S")
            hr_real_t.append(time_hr)

            #format the string containing all the neccessary information for the app
            details = "mag: " + str(elem['properties']['mag']) + "| place: " + elem['properties'][
                'place'] + "| time: " + time_hr

            TH = 0
            #Check if the Earthquke has a magnitude greater than a Treashold and if it's the last one
            if elem['properties']['mag'] >= TH and elem['properties']['time'] > LAST_TMP:
                send_sms(details)

            #trigger the function which sends the info the the IOT
            if elem['properties']['time'] > LAST_TMP:
               send_iot(str(EQ_ID) + ": " + details)
               EQ_ID += 1

        #trigger the function which shows the graph with the magnitudes
        mag_plot()

        LAST_TMP = max(tmp_real_t)
        time.sleep(60)

#function which shows the graph with the magnitudes
def mag_plot():
        #open the JSON file with the Earthqukes in the last day
        url_day = urllib.request.urlopen("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson")
        data_day = json.loads(url_day.read().decode())
        data_day = requests.get('https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson').json()

        #write the data in a file
        with open('data_7days.json', 'w') as f:
            json.dump(data_day, f)

        hr_day = []
        tmp_day = []
        magnitudes_day = []

        #past all the earthquakes
        for elem in data_day['features']:
            magnitudes_day.append(elem['properties']['mag'])
            tmp_day.append(elem['properties']['time'])

            #time_hr = datetime.fromtimestamp(int(elem['properties']['time']) / 1000).strftime("%Y-%m-%d %H:%M:%S")
            time_hr = datetime.fromtimestamp(int(elem['properties']['time']) / 1000).strftime("%H:%M:%S")
            hr_day.append(time_hr)

        hr_day.reverse()
        magnitudes_day.reverse()
        #configure and open the graph
        #print(magnitudes_day)
        plt .title('Magnitudes of Earthquakes today')
        plt.xlabel('Time')
        plt.ylabel('Magnitude')
        plt.stem(hr_day, magnitudes_day)
        (markerline, stemlines, baseline) = plt.stem(hr_day, magnitudes_day)
        plt.setp(baseline, visible=False)
        plt.show()

        #plt .title('Magnitudes of Earthquakes today')
        #plt.xlabel('Time')
        #plt.ylabel('Magnitude')
        #plt.plot(hr_day, magnitudes_day)
        #plt.show()

def main():
    map_graph()
    bar_graph()
    real_time()

if __name__ == "__main__":
    main()
