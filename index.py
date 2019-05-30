from flask import Flask, jsonify, request
import os
import dialogflow as df 
import requests 
import json 


app = Flask(__name__)
api_key = os.getenv('OMDB_API_KEY')
project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
default_puzzled_response = "Sorry, I can't figure out what to do!"


@app.route('/')
def index():
	return jsonify("Venus Server Running!")


@app.route('/dialogflow_webhook', methods=['POST'])
def dialogflow_webhook():
	data = request.get_json(silent=True)
	intent_name = data['queryResult']['intent']['displayName']

	result = None

	if intent_name == 'movie':
		result = get_movie_detail(data)
	
	return result or prepare_fulfillment_text(default_puzzled_response)


@app.route('/send_message', methods=['POST'])
def send_message():
	message = request.form.get('message', None)
	fulfillment_text = get_fulfillment_from_dialogflow(project_id, 'unique', message, 'en')

	return prepare_fulfillment_text(fulfillment_text or default_puzzled_response)


def prepare_fulfillment_text(text):

	reply = {
		"fulfillmentText": text
	}

	return jsonify(reply)


def get_fulfillment_from_dialogflow(project_id, session_id, text, language_code):
	session_client = df.SessionsClient()
	session = session_client.session_path(project_id, session_id)

	if text: 
		text_input = df.types.TextInput(text=text, language_code=language_code)
		query_input = df.types.QueryInput(text=text_input)

		response = session_client.detect_intent(session=session, query_input=query_input)

		return response.query_result.fulfillment_text


def get_movie_detail(data):

	movie = data['queryResult']['parameters']['movie']

	movie_detail = requests.get('http://www.omdbapi.com/?t={0}&apikey={1}'.format(movie, api_key)).content
	movie_detail = json.loads(movie_detail)

	response = """
		Title: {0}
		Released: {1}
		Actors: {2}
		Plot: {3}
	""".format(movie_detail['Title'], movie_detail['Released'], movie_detail['Actors'], movie_detail['Plot'])

	reply = prepare_fulfillment_text(response)

	return reply


if __name__ == "__main__":
	app.run()


