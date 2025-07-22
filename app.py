from flask import Flask, request, jsonify, send_from_directory
import requests
import os

app = Flask(__name__, static_folder='static')

# This route handles POST requests from Dialogflow
@app.route('/', methods=['POST'])
def index():
    data = request.get_json()
    try:
        source_currency = data['queryResult']['parameters']['unit-currency']['currency']
        amount = data['queryResult']['parameters']['unit-currency']['amount']
        target_currency = data['queryResult']['parameters']['currency-name']

        # Fetch the conversion factor
        conversion_rate = fetch_conversion_factor(source_currency, target_currency)

        if conversion_rate is None:
            return jsonify({"fulfillmentText": "Sorry, I couldn't fetch the exchange rate right now."})

        converted_amount = amount * conversion_rate
        response_text = f"{amount} {source_currency} is approximately {converted_amount:.2f} {target_currency}."
        return jsonify({"fulfillmentText": response_text})

    except Exception as e:
        print("Error:", e)
        return jsonify({"fulfillmentText": "Something went wrong. Please try again."})

# This function fetches the exchange rate using the public API
def fetch_conversion_factor(source_currency, target_currency):
    url = f"https://v6.exchangerate-api.com/v6/3a45bb2dd98bbc188b86fc0e/latest/{source_currency}"
    try:
        response = requests.get(url)
        data = response.json()
        if 'conversion_rates' in data and target_currency in data['conversion_rates']:
            return data['conversion_rates'][target_currency]
        else:
            return None
    except Exception as e:
        print("API Error:", e)
        return None

# Serve the chatbot HTML file
@app.route('/', methods=['GET'])
def home():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    # Use PORT from env or 10000 as default (Render uses $PORT)
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
