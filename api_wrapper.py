import os
import uuid
from google.cloud import language_v1
from google.cloud import dialogflow
from flask import make_response

# IBM Watson NLU
import json
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 \
    import Features, EmotionOptions

PROJECT_ID = "gcms-oht28999u9-2022"

CLASSIFY_TEXT = "Classify Text"
ANALYZE_ENTITY_SENTIMENT = "Analyze Entity Sentiment"
SENTIMENT_ANALYSIS = "Sentiment Analysis"
ENTITY_ANALYSIS = "Entity Analysis"
IDENTIFY_INTENT = "Identify Intent"

CE_SOURCE = "knative/eventing/samples/hello-world"
CE_TYPE = "dev.knative.samples.hifromknative"

class api_wrapper(object):
    
    @staticmethod
    def analyse_sentiment_wrapper(args):

        client = language_v1.LanguageServiceClient()
        type_ = language_v1.Document.Type.PLAIN_TEXT

        # For list of supported languages:
        # https://cloud.google.com/natural-language/docs/languages
        language = args['language'] or None
        text_content = args['Sentence']

        document = {"content": text_content,
                    "type_": type_, "language": language}

        # Available values: NONE, UTF8, UTF16, UTF32
        encoding_type = language_v1.EncodingType.UTF8

        response = client.analyze_sentiment(
            request={'document': document, 'encoding_type': encoding_type})

        response_body = {SENTIMENT_ANALYSIS: {}}
        for sentence in response.sentences:
            response_body[SENTIMENT_ANALYSIS][text_content] = {
                "magnitude": sentence.sentiment.magnitude, "score": sentence.sentiment.score}

        return response_body 
    
    @staticmethod
    def analyse_entities_wrapper(args):
        
        client = language_v1.LanguageServiceClient()
        type_ = language_v1.Document.Type.PLAIN_TEXT

        # For list of supported languages:
        # https://cloud.google.com/natural-language/docs/languages
        language = args['language']
        text_content = args['Sentence']

        document = {"content": text_content,
                    "type_": type_, "language": language}

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
    
    @staticmethod
    def classify_text_wrapper(args):
        client = language_v1.LanguageServiceClient()
        type_ = language_v1.Document.Type.PLAIN_TEXT

        # For list of supported languages:
        # https://cloud.google.com/natural-language/docs/languages
        language = args['language']
        text_content = args['Sentence']

        document = {"content": text_content,
                    "type_": type_, "language": language}

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
        
    @staticmethod
    def analyse_entity_sentiment_wrapper(args):
        client = language_v1.LanguageServiceClient()
        type_ = language_v1.Document.Type.PLAIN_TEXT

        # For list of supported languages:
        # https://cloud.google.com/natural-language/docs/languages
        language = args['language']
        text_content = args['Sentence']

        document = {"content": text_content,
                    "type_": type_, "language": language}

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

    @staticmethod
    def identify_intent_wrapper(args):
        text = args['Sentence']
        language_code = args['language']
        
        project_id = PROJECT_ID
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

        return response_body
    
    @staticmethod
    def indentify_emotions_wrapper(args):

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
    
    @staticmethod
    def call_analytics_wrapper(args):
        return args

    @staticmethod
    def knative_enventing_wrapper(response_body):
        response = make_response(response_body)
        response.headers["Ce-Id"] = str(uuid.uuid4())
        response.headers["Ce-specversion"] = "0.3"
        response.headers["Ce-Source"] = CE_SOURCE
        response.headers["Ce-Type"] = CE_TYPE
        return response



