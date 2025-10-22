import os

SECRET_KEY = 'dev'
SQLALCHEMY_DATABASE_URI = "sqlite:///project.db"
SWAGGER = {
    'title': 'My API',
    'uiversion': 3
}

# SQLALCHEMY_DATABASE_URI=(
# f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
# f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
# ),
