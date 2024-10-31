from flask import Flask, g, request, make_response, Response, flash
from flask import session, render_template, request, redirect, url_for
from markupsafe import Markup
from datetime import date, datetime, timedelta
from flask_mail import Mail, Message
import os
from .init_db import init_database, db_session
from .models import User
from sqlalchemy import and_
from functools import wraps

import re
import logging
import base64
import json
from io import BytesIO
import tensorflow as tf
from .cnn import ConvolutionalNeuralNetwork
from .operations import calculate_sqrt, calculate_operation  # 연산 파일 임포트

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import math

# 모델 로드를 애플리케이션이 시작될 때 한 번만 수행하도록 전역에서 설정
CNN = ConvolutionalNeuralNetwork()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
app.config.update(
    SECRET_KEY=os.environ.get('FLASK_SECRET_KEY', 'default_secret'),
    SESSION_COOKIE_NAME='secure_flask_session',
    SESSION_COOKIE_SECURE=True,  # HTTPS에서만 쿠키 전송
    SESSION_COOKIE_HTTPONLY=True,  # JavaScript에서 접근 불가
    SESSION_COOKIE_SAMESITE='Lax',  # XSS 공격 방지
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),  # 세션 만료 시간 설정
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME='',  # 본인 이메일 넣으세요
    MAIL_PASSWORD=''    # 본인 이메일 비밀번호 넣으세요
)


# Home route
@app.route('/')
def home():
    return render_template('app.html')

# 로그인 연동 
@app.route('/login', methods=['GET'])
def login():
    
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login_register():
    if request.method == 'POST':
        if 'email' in request.form:  # 로그인 또는 회원가입 요청 판단
            email = request.form.get('email')
            passwd = request.form.get('passwd')
            if 'passwd2' in request.form:  # 회원가입 폼 제출
                passwd2 = request.form.get('passwd2')
                nickname = request.form.get('nickname')

                # Validation checks
                if passwd != passwd2:
                    flash("비밀번호가 일치하지 않습니다.", "signup")
                    return redirect(url_for('login_register'))

                # Check if email already exists
                if User.query.filter_by(email=email).first():
                    flash("이미 사용 중인 이메일입니다.", "signup")
                    return redirect(url_for('login_register'))

                # Create user
                u = User(email=email, passwd=passwd, nickname=nickname)
                try:
                    db_session.add(u)
                    db_session.commit()
                    flash("%s 님, 가입을 환영합니다!" % nickname, "login")
                    return redirect(url_for('login_register'))
                except Exception as e:
                    db_session.rollback()
                    flash("회원가입 중 오류가 발생했습니다. 다시 시도하세요.", "signup")
                    return redirect(url_for('login_register'))

            else:  # 로그인 폼 제출
                u = User.query.filter(and_(User.email == email, User.passwd == passwd)).first()
                if u:
                    session['loginUserId'] = u.id
                    session['loginUserName'] = u.nickname
                    return redirect(url_for('home'))
                else:
                    flash("로그인에 실패했습니다. 이메일과 비밀번호를 확인하세요.", "login")
                    return redirect(url_for('login_register'))

    # GET 요청은 기본 템플릿을 렌더링
    return render_template('app.html')


@app.route('/logout', methods=['get'])
def logout():
    if session.get('loginUserId'):
        del session['loginUserId']
        del session['loginUserName']    
        
    return redirect('/')


# 로그인 이용자만 서비스 이용

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loginUserId' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


# Flask-Mail 설정
mail = Mail(app)

# Contact route for sending emails
@app.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    msg = Message('Contact Form Submission',
                  sender='', # 본인 이메일 넣으세요
                  recipients=['']) # 본인 이메일 넣으세요
    msg.body = f"Name: {name}\nEmail: {email}\nMessage: {message}"

    try:
        mail.send(msg)
        print("Email sent successfully.")
        return redirect(url_for('home', message='Message sent successfully'))
    except Exception as e:
        print(f"Failed to send email: {e}")
        return redirect(url_for('home', message='Failed to send message'))


# Canvas route
@app.route("/canvas")
@login_required
def canvas():
    return render_template('canvas.html')

# 손글씨 계산
@app.route('/predict', methods=['POST'])
def predict():
    try:
        operation = BytesIO(base64.urlsafe_b64decode(request.form['operation']))
        operation = CNN.predict(operation)

        # √ 기호를 처리합니다.
        n_operation = calculate_sqrt(operation)

        # 수식을 계산합니다.
        result, explanation = calculate_operation(n_operation)

        return json.dumps({
            'operation': operation,
            'solution': result,
            'explanation': explanation
        })
    except Exception as e:
        logger.error(f"Error in predict function: {e}")
        return json.dumps({
            'error': "처리 중 오류가 발생했습니다. 나중에 다시 시도해주세요."
        }), 500

if __name__ == "__main__":
    init_database() 
    app.run(debug=False, host='0.0.0.0')

