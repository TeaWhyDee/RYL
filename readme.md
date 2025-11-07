# Documentation
Migrations:
https://flask-migrate.readthedocs.io/en/latest/index.html
https://alembic.sqlalchemy.org/en/latest/tutorial.html

https://iamjeremie.me/post/2025-08/database-migration-with-flask-sqlalchemy-and-alembic/


# Prepare
```bash
python -m venv venv
```
install dependencies:
```
pip install -r requirements.txt
```

## Database
This project ONLY works correctly with Postgres. Why?:
- Audit Tables from sqla-extensions.

Create DB:
```sql
DROP DATABASE ryl_dev;

CREATE DATABASE ryl_dev;
CREATE USER ryl_dev WITH PASSWORD 'ryl_dev1';
GRANT ALL PRIVILEGES ON DATABASE ryl_dev TO ryl_dev;
ALTER DATABASE ryl_dev OWNER to ryl_dev;
```

Set up migrations (Flask-Migrate)[https://flask-migrate.readthedocs.io/en/latest/]:
```bash
flask db init
flask db migrate -m "Initial migration."
flask db upgrade
```
Migrations config: `migrations/alembic.ini`

# Run
App entry point in `app/__init__.py`


# Other
Go to http://127.0.0.1:5000/apidocs/ for Swagger UI.

SQLAlchemy models:
https://flask-sqlalchemy.readthedocs.io/en/stable/models/

Perform mugration:
```
flask db migrate -m "Message"
flask db upgrade
```

flask db --help





https://github.com/flasgger/flasgger/blob/bb1a86b2d71ed0bdd3e8183570a9ce9d1f5abac1/examples/parse_openapi3_json_product_schema.yml#L18
https://swagger.io/docs/specification/v3_0/describing-request-body/describing-request-body/
https://swagger.io/docs/specification/v3_0/authentication/cookie-authentication/
https://swagger.io/docs/specification/v3_0/describing-request-body/describing-request-body/
