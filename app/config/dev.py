import os
from datetime import timedelta

SECRET_KEY = "dev"
JWT_SECRET_KEY = "dev"
# SQLALCHEMY_DATABASE_URI = "sqlite:///project.db"
SQLALCHEMY_DATABASE_URI = "postgresql://ryl_dev:ryl_dev1@localhost:5432/ryl_dev"
SQLALCHEMY_TRACK_MODIFICATIONS = False

JWT_VERIFY_SUB = False
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=10)  # Token lifetime

# SWAGGER = {
#     'title': 'My API',
#     'uiversion': 3
# }

# SQLALCHEMY_DATABASE_URI=(
# f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
# f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
# ),
