import json
import os
from flask import  Flask
from flask_restplus import Resource, Api, reqparse
from werkzeug.middleware.proxy_fix import ProxyFix

from api_wrapper import api_wrapper

DEFAULTLANGUAGE = "en"


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

api = Api(app,
          title="icets-explorers-infy",
          version="0.0.1",
          description="Google hackthon")

ns = api.namespace('Google NLP APIs',path="/api")
ng = api.namespace("Dialogflow",path="/api")
nw = api.namespace("IBM Watson",path="/api")
ne = api.namespace("Elasticsearch",path="/api")

parser = reqparse.RequestParser()
parser.add_argument('conversation', type=lambda x:json.loads(x), required=True,
                    help='conversation cannot be blank')
parser.add_argument('language', type=str,default=DEFAULTLANGUAGE, help='sentence language')


ngparser = reqparse.RequestParser()
ngparser.add_argument("sentence", type=str, required=True,
                    help='sentence cannot be blank')
ngparser.add_argument('language', type=str,default=DEFAULTLANGUAGE, help='sentence language')


nwparser = reqparse.RequestParser()
nwparser.add_argument('conversation', type=lambda x:json.loads(x), required=True,
                    help='conversation cannot be blank')
nwparser.add_argument('target', type=lambda x:x.split(","), help='target keyword separated by comma')


neparser = reqparse.RequestParser()
neparser.add_argument("conversation", type=lambda x:json.loads(x), required=True)

@ns.route('/analyseSentiment')
@ns.expect(parser)
class AnalyseSentiment(Resource):
    def post(self):

        args = parser.parse_args()

        response_body = api_wrapper.analyse_sentiment_wrapper(args)
        response = api_wrapper.knative_enventing_wrapper(response_body,"classify_text")
        
        return response


# @ns.route('/analyseEntities')
# @ns.expect(parser)
class AnalyseEntities(Resource):
    def post(self):

        args = parser.parse_args()
        
        response_body = api_wrapper.analyse_entities_wrapper(args)
        response = api_wrapper.knative_enventing_wrapper(response_body)

        return response


@ns.route('/classifyText')
@ns.expect(parser)
class ClassifyText(Resource):
    def post(self):

        args = parser.parse_args()
        
        response_body = api_wrapper.classify_text_wrapper(args)
        response = api_wrapper.knative_enventing_wrapper(response_body,"identify_emotion")
        
        return response

# @ns.route('/analyseEntitySentiment')
# @ns.expect(parser)
class AnalyseEntitySentiment(Resource):
    def post(self):

        args = parser.parse_args()
        
        response_body = api_wrapper.analyse_entity_sentiment_wrapper(args)
        response = api_wrapper.knative_enventing_wrapper(response_body)

        return response


@ng.route('/identifyIntent')
@ng.expect(ngparser)
class IdentifyIntent(Resource):
    def post(self):

        args = ngparser.parse_args()

        response_body = api_wrapper.identify_intent_wrapper(args)
        response = api_wrapper.knative_enventing_wrapper(response_body)
        
        return response

@nw.route('/identifyEmotions')
@nw.expect(nwparser)
class identifyEmotions(Resource):
    def post(self):
        args = nwparser.parse_args()

        response_body = api_wrapper.indentify_emotions_wrapper(args)
        response = api_wrapper.knative_enventing_wrapper(response_body,"elasticsearch")

        return response

@ne.route("/esCreate")
@ne.expect(neparser)
class elasticSearchCreate(Resource):
    def post(self):
        args = nwparser.parse_args()

        response_body = api_wrapper.elastic_search_wrapper(args)
        response = api_wrapper.knative_enventing_wrapper(response_body,"completed")

        return response


if __name__ == "__main__":
    
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join("certs","gcp","gcms-oht28999u9-2022-d6a3ab347605.json")
    os.environ["IBM_NLU_CREDENTIALS"] = os.path.join("certs","ibm","nlu_watson.json")
    os.environ["ES_CREDENTIALS"] =  os.path.join("certs","es","es.ini")
    
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
