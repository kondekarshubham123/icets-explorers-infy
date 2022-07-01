import os
from flask import  Flask
from google.cloud import language_v1
from flask_restplus import Resource, Api, reqparse
from werkzeug.middleware.proxy_fix import ProxyFix


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

api = Api(app,
          title="icets-explorers-infy",
          version="0.0.1",
          description="Google hackthon")

ns = api.namespace('Google NLP APIs',path="/api")

parser = reqparse.RequestParser()
parser.add_argument('Sentence', type=str, required=True,
                    help='sentence cannot be blank')
parser.add_argument('language', type=str, help='sentence language')


CLASSIFY_TEXT = "Classify Text"
ANALYZE_ENTITY_SENTIMENT = "Analyze Entity Sentiment"
SENTIMENT_ANALYSIS = "Sentiment Analysis"
ENTITY_ANALYSIS = "Entity Analysis"



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
        return response_body


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
        return response_body



if __name__ == "__main__":
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= os.path.join("dev-racer-354316-304665e54afb.json")
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
