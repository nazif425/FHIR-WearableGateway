import sys, os, random, base64, hashlib, secrets, random, string, requests

from os import environ
from flask import Flask, request, jsonify, abort, render_template, Response, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.sql import func
from models import db, User
from fhir.resources.patient import Patient
from fhir.resources.humanname import HumanName
from datetime import date
basedir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(basedir,'python-fitbit'))
from fitbit.api import Fitbit



#Setup FLASK App
app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345678@127.0.0.1:3306/pghd_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)
app.secret_key = b"w#\x95\xa2\xb0\xa1`\x04w\x16l&J\xc5G\xa4\xbaZX\xba\xf6\xf5\x8c\xe9\xa0\xaa'\x81\xe6\xd2?\x83"

# FITBIT 
CLIENT_ID = '238ZN5'
CLIENT_SECRET = '2c1f3aa0a96bc067d34714c281b953d0'
REDIRECT_URI = 'http://127.0.0.1:5000/wearables/registration/fitbit'
OAUTH_URL = 'https://api.fitbit.com/oauth2/token'

# OPENMRS
OPENMRS_BASE_URL = 'http://127.0.0.1:8081/openmrs'
OPENMRS_FHIR_VERSION = 'R4'
OPENMRS_FHIR_API = f'{OPENMRS_BASE_URL}/ws/fhir2/{OPENMRS_FHIR_VERSION}/'

def store_new_tokens(data):
  if data.get("access_token", None):
    print(data['user_id'])
    users = User.query.filter(User.platform_user_id==data['user_id'])
    if users.count() != 0:
      user = users.all()[0]
      user.access_token = data['access_token']
      user.refresh_token = data['refresh_token']
      db.session.add(user)
      db.session.commit()

@app.route('/', methods=['GET'])
def index():
  return render_template('index.html')

@app.route('/wearables/registration', methods=['GET'])
def register():
  return render_template('register.html')

@app.route('/wearables/registration/fitbit', methods=['GET'])
def fitbit_authorization():
  code = request.args.get("code", None)
  state = request.args.get("state", None)
  
  if not code or not state:


    # Generate a code verifier and code challenge
    code_verifier = secrets.token_urlsafe(80)
    session['code_verifier'] = code_verifier
    code_verifier_hash = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(code_verifier_hash).rstrip(b'=').decode()
    state = '2q2l294e7168333p322k1o680a3u2l22'
    
    # Redirect the user to the Fitbit
    auth_url = f'https://www.fitbit.com/oauth2/authorize?response_type=code&client_id={CLIENT_ID}'\
                f'&scope=activity+cardio_fitness+electrocardiogram+heartrate+location+nutrition'\
                f'+oxygen_saturation+profile+respiratory_rate+settings+sleep+social+temperature+weight'\
                f'&code_challenge={code_challenge}&code_challenge_method=S256&state={state}'
    
    print(auth_url, "len of challenge:", len(code_challenge))
    html_response = '<h3>To integrate your fitbit watch with our service, your permission is required to grant access to data from your fitbit account.<br><br>Click continue to proceed</h3>'\
                    '<button onclick="window.location.href=' + f"'{auth_url}'" + '">Continue</button>'
    
    print(html_response)
    return Response(html_response) # 'register_fitbit.html'
  else:
    print(session['code_verifier'])
    if not session['code_verifier']:
      return Response('<h2>Something went Wrong</h2>', status=400) 
    
    # Retrieve access and refresh token
    token64 = base64.urlsafe_b64encode((CLIENT_ID + ':' + CLIENT_SECRET).encode()).decode().rstrip('=')
    print('this is token in 64 bit', token64, sep='\n')
    bearer_token = 'Basic {0}'.format(token64)
    
    print(state, code, bearer_token, sep="\n")
    
    res = requests.post(
      OAUTH_URL,
      data={
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "code": code,
        "code_verifier": session['code_verifier'],
      },
      headers={
        "Authorization": bearer_token,
        "Content-Type": "application/x-www-form-urlencoded"
      })
    if res.status_code != 201:
      return Response('<h2>Something went wrong. Try again later</h2><p><a href="/">Home</a></p>', status=400)
    data = res.json()
    print(data)
    
    if data.get("access_token", None):
      users = User.query.filter(User.platform_user_id==data['user_id'])
      user = users.first()
      if not user:
        id = data['user_id']
        del data['user_id']
        del data['token_type']
        data['platform'] = 'Fitbit'
        data['platform_user_id'] = id
        user = User(**data)
        db.session.add(user)
        db.session.commit()
      
      if user.patient_id == None:
        fitbit = Fitbit(
          CLIENT_ID,
          CLIENT_SECRET,
          access_token=data['access_token'],
          refresh_token=data['refresh_token'],
          refresh_cb=store_new_tokens)
        profile = fitbit.user_profile_get(user_id=user.platform_user_id)
        print(profile)
        EHR_system = 'openmrs'
        profile_pid = user.id

        html_response = f"<h2>Hi {profile['user']['firstName']}, You are almost there. <br>Select the healthcare system use by your health centre."\
                        f'</h2><ul><li><a href="/user_identification?EHR_system=openmrs&pid={profile_pid}">Openmrs</a></li></ul>' 
        return Response(html_response)
      else:
        # user already exist
        return Response('<h2>Oh, it seems your Fitbit account is already linked to our platform. '\
                        'But that is just fine anyway.</h2><p><a href="/">Home</a></p>')
    else:
      return Response('<h2>Something went wrong. Try again later</h2><p><a href="/">Home</a></p>', status=400)
    # Save access_token and refresh_token
    # fitbit.client.save_tokens(data.get('access_token', None), data.get('refresh_token', None))



