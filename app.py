from flask import Flask, render_template, request
import requests
from collections import defaultdict
import os
import json
import logging
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Set up logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Load API key from environment variable
API_KEY = "677ac88f3a45b414acd274ed"

# Ensure logs directory exists
if not os.path.exists('logs'):
    os.makedirs('logs')

def save_response_to_file(data, airport_code):
    """
    Save API response to a JSON file with timestamp
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'logs/response_{airport_code}_{timestamp}.json'
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logging.info(f"Response saved to: {filename}")
        return filename
    except Exception as e:
        logging.error(f"Error saving response: {str(e)}")
        return None

def get_flight_data(airport_code):
    """
    Fetch flight data from FlightAPI.io for a specific airport
    """
    url = f'https://api.flightapi.io/schedule/{API_KEY}?mode=arrivals&iata={airport_code}&day=1'
    
    logging.debug(f"Attempting to fetch data from: {url}")
    
    try:
        response = requests.get(url)
        logging.debug(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            saved_file = save_response_to_file(data, airport_code)
            if saved_file:
                logging.info(f"Response data saved to {saved_file}")
            return data
        else:
            error_data = {
                'status_code': response.status_code,
                'error': response.text
            }
            save_response_to_file(error_data, f"{airport_code}_error")
            logging.error(f"Error response: {response.text}")
            return None
    except Exception as e:
        logging.error(f"Error fetching data: {str(e)}")
        return None

def process_flight_data(data):
    """
    Process the flight data to get country-wise flight counts
    """
    country_flights = defaultdict(int)
    
    try:
        arrivals = data.get('airport', {}).get('pluginData', {}).get('schedule', {}).get('arrivals', {}).get('data', [])
        
        for flight_data in arrivals:
            country = flight_data.get('flight', {}).get('airport', {}).get('origin', {}).get('position', {}).get('country', {}).get('name')
            if country:
                country_flights[country] += 1
        
        result = [{'country': country, 'flights': count} for country, count in country_flights.items()]
        
        return sorted(result, key=lambda x: x['flights'], reverse=True)
        
    except Exception as e:
        logging.error(f"Error processing flight data: {str(e)}")
        logging.debug(f"Data structure: {json.dumps(data, indent=2)[:500]}")
        return []

@app.route('/', methods=['GET', 'POST'])
def index():
    flight_data = None
    error = None
    airport_code = ''
    
    if request.method == 'POST':
        airport_code = request.form.get('airport_code', '').upper()
        
        if len(airport_code) != 3:
            error = "Please enter a valid 3-character airport code"
        else:
            logging.debug(f"Fetching data for airport: {airport_code}")
            raw_data = get_flight_data(airport_code)
            
            if raw_data:
                logging.debug("Successfully got raw data")
                flight_data = process_flight_data(raw_data)
                if not flight_data:
                    error = "No flights found for this airport"
            else:
                error = "Unable to fetch flight data. Please try again later."
    
    return render_template('index.html', 
                         flight_data=flight_data, 
                         error=error, 
                         airport_code=airport_code)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
