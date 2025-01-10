from flask import Flask, render_template, request
from openai import OpenAI
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from db import Flight, Base

# Initialize Flask app
app = Flask(__name__)

# Set up logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, 
                   format='%(asctime)s - %(levelname)s - %(message)s')

# Create database connection
engine = create_engine("sqlite:///flights.db")
Session = sessionmaker(bind=engine)

# Initialize OpenAI API Key
# client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
client = OpenAI(api_key = 'sk-svcacct-Hf761fHpn1N9kra1QJTyYeSFFrGe0rat--Qn96ZcOImjeU65CBuhunpe1v7oZG0Q7NJGYwhhjBcPT3BlbkFJpWAuRN4N4uAwJRhLqYDevJi7_HAGWgMlo2jYfFtionksPGAaA64UyPlASQPWTWXC0V6l9xuGrZcA')


def get_unique_airports():
    """
    Get list of unique airport codes from the database.
    """
    session = Session()
    try:
        airports = session.query(Flight.destination_airport)\
                         .distinct()\
                         .order_by(Flight.destination_airport)\
                         .all()
        return [airport[0] for airport in airports]
    finally:
        session.close()

def generate_sql_query(question, airport_code):
    """
    Use LLM to generate appropriate SQL query based on the question.
    """
    # Country code to full name mapping
    country_mapping = {
        "US": "United States",
        "UK": "United Kingdom",
        "UAE": "United Arab Emirates",
        "SG": "Singapore",
        "HK": "Hong Kong",
        "NL": "Netherlands"
    }
    
    # Replace country codes with full names in the question
    modified_question = question
    for code, country in country_mapping.items():
        modified_question = modified_question.replace(code, country)

    prompt = f"""
    Given the following SQLite database table structure:
    Table name: flights
    Database: flights.db
    Columns:
    - destination_airport (String): Airport code for destination
    - src_airline_code (String): Airline code
    - src_country (String): Full country name of origin
    - src_city (String): City of origin
    - src_identification_codeshare (String): Codeshare identification
    - flight_number (String): Flight number
    - arrived_late (String): '1' or '0' indicating if flight arrived late
    - estimated_late (String): '1' or '0' indicating if flight was estimated to be late

    The user is asking about airport: {airport_code}
    Question: {modified_question}

    Generate a SQL query to answer this question. The query should:
    1. Always include WHERE destination_airport = '{airport_code}'
    2. Be specific to the question asked
    3. Use appropriate aggregations (COUNT, AVG, SUM) when needed
    4. Use proper grouping when aggregating
    5. Include CASE statements for Yes/No counting if needed
    6. Be a valid SQLite query
    7. Use proper string comparisons for 'Yes'/'No' fields
    
    Return only the SQL query without any explanation or comments.
    """

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are a SQL query generator. Return only the SQL query without any explanation, comments, or markdown formatting."},
                      {"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=500
        )
        query = completion.choices[0].message.content.strip()
        print(query)
        
        # Ensure that no unwanted characters are in the query
        query = query.replace("```sql", "").replace("```", "")
        return query
    except Exception as e:
        logging.error(f"Error generating SQL query: {str(e)}")
        return None

def execute_sql_query(sql_query):
    """
    Execute the generated SQL query and return results.
    """
    session = Session()
    try:
        print(f"Executing SQL query: {sql_query}")  # Debugging statement
        result = session.execute(text(sql_query))  # Using the correct execution method
        columns = result.keys()
        data = [dict(zip(columns, row)) for row in result]
        return data
    except Exception as e:
        logging.error(f"Error executing SQL query: {str(e)}")
        print(f"Error executing SQL query: {str(e)}")  # Debugging statement
        return None
    finally:
        session.close()


def format_sql_results(results, question):
    """
    Use LLM to format SQL results into a natural language response.
    """
    prompt = f"""
    Question: {question}
    SQL Results: {results}
    
    Please provide a clear, natural language response based on these SQL query results.
    Focus on directly answering the question while including specific numbers and facts from the data.
    If the results are empty, indicate that no data was found.
    """

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a data interpreter. Provide clear, concise answers based on SQL query results and beautify the results.Do not write things like according to SQL results. Answer in human like way."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Error formatting results: {str(e)}")
        return "Sorry, there was an error processing the results."

@app.route('/', methods=['GET', 'POST'])
def index():
    answer = None
    error = None
    selected_airport = None
    airports = get_unique_airports()

    if request.method == 'POST':
        selected_airport = request.form.get('airport_code')
        question = request.form.get('question', '').strip()

        if not selected_airport or selected_airport not in airports:
            error = "Please select a valid airport."
        elif not question:
            error = "Please enter a question."
        else:
            # Generate and execute SQL query
            sql_query = generate_sql_query(question, selected_airport)
            print('SQL query is :', sql_query)
            if sql_query:
                results = execute_sql_query(sql_query)
                print(results)
                if results is not None:
                    answer = format_sql_results(results, question)
                else:
                    error = "Error executing the query."
            else:
                error = "Error generating the query."

    return render_template('index.html', 
                         airports=airports,
                         selected_airport=selected_airport,
                         answer=answer,
                         error=error)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)