@app.route('/user_identification', methods=['GET','POST'])
def identify_user():
  # verify if user already exist on the EHR SYSTEM

  if request.method == 'GET':
    pid = request.args.get('pid', None)
    EHR_system = request.args.get('EHR_system', None)
    try:
      user = User.query.get(pid)
    except:
      print(f'id {pid} not found')
      return Response('<h1>Something went wrong</h1>')
    return Response(
        f'<h2>Please enter your Patient ID to link you to your {EHR_system} system. '\
        'If you do not have, you can request for from your healthcare providers</h2>'\
        '<form method="post" action="/user_identification" target="_self">'\
        '<label>Patient ID:</label><br><input type="text" name="patient_id"><br>'\
        f'<input type="hidden" name="pid" value="{pid}"><input type="hidden" name="EHR_system" value="{EHR_system}">'\
        '<input type="submit"></form>')
  else:
    patient_id = request.form["patient_id"]
    pid = request.form["pid"]
    EHR_system = request.form["EHR_system"]
    bearer_token = 'Basic YWRtaW46QWRtaW4xMjM='
    if EHR_system == "openmrs":
      res = requests.get(
        OPENMRS_FHIR_API + 'Patient?identifier=' + patient_id,
        headers={
          "Authorization": bearer_token,
          "Content-Type": "application/fhir+json"
        })
      if res.status_code != '200':
        return Response('<h2>Something went wrong. Try again later</h2><p><a href="/">Home</a></p>', status=400)
      data = res.json()
      print(data)
      if data['total'] == 1:
        try:
          user = User.query.get(pid)
          user.patient_id = patient_id
          db.session.add(user)
          db.session.commit()
        except:
          print(f'id {pid} not found')
          return Response('<h1>Patient ID is invalid. try again later</h1><a href="/">Home</a>', status=400)
      return Response('<h2>Registration successful</h2><p><a href="/">Home</a></p>')
  
"""  
  # Exchange the authorization code for an access token
  access_token, refresh_token = fitbit.client.fetch_access_token(authorization_code, code_verifier=code_verifier)
  
  # Save the access token and refresh token for future use
  fitbit.client.save_tokens(access_token, refresh_token)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#



# Or specify port manually:

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=5001)
"""

# Default port:
if __name__ == '__main__':
    app.run(debug=True)