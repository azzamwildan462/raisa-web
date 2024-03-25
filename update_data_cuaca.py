import requests
import xml.etree.ElementTree as ET
import xml.dom.minidom
import os

CONFIG_daerah = "Jember"

dts_humidity = ""
dts_temperatur = ""
dts_weather = ""
dts_wind = ""


def parse_kode_cuaca(kode):
    ret = ""

    # Dictionary mapping integer codes to weather descriptions
    weather_map = {
        0: "Cerah",
        1: "Cerah Berawan",
        2: "Cerah Berawan",
        3: "Berawan",
        4: "Berawan Tebal",
        5: "Udara Kabur",
        10: "Asap",
        45: "Kabut",
        60: "Hujan Ringan",
        61: "Hujan Sedang",
        63: "Hujan Lebat",
        80: "Hujan Lokal",
        95: "Hujan Petir",
        97: "Hujan Petir"
    }

    # Lookup the weather description based on the code
    if kode in weather_map:
        ret = weather_map[kode]

    return ret


# URL of the XML data
url = 'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-JawaTimur.xml'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
'Content-Type': 'application/xml'}

# Perform the HTTP GET request
response = requests.get(url,headers=headers)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the XML content
    xml_content = response.content
    xml_string = xml_content.decode('utf-8')

    doc = xml.dom.minidom.parseString(xml_string)

    root = doc.documentElement

    areas = root.getElementsByTagName('area')

    for area in areas:
        if area.getAttribute('description') == CONFIG_daerah:
            parameters = area.getElementsByTagName('parameter')
            for parameter in parameters:
                if parameter.getAttribute('id') == "hu" or parameter.getAttribute('id') == "t" or parameter.getAttribute('id') == "weather" or parameter.getAttribute('id') == "ws":
                    timerange = parameter.getElementsByTagName('timerange')
                    for timer in timerange:
                        if timer.getAttribute('h') == "0":
                            if parameter.getAttribute('id') == "hu":
                                dts_humidity = timer.getElementsByTagName('value')[0].firstChild.data + "%"
                            elif parameter.getAttribute('id') == "t":
                                dts_temperatur = timer.getElementsByTagName('value')[0].firstChild.data + "  C"
                            elif parameter.getAttribute('id') == "weather":
                                dts_weather = timer.getElementsByTagName('value')[0].firstChild.data
                                dts_weather = parse_kode_cuaca(int(dts_weather))
                            elif parameter.getAttribute('id') == "ws":
                                dts_wind = timer.getElementsByTagName('value')[0].firstChild.data + "km/h"
            break
    
    # Save to json file 
    with open(os.environ.get('UI_ASSETS') + '/misc/data_cuaca.json', 'w') as file:
        file.write(f'{{"kelembapan": "{dts_humidity}", "suhu": "{dts_temperatur}", "cuaca": "{dts_weather}", "kecepatan_angin": "{dts_wind}"}}')
        
else:
    print(f"Failed to retrieve data: {response.status_code} - {response.reason}")
