from recommendation.repo.user_repo import UserRepo
from recommendation.service.recommendation_service import RecommendationService
from recommendation.service.similarity_service import SimilarityService


class RecommendationManager:
    def __init__(self):
        self.user_repo = UserRepo()
        self.recommendation_service = RecommendationService(user_repo=self.user_repo)
        self.similarity_service = SimilarityService(user_repo=self.user_repo)

    def get_recommendation_service(self):
        return self.recommendation_service

    def get_similarity_service(self):
        return self.similarity_service
