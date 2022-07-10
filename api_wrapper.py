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

CLASSIFY_TEXT = "classifyText"
ANALYZE_ENTITY_SENTIMENT = "analyzeEntitySentiment"
SENTIMENT_ANALYSIS = "sentimentAnalysis"
ENTITY_ANALYSIS = "entityAnalysis"
IDENTIFY_INTENT = "identifyIntent"
IDENTIFY_EMOTIONS = "identifyEmotions"

CE_SOURCE = "knative/eventing/samples/hello-world"
CE_TYPE = "dev.knative.samples.hifromknative"

class api_wrapper(object):
    
    @staticmethod
    def analyse_sentiment_wrapper(args):

        ## Sentiment Score Configuration
        NEGATIVE = lambda x: (-1 <= x < - 0.5)
        NEUTRAL = lambda x: (-0.5 <= x < 0.5)
        POSITIVE = lambda x: (0.5 <= x <= 1)

        client = language_v1.LanguageServiceClient()
        type_ = language_v1.Document.Type.PLAIN_TEXT

        # For list of supported languages:
        # https://cloud.google.com/natural-language/docs/languages
        language = args['language']

        args["conversation"][SENTIMENT_ANALYSIS] = {}

        def find_sentiment(score_dict):
            for text,val in score_dict.items():
                if NEGATIVE(val["score"]):
                    return "NEGATIVE"
                if POSITIVE(val["score"]):
                    return "POSITIVE"
                if NEUTRAL(val["score"]):
                    return "NEUTRAL"
            return None

        def find_sentiment_score(text_content,language):

            document = {"content": text_content,
                        "type_": type_, "language": language}

            # Available values: NONE, UTF8, UTF16, UTF32
            encoding_type = language_v1.EncodingType.UTF8

            response = client.analyze_sentiment(
                request={'document': document, 'encoding_type': encoding_type})

            response_body = {}
            for sentence in response.sentences:
                response_body[text_content] = {
                    "magnitude": sentence.sentiment.magnitude, "score": sentence.sentiment.score}
            return find_sentiment(response_body)

        args["conversation"][SENTIMENT_ANALYSIS]["agent_sentiment"] = find_sentiment_score(" ".join(args["conversation"]["agent"]["transcript"]),language)
        args["conversation"][SENTIMENT_ANALYSIS]["client_sentiment"] = find_sentiment_score(" ".join(args["conversation"]["customer"]["transcript"]),language)
        return args["conversation"]
    
    @staticmethod
    def analyse_entities_wrapper(args):
        
        client = language_v1.LanguageServiceClient()
        type_ = language_v1.Document.Type.PLAIN_TEXT

        # For list of supported languages:
        # https://cloud.google.com/natural-language/docs/languages
        language = args['language']
        text_content = args['sentence']

        document = {"content": text_content,
                    "type_": type_, "language": language}

        # Available values: NONE, UTF8, UTF16, UTF32
        encoding_type = language_v1.EncodingType.UTF8

        response = client.analyze_entities(
            request={'document': document, 'encoding_type': encoding_type})

        response_body = {ENTITY_ANALYSIS: {}}

        for entity in response.entities:
            response_body[ENTITY_ANALYSIS][text_content] = {
                "name": entity.name, "salienceScore": entity.salience, "type_": entity.type_}
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
        text_content = args['sentence']

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
                "categoryName": category.name,
                "confidence": category.confidence
            }
        
        return response_body
        
    @staticmethod
    def analyse_entity_sentiment_wrapper(args):
        client = language_v1.LanguageServiceClient()
        type_ = language_v1.Document.Type.PLAIN_TEXT

        # For list of supported languages:
        # https://cloud.google.com/natural-language/docs/languages
        language = args['language']
        text_content = args['sentence']

        document = {"content": text_content,
                    "type_": type_, "language": language}

        response = client.analyze_entity_sentiment(
            request={'document': document})

        response_body = {ANALYZE_ENTITY_SENTIMENT: {}}
        
        for entity in response.entities:
            response_body[ANALYZE_ENTITY_SENTIMENT][text_content] = {
                "representativeName": entity.name,
                "entityType": language_v1.Entity.Type(entity.type_).name,
                "salienceScore": entity.salience,
                "sentiment": {
                    "magnitude": entity.sentiment.magnitude,
                    "score": entity.sentiment.score
                },
                "metadata": {
                    metadata_name: metadata_value for metadata_name, metadata_value in entity.metadata.items()
                },
                "mentions": {
                    "mentionText": mention.text.content for mention in entity.mentions
                },
                "language": response.language
            }

        return response_body

    @staticmethod
    def identify_intent_wrapper(args):
        text = args['sentence']
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
                "queryText":response.query_result.query_text,
                "detectedIntent":response.query_result.intent.display_name,
                "confidence":response.query_result.intent_detection_confidence,
                "fulfillmentText":response.query_result.fulfillment_text
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

        response_body = {IDENTIFY_EMOTIONS :natural_language_understanding.analyze(
            text=args["sentence"],
            features=Features(emotion=EmotionOptions(targets=args["target"]))).get_result()}

        return response_body
    
    @staticmethod
    def knative_enventing_wrapper(response_body):
        response = make_response(response_body)
        response.headers["Ce-Id"] = str(uuid.uuid4())
        response.headers["Ce-specversion"] = "0.3"
        response.headers["Ce-Source"] = CE_SOURCE
        response.headers["Ce-Type"] = CE_TYPE
        return response



