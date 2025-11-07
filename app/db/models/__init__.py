# import jwt
# from datetime import datetime, timedelta
# from werkzeug.security import generate_password_hash, check_password_hash


# class User2(db.Model):
#     __tablename__ = 'users'
#     id = .Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password_hash = db.Column(db.String(200))
#     role = db.Column(db.String(20), default='user')
#
#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password)
#
#     def check_password(self, password):
#         return check_password_hash(self.password_hash, password)
#
#     def generate_jwt(self, token_type='access'):
#         """Generate JWT token with expiration"""
#         expiration = (
#             timedelta(seconds=int(os.getenv('JWT_ACCESS_EXP')))
#             if token_type == 'access'
#             else timedelta(seconds=int(os.getenv('JWT_REFRESH_EXP')))
#         )
#
#         payload = {
#             'sub': self.id,
#             'email': self.email,
#             'role': self.role,
#             'type': token_type,
#             'exp': datetime.utcnow() + expiration
#         }
#         return jwt.encode(
#             payload,
#             os.getenv('SECRET_KEY'),
#             algorithm='HS256'
#         )
