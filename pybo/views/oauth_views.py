import json
from functools import partial

import jwt
import requests
from flask import Blueprint, request, jsonify, redirect, url_for, session
from flask_jwt_extended import create_access_token, create_refresh_token, set_access_cookies, set_refresh_cookies
from werkzeug.local import LocalProxy

from pybo import db
from pybo.kakaoConfig import CLIENT_ID, REDIRECT_URI, CLIENT_SECRET
from pybo.models import User

bp = Blueprint('oauth', __name__, url_prefix='/oauth')


@bp.route('/kakao/callback')
def oauth():
    code = str(request.args.get('code'))
    url = "https://kauth.kakao.com/oauth/token"
    kdata = "grant_type=authorization_code&client_id="+CLIENT_ID+"&redirect_uri="+REDIRECT_URI+"&code="+str(code)+"&client_secret="+CLIENT_SECRET
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache",
        }
    response = requests.request("POST", url, data=kdata, headers=headers)
    access_token = json.loads(((response.text).encode('utf-8')))['access_token']

    url = "https://kapi.kakao.com/v2/user/signup"

    headers.update({'Authorization' : "Bearer " + str(access_token)})
    response = requests.request("POST", url, headers=headers)

    url = "https://kapi.kakao.com/v2/user/me"
    response = requests.request("POST", url, headers=headers)

    data = response.json()

    return social_signin(data=data)
    # return (response.text)

@bp.route('/')
def oauth_url_api():
    """
    Kakao OAuth URL 가져오기
    """
    return redirect(
        "https://kauth.kakao.com/oauth/authorize?client_id=%s&redirect_uri=%s&response_type=code" \
        % (CLIENT_ID, REDIRECT_URI)

    )


def social_signin(data):
    kakao_account = data.get("kakao_account")
    properties = data.get("properties")
    email = kakao_account.get("email", None)
    kakao_id = str(data.get("id"))  # 모델에서 비번을 str으로 설정했기 때문에 여기서 문자열로 변경안해주면 에러가!
    nickname = properties.get("nickname", None)
    user = User.query.filter_by(id=kakao_id).first()  # 아이디값으로 쿼리 필터를 한번 해주고
    if not user:
        new_user = User(
            email=email,
            password=kakao_id,
            id=kakao_id,
            username=nickname
        )
        db.session.add(new_user)
        db.session.commit()
        session.clear()
        session['user_id'] = user.id
        return redirect(url_for('main.index'))
    else:
        session.clear()
        session['user_id'] = user.id
        _next = request.args.get('next', '')
        if _next:
            return redirect(_next)
        else:
            return redirect(url_for('main.index'))


