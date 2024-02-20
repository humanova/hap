import google.generativeai as genai
from pprint import pprint
import requests
import json
import yaml

with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

genai.configure(api_key=config['gemini-api-key'])
model = genai.GenerativeModel('gemini-pro')

prompt = """You are a multilingual news intelligence assistant designed to provide concise summaries of relevant news articles from a business and security perspective, using English for output.
-Analyze news articles through a lens relevant to business operations and security concerns, identifying key information and potential risks or opportunities.
-Generate summaries that are clear, informative, and to the point, avoiding excessive verbosity or irrelevant details.
-Assign severity scores using integers (1-5) to each news item based on its potential impact on businesses and their security postures, with 1 being minimal impact and 5 being critical.
-Extract and process location information (city/district) from news articles where available, making summaries location-specific and enhancing their value.
-If the district or city information isn't avaliable then use "None".
-Respond with JSON using this schema : {"location" : {"country": <COUNTRY> , "city": <CITY>, "district": <DISTRICT>} , "event_summary":  <SUMMARY>, "severity_business": <SEVERITY_BUSINESS>, "severity_security": <SEVERITY_SECURITY>}
News : """

news_text = """Eskişehir'in Tepebaşı ve Seyitgazi ilçelerinde 2 heykel ve haç figürü ile 32 sikke ele geçirilen tarihi eser operasyonlarında 2 şüpheli yakalandı. """


def get_coordinates(city:str, district:str, country:str, polygon=1, addressdetails=1) -> tuple:
    """
    Sends a GET request to the Nominatim OpenStreetMap API and returns the lat/lon in a tuple.
    """
    location_text = f"{city} {country}"
    if district != "None" and isinstance(district, str):
        location_text = f"{district} {location_text}"

    url = f"https://nominatim.openstreetmap.org/search?q={location_text}&format=json&polygon={polygon}&addressdetails={addressdetails}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            place = response.json()[0]
            return (place['lat'], place['lon'])
        else:
            print(f"Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error finding the coordinates: {e}")
        return None
    
    
def summarize_news(news_text: str):
    final_prompt = f"{prompt} {news_text}"
    response = model.generate_content(final_prompt, generation_config={"temperature": 0.7})
    return json.loads(response.text)


if __name__ == "__main__":
    summarization = summarize_news(news_text)
    loc = summarization['location']
    coordinates = get_coordinates(city=loc['city'], district=loc['district'], country=loc['country'])
    print(f"LOCATION = {loc['city']} - {loc['district']} -> {coordinates}")
    pprint(summarization)
