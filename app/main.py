from flask import Flask
from flask_cors import CORS
from app.db import Database
from app.routes.api import recommend

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Register API route
    app.add_url_rule("/api/recommend", view_func=recommend)

    # Initialize Database
    try:
        Database.get_connection()
        print("✅ Database connection successful.")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
