import os
from typing import List
import uuid
from google.cloud import dialogflow
from flask import  Flask, make_response
from google.cloud import language_v1
from flask_restplus import Resource, Api, reqparse
from werkzeug.middleware.proxy_fix import ProxyFix

# IBM Watson NLU
import json
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 \
    import Features, EmotionOptions

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

api = Api(app,
          title="icets-explorers-infy",
          version="0.0.1",
          description="Google hackthon")

ns = api.namespace('Google NLP APIs',path="/api")
ng = api.namespace("Dialogflow",path="/api")
nw = api.namespace("IBM Watson",path="/api")

parser = reqparse.RequestParser()
parser.add_argument('Sentence', type=str, required=True,
                    help='sentence cannot be blank')
parser.add_argument('language', type=str, help='sentence language')


nwparser = reqparse.RequestParser()
nwparser.add_argument('Sentence', type=str, required=True,
                    help='sentence cannot be blank')
nwparser.add_argument('target', type=lambda x:x.split(","), help='target keyword separated by comma')

CLASSIFY_TEXT = "Classify Text"
ANALYZE_ENTITY_SENTIMENT = "Analyze Entity Sentiment"
SENTIMENT_ANALYSIS = "Sentiment Analysis"
ENTITY_ANALYSIS = "Entity Analysis"
IDENTIFY_INTENT = "Identify Intent"



CE_SOURCE = "knative/eventing/samples/hello-world"
CE_TYPE = "dev.knative.samples.hifromknative"

@ns.route('/analyseSentiment')
@ns.expect(parser)
class AnalyseSentiment(Resource):
    def post(self):

        args = parser.parse_args()
        
        client = language_v1.LanguageServiceClient()
        type_ = language_v1.Document.Type.PLAIN_TEXT

        # For list of supported languages:
        # https://cloud.google.com/natural-language/docs/languages
        language = args['language'] or None
        text_content = args['Sentence']

        if language:
            document = {"content": text_content,
                        "type_": type_, "language": language}
        else:
            document = {"content": text_content,
                        "type_": type_}

        # Available values: NONE, UTF8, UTF16, UTF32
        encoding_type = language_v1.EncodingType.UTF8

        response = client.analyze_sentiment(
            request={'document': document, 'encoding_type': encoding_type})

        response_body = {SENTIMENT_ANALYSIS: {}}
        for sentence in response.sentences:
            response_body[SENTIMENT_ANALYSIS][text_content] = {
                "magnitude": sentence.sentiment.magnitude, "score": sentence.sentiment.score}
        
        response = make_response(response_body)
        response.headers["Ce-Id"] = str(uuid.uuid4())
        response.headers["Ce-specversion"] = "0.3"
        response.headers["Ce-Source"] = CE_SOURCE
        response.headers["Ce-Type"] = CE_TYPE
        
        return response 


@ns.route('/analyseEntities')
@ns.expect(parser)
class AnalyseEntities(Resource):
    def post(self):

        args = parser.parse_args()
        
        client = language_v1.LanguageServiceClient()
        type_ = language_v1.Document.Type.PLAIN_TEXT

        # For list of supported languages:
        # https://cloud.google.com/natural-language/docs/languages
        language = args['language'] or None
        text_content = args['Sentence']

        if language:
            document = {"content": text_content,
                        "type_": type_, "language": language}
        else:
            document = {"content": text_content,
                        "type_": type_}

        # Available values: NONE, UTF8, UTF16, UTF32
        encoding_type = language_v1.EncodingType.UTF8

        response = client.analyze_entities(
            request={'document': document, 'encoding_type': encoding_type})

        response_body = {ENTITY_ANALYSIS: {}}

        for entity in response.entities:
            response_body[ENTITY_ANALYSIS][text_content] = {
                "name": entity.name, "Salience score": entity.salience, "type_": entity.type_}
            mentions = {}
            for mention in entity.mentions:
                mentions[mention.text.content] = {
                    "begin_offset": mention.text.begin_offset}
            response_body[ENTITY_ANALYSIS][text_content]["mentions"] = mentions
            response_body[ENTITY_ANALYSIS][text_content]["language"] = language

        response = make_response(response_body)
        response.headers["Ce-Id"] = str(uuid.uuid4())
        response.headers["Ce-specversion"] = "0.3"
        response.headers["Ce-Source"] = CE_SOURCE
        response.headers["Ce-Type"] = CE_TYPE

        return response_body


