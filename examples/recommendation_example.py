from recommendation.repo.user_repo import UserRepo
from recommendation.service.recommendation_service import RecommendationService

if __name__ == '__main__':
    user_repo = UserRepo()
    recommendation_service = RecommendationService(user_repo=user_repo)
    recommendations = recommendation_service.get_recommendations("1")
    print(recommendations)

    # Plot the user-product matrix
    recommendation_service.plot_user_product_matrix()