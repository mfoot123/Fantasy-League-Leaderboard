from flask import Flask, jsonify
from flask_cors import CORS
import requests
from User import User

app = Flask(__name__)
CORS(app)

LEAGUE_ID = "1257085186806382592"

# id, User
users_dict: dict[str, User] = {}
# roster id, user id
roster_id_lookup_table: dict[str, str] = {}

rankings: list[User] = []

def get_current_nfl_week():
    nfl_state_url = "https://api.sleeper.app/v1/state/nfl"
    response = requests.get(nfl_state_url)

    if response.status_code == 200:
        data = response.json()
        return int(data["week"])
    else:
        print(f"Failed to fetch NFL state: {response.status_code}")
        return None

def create_user_dictionary(users):
    for user in users:
        newUser = User(
            display_name=user.get("display_name"),
            user_id=user.get("user_id"),
            team_name=user.get("metadata", {}).get("team_name"),
            league_id=LEAGUE_ID
        )

        users_dict[newUser.user_id] = newUser

def determine_user_roster_numbers():
    rosters_url = "https://api.sleeper.app/v1/league/" + LEAGUE_ID + "/rosters"
    rosters_reponse = requests.get(rosters_url)

    if rosters_reponse.status_code == 200:
        rosters = rosters_reponse.json()
        for roster in rosters:
            user_id = roster["owner_id"]
            if users_dict[user_id]:
                users_dict[user_id].roster_id = roster["roster_id"]
                roster_id_lookup_table[roster["roster_id"]] = user_id

    else:
        print(f"Rosters request failed with status code {rosters_reponse.status_code}")

def calculate_weekly_points(week: int):
    matchups_url = f"https://api.sleeper.app/v1/league/{LEAGUE_ID}/matchups/{week}"
    matchups_response = requests.get(matchups_url)

    if matchups_response.status_code == 200:
        matchups = matchups_response.json()
        for matchup in matchups:
            current_user = users_dict[roster_id_lookup_table[matchup.get("roster_id")]]
            current_user.points_per_week[week] = matchup.get("points", 0.0)

    else:
        print(f"Failed to fetch matchups for week {week} (status code {matchups_response.status_code})")
        return None
    
def set_season_rankings(users_dict):
    for week in range(1, get_current_nfl_week() + 1):
        calculate_weekly_points(week)

        rankings = sorted(
            users_dict.values(),
            key=lambda u: u.points_per_week[week],
            reverse=False
        )  

        for i in range(len(users_dict)):
            rankings[i].wins += i

def get_users_wins():
    users_url = f"https://api.sleeper.app/v1/league/{LEAGUE_ID}/users"
    users_response = requests.get(users_url)
    if users_response.ok:
        create_user_dictionary(users_response.json())
        determine_user_roster_numbers()
        set_season_rankings(users_dict)

        return {user.display_name: user.wins for user in users_dict.values()}
    else:
        print("Failed to fetch users")
        return {}

@app.route("/users", methods=["GET"])
def get_users():
    users_wins = get_users_wins()
    return jsonify(users_wins)

def main():
    get_users_wins()

if __name__ == "__main__":
    app.run(debug=True)
