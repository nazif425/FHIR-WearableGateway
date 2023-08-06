from flask import Flask, request, jsonify, abort, render_template, Response, flash, redirect, url_for
import base64
import  requests

app = Flask(__name__)
#client = app.test_client
@app.route('/', methods=["GET"])
def index():
  return Response('<a href="https://emr.vlabnigeria.org/oauth2/default/authorize?client_id=qZ45JJ2fGttCHNOtGIOwSAxKBfdkUXim-N2FVf-nZSo&response_type=code&scope=launch%2Fpatient%20openid%20fhirUser%20offline_access%20patient%2FAllergyIntolerance.read%20patient%2FCarePlan.read%20patient%2FCareTeam.read%20patient%2FCondition.read%20patient%2FDevice.read%20patient%2FDiagnosticReport.read%20patient%2FDocumentReference.read%20patient%2FEncounter.read%20patient%2FGoal.read%20patient%2FImmunization.read%20patient%2FLocation.read%20patient%2FMedication.read%20patient%2FMedicationRequest.read%20patient%2FObservation.read%20patient%2FOrganization.read%20patient%2FPatient.read%20patient%2FPractitioner.read%20patient%2FProcedure.read%20patient%2FProvenance.read&redirect_uri=http://localhost:8000/home&state=9512151b-e5ca-cb4b-1ddc-aaf4cd8c6ecc">click me</a>')

@app.route('/home', methods=['GET'])
def home():
  client_id = 'qZ45JJ2fGttCHNOtGIOwSAxKBfdkUXim-N2FVf-nZSo'
  client_secret = '4JsIz_w77qqMfuKCetLQtBX32Z_8ZfbJsSd2-ReIUkI9rbPxrK3PpgjVCajbgfwN6Qrl5f2HlZJOXWL_uc7J2g'
  token64 = base64.urlsafe_b64encode((client_id + ':' + client_secret).encode()).decode().rstrip('=')
  print('this is token in 64 bit', token64, sep='\n')
  bearer_token = 'Basic {0}'.format(token64)
  code = request.args.get("code", None)
  state = request.args.get("state", None)
  print(state, code, bearer_token, sep="\n")
  
  res = requests.post(
    "https://emr.vlabnigeria.org/oauth2/default/token",
    data={
      "grant_type": "authorization_code",
      "client_id": client_id,
      "redirect_uri": "http://localhost:8000/home",
      "code": code
    },
    headers={
      "Authorization": bearer_token
    })
  data = res.json()
  print(data)
  return Response(data)
  

if  __name__ == '__main__':
  app.run(host="localhost", port=8000)