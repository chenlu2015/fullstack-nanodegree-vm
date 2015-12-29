from flask import Flask, render_template,url_for, jsonify, abort, redirect, make_response, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from database_setup import Base, Category, User, CatalogItem
from json import dumps
from datetime import datetime, timedelta



#auth imports
from flask import session as login_session
import random, string

import os
import jwt
from functools import wraps
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(
  open('client_secrets.json','r').read())['web']['client_id']
GOOGLE_SECRET = json.loads(
  open('client_secrets.json','r').read())['web']['client_secret']
TOKEN_SECRET = "1234secret"

app = Flask(__name__)
#engine = create_engine('postgresql+psycopg2://lolitschen:xxxxxxx@localhost/lolitschen')
engine = create_engine('postgresql+psycopg2:///catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
session = DBSession()

#Application Routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.headers.get('Authorization'):
            response = jsonify(message='Missing authorization header')
            response.status_code = 401
            return response

        try:
            payload = parse_token(request)
        except DecodeError:
            response = jsonify(message='Token is invalid')
            response.status_code = 401
            return response
        except ExpiredSignature:
            response = jsonify(message='Token has expired')
            response.status_code = 401
            return response

        g.user_id = payload['sub']

        return f(*args, **kwargs)

    return decorated_function

@app.route("/")
def main():
	return render_template('index.html')

@app.route('/api/v1.0/gconnect',methods=['POST'])
def gconnect():
  # if request.args.get('state')!= login_session['state']:
  #   response = make_response(json.dumps('Invalid state'),401)
  #   response.headers['Content-Type'] = 'application/json'
  #   return response
  code = request.data
  try:
    oauth_flow = flow_from_clientsecrets('client_secrets.json',
      scope='')
    oauth_flow.redirect_uri = 'postmessage'
    credentials = oauth_flow.step2_exchange(code)
  except FlowExchangeError:
    response = make_response(json.dumps('Failed to upgrade auth code'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response
  access_token = credentials.access_token
  url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %access_token)
  h = httplib2.Http()
  result = json.loads(h.request(url, 'GET')[1])
  if result.get('error') is not None:
    response = make_response(json.dumps(result.get('error')),50)
    response.headers['Content-Type'] = 'application/json'
    return response
  gplus_id = credentials.id_token['sub']
  if result['user_id'] != gplus_id:
    response = make_response(json.dumps("token's user ID doesnt match"),401)
    response.headers['Content-Type'] = 'application/json'
    return response
  if result['issued_to'] != CLIENT_ID:
    response = make_response(json.dumps("Token's client ID doesnt match"), 401)
    response.headers['Content-Type'] = 'application/json'
    return response
  stored_credentials = login_session.get('credentials')
  stored_gplus_id = login_session.get('gplus_id')
  if stored_credentials is not None and gplus_id == stored_gplus_id:
    response = make_response(json.dumps('current user is already connected'),200)
    response.headers['Content-Type'] = 'application/json'
    return response

  login_session['credentials'] = credentials
  login_session['gplus_id'] = gplus_id

  userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
  params = {'access_token': credentials.access_token, 'alt':'json'}
  answer = requests.get(userinfo_url, params=params)
  data = json.loads(answer.text)

  login_session['username'] = data["name"]
  login_session['picture'] = data["picture"]
  login_session['email'] = data["email"]

  output = ''
  output += 'hello: </br>'
  output += login_session['username']
  # flash("you are now logged in as %s" %login_session['username'])
  return output


# API Routes
@app.route ('/api/v1.0/getstate', methods=['GET'])
def showLogin():
	state = ''.join(random.choice(string.ascii_uppercase + 
		string.digits) for x in xrange(32))
	login_session['state'] = state
	return "the current sesion state is %s" %login_session['state']



@app.route("/api/v1.0/categories/", methods=['GET'])
def get_categories():
		DBSession = sessionmaker(bind = engine)
		session = DBSession()
		categories = session.query(Category).all()
		data = []
		for c in categories:
			print c
			data.append(c.serialize())

		#print data
		session.close()
		return jsonify({'categories':data})

@app.route("/api/v1.0/categories/new/", methods = ['GET', 'POST'])
def new_category():
	if request.method == 'POST':
		#print 'name' in request.form
		if not request.form or not 'name' in request.form:
			abort(400)
		newCategory = Category(name = request.form['name'], description=request.form.get('description',""))
		DBSession = sessionmaker(bind = engine)
		session = DBSession()
		session.add(newCategory)
		session.commit()
		session.close()
		#print 'closing session'
		return redirect(url_for('get_categories'), code=302)
	elif request.method == 'GET':
		return render_template('new_category_form.html')
	else:
		abort(400)

@app.route("/api/v1.0/categories/<int:category_id>/", methods=['GET'])
def get_category(category_id):
	DBSession = sessionmaker(bind = engine)
	session = DBSession()
	try:
		result = session.query(Category).filter_by(id=category_id).one()
		return jsonify({'category':result.serialize()})
	except NoResultFound:
		abort(404)
	finally:
		session.close()
		#print 'closing session'
@app.route("/api/v1.0/categories/<int:category_id>/edit/", methods=['GET', 'POST'])
def edit_category(category_id):
	if request.method == 'GET':
		DBSession = sessionmaker(bind = engine)
		session = DBSession()
		try:
			result = session.query(Category).filter_by(id=category_id).one()
			return render_template('edit_category.html', category = result)
		except NoResultFound:
			abort(404)
		finally:
			session.close()
	elif request.method == 'POST':
		DBSession = sessionmaker(bind = engine)
		session = DBSession()
		try:
			result = session.query(Category).filter_by(id=category_id).one()
			result.name = request.form['name']
			result.description = request.form['description']
			session.add(result)
			session.commit()
			return redirect(url_for('get_category',category_id=category_id),code=302)
		except NoResultFound:
			abort(404)
		finally:
			session.close()

		return 'test'
	else:
		abort(400)

@app.route('/api/v1.0/auth/google', methods=['POST'])
def google():
    access_token_url = 'https://accounts.google.com/o/oauth2/token'
    people_api_url = 'https://www.googleapis.com/plus/v1/people/me/openIdConnect'

    payload = dict(client_id=request.json['clientId'],
                   redirect_uri=request.json['redirectUri'],
                   client_secret=GOOGLE_SECRET,
                   code=request.json['code'],
                   grant_type='authorization_code')

    # Step 1. Exchange authorization code for access token.
    r = requests.post(access_token_url, data=payload)
    token = json.loads(r.text)
    headers = {'Authorization': 'Bearer {0}'.format(token['access_token'])}

    # Step 2. Retrieve information about the current user.
    r = requests.get(people_api_url, headers=headers)
    profile = json.loads(r.text)

    DBSession = sessionmaker(bind = engine)
    session = DBSession()
    try:
    	user = session.query(User).filter_by(google=profile['sub']).first()
    finally:
    	session.close()
    if user:
        token = create_token(user)
        return jsonify(token=token)

    DBSession = sessionmaker(bind = engine)
    session = DBSession()
    u = User(google=profile['sub'],
             name=profile['name'])
    session.add(u)
    session.commit()
    token = create_token(u)
    # print token
    return jsonify(token=token)

def create_token(user):
    payload = {
        'sub': user.id,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=14)
    }
    # token = jwt.encode(payload, app.config['TOKEN_SECRET'])
    token = jwt.encode(payload, TOKEN_SECRET)
    return token.decode('unicode_escape')


def parse_token(req):
    token = req.headers.get('Authorization').split()[1]
    # return jwt.decode(token, app.config['TOKEN_SECRET'])
    return jwt.decode(token, TOKEN_SECRET)




# @app.route("/api/v1.0/categories/<int:category_id>/delete/", methods=['GET'])

#error handling
@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error':'Not Found'}), 404)

if __name__ == "__main__":
	app.secret_key = 'super secret key'
	app.config['SESSION_TYPE'] = 'filesystem'

	app.debug = True
	app.run(host='0.0.0.0',port=8080)


#helper functions

def to_json(model):
    """ Returns a JSON representation of an SQLAlchemy-backed object.
    """
    json = {}
    json['fields'] = {}
    json['pk'] = getattr(model, 'id')

    for col in model._sa_class_manager.mapper.mapped_table.columns:
        json['fields'][col.name] = getattr(model, col.name)

    return dumps([json])
