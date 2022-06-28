from app.main.nlp import nlp_router
from app.main.nlp.analyzeSentiments.dto.analyzeSentement_dto import AnalyzeSentimentDTO
from app.main.nlp.analyzeSentiments.service.analyzeSentement_service import AnalyzeSentimentService


@nlp_router.post("/analyzeSentiment")
def analyze_sentiment(query: AnalyzeSentimentDTO):
    return AnalyzeSentimentService.get_sentiment(query)