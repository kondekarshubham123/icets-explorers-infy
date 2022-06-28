from google.cloud import language_v1
from app.main.nlp.analyzeSentiments.dto.analyzeSentement_dto import AnalyzeSentimentDTO


class AnalyzeSentimentService():

    @staticmethod
    def get_sentiment(query: AnalyzeSentimentDTO):

        client = language_v1.LanguageServiceClient()
        type_ = language_v1.Document.Type.PLAIN_TEXT

        # For list of supported languages:
        # https://cloud.google.com/natural-language/docs/languages
        language = query.language
        text_content = query.sentence

        document = {"content": text_content,
                    "type_": type_, "language": language}

        # Available values: NONE, UTF8, UTF16, UTF32
        encoding_type = language_v1.EncodingType.UTF8

        response = client.analyze_sentiment(
            request={'document': document, 'encoding_type': encoding_type})

        response_body = {"Sentiment Analysis": {}}
        for sentence in response.sentences:
            response_body["Sentiment Analysis"][sentence.text.content] = {
                "magnitude": sentence.sentiment.magnitude, "score": sentence.sentiment.score}

        return response_body
