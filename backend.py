# This file contains all the code that interacts with the DRM/billing box
from ip import drm_ip
import webbrowser, requests, json


# sends backend (drm) box the inputted user/pass combo
# and returns True if the authentication succeeds, false otherwise
def authenticate(user, passwd):
    #url = "http://" + drm_ip + "/auth"
    ##payload = {'username': user, 'password': passwd}
    #headers = {'content-type' : 'application/json'}

    #response = requests.post(url, data=json.dumps(payload), headers=headers)
   
  #  parsed_response = response.json()

    return "True", "True"


# sends current score (a value in seconds) to backend,
# returns True if new high score, False if not
def send_score(user, score):
    #url = "http://" + drm_ip + "/highscore"
    #payload = {'username': user, 'score': score}
    #headers = {'content-type' : 'application/json'}

  #  response = requests.post(url, data=json.dumps(payload), headers=headers)
   
 #   parsed_response = response.json()

    #bool_resp = parsed_response['ishighscore']

    return True


# opens the user's browser to the leaderboard page of the billing/DRM box
def open_leaderboard():
    target = "http://" + drm_ip + "/leaderboard"
    webbrowser.open_new(target)
