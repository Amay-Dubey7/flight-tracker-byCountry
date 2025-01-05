# Flight Tracker Application

## Overview

The **Flight Tracker Application** is a Flask-based web application that allows users to fetch and display real-time flight data for a specific airport. It uses the FlightAPI.io service to retrieve flight schedules, processes the data to count flights by country, and provides an easy-to-use interface for inputting airport codes.

## Features

* **Fetch Real-Time Flight Data**: Query flight arrivals for any airport using a valid IATA airport code.
* **Data Processing**: Aggregates flight data and displays the number of flights grouped by the originating country.
* **Error Handling**: Logs errors and saves API responses (both success and failure) for debugging.
* **Simple Web Interface**: Input airport codes and view results via a browser.
* **Logging**: Maintains logs for debugging and tracking API usage.

## Requirements

### Software
* Python 3.8 or higher
* Flask 2.x
* Required Python libraries:
    * `requests`
    * `collections`
    * `logging`
    * `json`
    * `datetime`

### API Key
The application uses **FlightAPI.io** to fetch flight data. You need an API key, which is configured in the code as `API_KEY`.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-repo/flight-tracker.git
cd flight-tracker
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
    * Update the `API_KEY` in the code or configure it as an environment variable:
```bash
export FLIGHT_API_KEY="your_api_key_here"
```

5. Ensure you have the `logs` directory for saving API responses:
```bash
mkdir logs
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Open a web browser and navigate to:
```
http://127.0.0.1:5000/
```

3. Enter a valid 3-character IATA airport code (e.g., `JFK`, `LAX`) and click "Submit" to view flight data.

## File Structure

```
flight-tracker/
├── app.py              # Main Flask application
├── templates/
│   └── index.html     # HTML template for the web interface
├── logs/              # Directory for saving API responses
├── app.log            # Application log file
└── requirements.txt   # Python dependencies
```

## Key Functions

1. `get_flight_data(airport_code)`
    * Fetches flight arrival data from FlightAPI.io for the given airport code.
    * Saves API responses to the `logs/` directory.
    * Handles API errors and logs any issues.

2. `process_flight_data(data)`
    * Processes the raw flight data to count the number of flights by country.
    * Returns a sorted list of countries with flight counts.

3. `save_response_to_file(data, airport_code)`
    * Saves API responses (success or error) to timestamped JSON files in the `logs/` directory.

## Logging

* Logs are stored in `app.log` with detailed messages for debugging.
* Example log entries:
```
2025-01-05 12:00:00 - DEBUG - Fetching data for airport: JFK
2025-01-05 12:00:02 - INFO - Response saved to: logs/response_JFK_20250105_120002.json
```

## Configuration

* **API Key**: Replace the placeholder in `API_KEY` with your FlightAPI.io key.
* **Host and Port**: Configurable in the `app.run()` call:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

## Troubleshooting

* **Invalid Airport Code**: Ensure the input is a 3-character IATA airport code (e.g., `JFK`).
* **No Flights Found**: If no data is returned, check the availability of flight schedules for the airport.
* **API Key Errors**: Verify your API key and its usage limits on FlightAPI.io.

## Future Enhancements

* Add support for departure schedules
* Provide filtering options (e.g., by airline or flight type)
* Implement user authentication for API usage tracking

## License

This project is licensed under the MIT License. See `LICENSE` for more details.
