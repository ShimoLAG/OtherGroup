from flask import Blueprint, render_template, redirect, request, jsonify, flash, url_for, session, abort
import app.models as models
from app.users.forms import UserForm, LoginForm
from config import GOOGLE_CLIENT_ID, GOOGLE_DISCOVERY_URL, GOOGLE_CLIENT_SECRET
import os
import json
from urllib.parse import urlencode
from flask_login import LoginManager,current_user,login_required,login_user,logout_user

from pip._vendor import cachecontrol
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from oauthlib.oauth2 import WebApplicationClient

import google.auth.transport.requests
import requests

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

client = WebApplicationClient(GOOGLE_CLIENT_ID)

auth = Blueprint('auth', __name__)

def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"%s Error - %s" % (getattr(form, field).label.text, error), 'error')

def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


# Routes
@auth.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@auth.route('signup_d', methods=['POST', 'GET'])
def signup_d(is_facilitator=False):
    form = UserForm(request.form)
    
    if request.method == 'POST':
        if form.validate_on_submit():
            
            user = models.Users(id=form.idnum.data, email=session["user_email"], \
            name=session["user_fullname"], is_facilitator=is_facilitator, \
            college=form.college.data, course=form.course.data, year_level=form.year_level.data)
            
            try:
                user.add()
            except:
                
                coursefetch = models.CollegeCourse.getcourse()
                courselist = []
                for item in coursefetch:
                    courselist.append(item[0])
            
                form.course.choices = courselist
                flash("Duplicate Error - An account already exists with your ID number, username, or email.")
                return render_template('signup_facilitator.html', form=form)
            session['is_facilitator'] = is_facilitator
            session['user_id'] = form.idnum.data
            session['logged_in'] = True
            return redirect(url_for('routes.home'))
        else:
            
            coursefetch = models.CollegeCourse.getcourse()
            courselist = []
            for item in coursefetch:
                courselist.append(item[0])
        
            form.course.choices = courselist
            flash_errors(form)
            return render_template('signup.html', form=form)
    else:
        
        coursefetch = models.CollegeCourse.getcourse()
        courselist = []
        for item in coursefetch:
            courselist.append(item[0])
        
        form.course.choices = courselist
        return render_template('signup.html', form=form)

@auth.route('signup_facilitator_d', methods=['POST', 'GET'])
def signup_facilitator_d(is_facilitator=True):
    form = UserForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            
            user = models.Users(id=form.idnum.data, email=session["user_email"], \
            name=session["user_fullname"], is_facilitator=is_facilitator, \
            college=form.college.data, course=form.course.data, year_level=form.year_level.data)
            
            try:
                user.add()
            except:
                coursefetch = models.CollegeCourse.getcourse()
                courselist = []
                for item in coursefetch:
                    courselist.append(item[0])
            
                form.course.choices = courselist
                flash("Duplicate Error - An account already exists with your ID number, username, or email.")
                return render_template('signup_facilitator.html', form=form)
            session['user_id'] = form.idnum.data
            session['college'] = form.college.data
            session['course'] = form.course.data
            session['year'] = form.year_level.data
            session['is_facilitator'] = is_facilitator
            session['user_id'] = form.idnum.data
            session['logged_in'] = True
            return redirect(url_for('routes.home'))
        else:
            
            coursefetch = models.CollegeCourse.getcourse()
            courselist = []
            for item in coursefetch:
                courselist.append(item[0])
        
            form.course.choices = courselist
            flash_errors(form)
            return render_template('signup_facilitator.html', form=form)
    else:
        
        coursefetch = models.CollegeCourse.getcourse()
        courselist = []
        for item in coursefetch:
            courselist.append(item[0])
        
        form.course.choices = courselist
        return render_template('signup_facilitator.html', form=form)

@auth.route("callback")
def callback():
    
    code = request.args.get("code")
    params = urlencode({
        'code': code,
        'redirect_uri': "http://127.0.0.1:5555/auth/callback",
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'grant_type': 'authorization_code'
    })

    headers = {'content-type': 'application/x-www-form-urlencoded'}
    token_response = requests.post("https://accounts.google.com/o/oauth2/token", data=params, headers=headers).json()

    userinfo_response = requests.get(f'https://www.googleapis.com/oauth2/v1/userinfo?access_token={token_response.get("access_token")}').json()

    

    if userinfo_response.get("verified_email"):
        user_email = userinfo_response.get("email")
        user_fullname = userinfo_response.get("name")
        profile = userinfo_response.get("picture")
        
    else:
        session.clear()
        return redirect(url_for("routes.landing_page"))

    # put to session the data that we need
    session["user_email"] = user_email
    session["user_fullname"] = user_fullname
    session["profile"] = profile

    # check if user is already signed up
    account_exists = models.Users.login_or_signup(user_email)
    if account_exists:
        # account already registered in the database
        # login code below

        # get id
        session["user_id"], session["is_facilitator"] = models.Users.get_id(user_email)[0]

        session["logged_in"] = True
        
        return redirect(url_for('routes.home'))
    else:
        # ask user for details (signup)
        if session["is_facilitator"]:
            return redirect(url_for('auth.signup_facilitator_d'))
        else:
            return redirect(url_for('auth.signup_d'))

    # session["userinfo_response"] = userinfo_response
    
    

@auth.route('login')
def login():

    #logout_user()
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri="http://127.0.0.1:5555/auth/callback",
        scope=["openid", "email", "profile"],
    )

    session["is_facilitator"] = False
    return redirect(request_uri)

@auth.route('signup')
def signup():

    #logout_user()
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri="http://127.0.0.1:5555/auth/callback",
        scope=["openid", "email", "profile"],
    )

    session["is_facilitator"] = False
    return redirect(request_uri)

@auth.route('signup_facilitator')
def signup_facilitator():

    #logout_user()
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri="http://127.0.0.1:5555/auth/callback",
        scope=["openid", "email", "profile"],
    )

    session["is_facilitator"] = True
    return redirect(request_uri)

@auth.route('view_event')
def view_event():
    event_id = ['1ebc9b6c-87d8-4271-a2ef-7f20b59459c6']
    session['event_id'] = event_id
    return f'Event ID {event_id} set in session.'