@ns.route('/classifyText')
@ns.expect(parser)
class ClassifyText(Resource):
    def post(self):

        args = parser.parse_args()
        
        client = language_v1.LanguageServiceClient()
        type_ = language_v1.Document.Type.PLAIN_TEXT

        # For list of supported languages:
        # https://cloud.google.com/natural-language/docs/languages
        language = args['language'] or None
        text_content = args['Sentence']

        if language:
            document = {"content": text_content,
                        "type_": type_, "language": language}
        else:
            document = {"content": text_content,
                        "type_": type_}

        try:
            response = client.classify_text(
                request={'document': document})
        except AttributeError:
            return {"ERROR": "Please give a valid paragraph"}

        response_body = {CLASSIFY_TEXT: {}}
        
        for category in response.categories:
            response_body[CLASSIFY_TEXT][text_content] = {
                "Category name": category.name,
                "Confidence": category.confidence
            }


        response = make_response(response_body)
        response.headers["Ce-Id"] = str(uuid.uuid4())
        response.headers["Ce-specversion"] = "0.3"
        response.headers["Ce-Source"] = CE_SOURCE
        response.headers["Ce-Type"] = CE_TYPE

        return response_body

@ns.route('/analyseEntitySentiment')
@ns.expect(parser)
class AnalyseEntitySentiment(Resource):
    def post(self):

        args = parser.parse_args()
        
        client = language_v1.LanguageServiceClient()
        type_ = language_v1.Document.Type.PLAIN_TEXT

        # For list of supported languages:
        # https://cloud.google.com/natural-language/docs/languages
        language = args['language'] or None
        text_content = args['Sentence']

        if language:
            document = {"content": text_content,
                        "type_": type_, "language": language}
        else:
            document = {"content": text_content,
                        "type_": type_}

        response = client.analyze_entity_sentiment(
            request={'document': document})

        response_body = {ANALYZE_ENTITY_SENTIMENT: {}}
        
        for entity in response.entities:
            response_body[ANALYZE_ENTITY_SENTIMENT][text_content] = {
                "Representative name": entity.name,
                "Entity type": language_v1.Entity.Type(entity.type_).name,
                "Salience score": entity.salience,
                "Sentiment": {
                    "Magnitude": entity.sentiment.magnitude,
                    "Score": entity.sentiment.score
                },
                "metadata": {
                    metadata_name: metadata_value for metadata_name, metadata_value in entity.metadata.items()
                },
                "mentions": {
                    "Mention text": mention.text.content for mention in entity.mentions
                },
                "language": response.language
            }

        response = make_response(response_body)
        response.headers["Ce-Id"] = str(uuid.uuid4())
        response.headers["Ce-specversion"] = "0.3"
        response.headers["Ce-Source"] = CE_SOURCE
        response.headers["Ce-Type"] = CE_TYPE

        return response_body


@ng.route('/identifyIntent')
@ng.expect(parser)
class IdentifyIntent(Resource):
    def post(self):

        args = parser.parse_args()
        text = args['Sentence']
        language_code = args['language'] or None
        
        project_id = "gcms-oht28999u9-2022"
        session_id = uuid.uuid4()

        session_client = dialogflow.SessionsClient()
        session = session_client.session_path(project_id, session_id)

        text_input = dialogflow.TextInput(text=text, language_code=language_code)

        query_input = dialogflow.QueryInput(text=text_input)

        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )

        response_body = {
            IDENTIFY_INTENT: {
                "Query text":response.query_result.query_text,
                "Detected intent":response.query_result.intent.display_name,
                "confidence":response.query_result.intent_detection_confidence,
                "Fulfillment text":response.query_result.fulfillment_text
            }
        }

        response = make_response(response_body)
        response.headers["Ce-Id"] = str(uuid.uuid4())
        response.headers["Ce-specversion"] = "0.3"
        response.headers["Ce-Source"] = CE_SOURCE
        response.headers["Ce-Type"] = CE_TYPE

        return response_body

@nw.route('/identifyEmotions')
@nw.expect(nwparser)
class identifyEmotions(Resource):
    def post(self):
        args = nwparser.parse_args()

        key = json.load(open(os.environ["IBM_NLU_CREDENTIALS"]))
        authenticator = IAMAuthenticator(key["apikey"])
        natural_language_understanding = NaturalLanguageUnderstandingV1(
            version='2022-04-07',
            authenticator=authenticator
        )

        natural_language_understanding.set_service_url(key["url"])

        response = natural_language_understanding.analyze(
            text=args["Sentence"],
            features=Features(emotion=EmotionOptions(targets=args["target"]))).get_result()

        return response



if __name__ == "__main__":
    
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join("certs","gcp","gcms-oht28999u9-2022-d6a3ab347605.json")
    os.environ["IBM_NLU_CREDENTIALS"] = os.path.join("certs","ibm","nlu_watson.json")
    
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
