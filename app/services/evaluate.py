import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from tabulate import tabulate
from sklearn.metrics import accuracy_score
from app.services.recommendation import fetch_user_product_matrix, get_recommendations

def plot_user_product_matrix():
    """Visualizes the user-product interaction matrix."""
    user_product_matrix, _ = fetch_user_product_matrix()
    print("User-Product Matrix:")
    print(tabulate(user_product_matrix, headers='keys', tablefmt='psql'))

    if user_product_matrix is None:
        print("No interactions found.")
        return

    plt.figure(figsize=(12, 6))
    sns.heatmap(user_product_matrix, cmap="coolwarm", linewidths=0.5)
    plt.xlabel("Products")
    plt.ylabel("Users")
    plt.title("User-Product Interaction Matrix")
    plt.show()

def show_user_interactions():
    """Print all user interactions in a tabulated format."""
    _, df = fetch_user_product_matrix()
    if df is None:
        print("No interactions found.")
        return
    print("\nUser Interactions:")
    print(tabulate(df, headers='keys', tablefmt='psql'))

def evaluate_recommendations():
    """Evaluate recommendations using accuracy score."""
    user_product_matrix, df = fetch_user_product_matrix()
    
    if user_product_matrix is None:
        print("No interactions found.")
        return
    
    actual = []
    predicted = []
    results = []
    
    for user_id in user_product_matrix.index:
        actual_products = df[df["userId"] == user_id]["productId"].tolist()
        recommended_products = get_recommendations(user_id)
        
        actual.append(set(actual_products))
        predicted.append(set(recommended_products))
        
        results.append([user_id, actual_products, recommended_products])
    
    print("\nUser-wise Recommendations:")
    print(tabulate(results, headers=["User ID", "Actual Products", "Recommended Products"], tablefmt='psql'))
    
    accuracy = sum(len(act & pred) / max(len(act), 1) for act, pred in zip(actual, predicted)) / len(actual)
    
    print(f"\nRecommendation Accuracy: {accuracy:.6f}")

if __name__ == "__main__":
    show_user_interactions()
    plot_user_product_matrix()
    evaluate_recommendations()
