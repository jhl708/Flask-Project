import os

BASE_DIR = os.path.dirname(__file__)

# 데이터베이스 접속 주소 : 데이터베이스 파일이 pybo.db로 저장됨
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(BASE_DIR, 'pybo.db'))
# SQLAlchemy의 이벤트를 처리하는 옵션
SQLALCHEMY_TRACK_MODIFICATIONS = False
# CSRF(cross-site request forgery)라는 웹 사이트 취약점 공격을 방지하는 데 사용
SECRET_KEY = "dev"