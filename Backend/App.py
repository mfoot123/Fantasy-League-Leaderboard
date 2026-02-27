from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from User import User

app = Flask(__name__)
CORS(app)

LEAGUE_ID = "1257085186806382592"
PEOPLE_IN_LEAGUE = 10
LOSERS = 6
WINNERS = 4
YEAR = 2025

# id, User
users_dict: dict[str, User] = {}
winners_dict: dict[str, User] = {}
losers_dict: dict[str, User] = {}
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

def calculate_weekly_points(dict, week: int):
    matchups_url = f"https://api.sleeper.app/v1/league/{LEAGUE_ID}/matchups/{week}"
    matchups_response = requests.get(matchups_url)

    if matchups_response.status_code == 200:
        matchups = matchups_response.json()
        for matchup in matchups:
            current_user = dict[roster_id_lookup_table[matchup.get("roster_id")]]
            current_user.points_per_week[week] = matchup.get("points", 0.0)

    else:
        print(f"Failed to fetch matchups for week {week} (status code {matchups_response.status_code})")
        return None
    
def set_season_rankings(dict, min_week, current_week):
    for user in dict.values():
        user.wins = 0

    for week in range(min_week, current_week + 1):
        calculate_weekly_points(dict, week)

        rankings = sorted(
            dict.values(),
            key=lambda u: u.points_per_week[week],
            reverse=False
        )  

        for i in range(len(dict)):
            rankings[i].wins += i

    return dict

def set_current_week_rankings(dict):
    for user in dict.values():
        user.wins = 0

    week = get_current_nfl_week()

    calculate_weekly_points(dict, week)

    rankings = sorted(
        users_dict.values(),
        key=lambda u: u.points_per_week[week],
        reverse=False
    )  

    for i in range(len(users_dict)):
        rankings[i].wins += i

def get_number_of_weeks_in_season():
    url = f"https://api.sleeper.app/v1/nfl/schedule/{year}"
    resp = requests.get(url).json()
    weeks = sorted({game["week"] for game in resp})
    return len(weeks)

def set_winners_and_losers(users_dict):
    global winners_dict, losers_dict

    ranked_users = sorted(
        users_dict.values(),
        key=lambda u: u.wins,
        reverse=True
    )

    winners_dict = {user.user_id: user for user in ranked_users[:LOSERS]}
    losers_dict = {user.user_id: user for user in ranked_users[-WINNERS:]}

def drop_week_extremes_from_brackets(week: int):
    """Remove lowest-scoring winner and highest-scoring loser for a given week."""
    global winners_dict, losers_dict

    if winners_dict:
        lowest_winner = min(
            winners_dict.values(),
            key=lambda u: u.points_per_week.get(week, 0.0)
        )
        winners_dict.pop(lowest_winner.user_id, None)

    if losers_dict:
        highest_loser = max(
            losers_dict.values(),
            key=lambda u: u.points_per_week.get(week, 0.0)
        )
        losers_dict.pop(highest_loser.user_id, None)


def get_users_wins():
    users_url = f"https://api.sleeper.app/v1/league/{LEAGUE_ID}/users"
    users_response = requests.get(users_url)
    if users_response.ok:
        create_user_dictionary(users_response.json())
        determine_user_roster_numbers()
        current_week = get_current_nfl_week()

        # preseason
        if(current_week <=  get_number_of_weeks_in_season() - LOSERS):
            users_dict = set_season_rankings(users_dict, 1, current_week)
        # post season
        else:
            users_dict = set_season_rankings(users_dict, 1, get_number_of_weeks_in_season() - LOSERS)
            set_winners_and_losers(users_dict)
            if(get_current_nfl_week() <= 17):
                for i in range(get_current_nfl_week(), get_current_nfl_week() - get_number_of_weeks_in_season() + LOSERS):
                    calculate_weekly_points(losers_dict, i)
                    calculate_weekly_points(winners_dict, i)
                    drop_week_extremes_from_brackets(i)
            # season is over
            else:
                for i in range(12, 17 - get_number_of_weeks_in_season() + LOSERS):
                    calculate_weekly_points(losers_dict, i)
                    calculate_weekly_points(winners_dict, i)
                    drop_week_extremes_from_brackets(i)

        return {user.display_name: user.wins for user in users_dict.values()}
    
    else:
        print("Failed to fetch users")
        return {}

@app.route("/users", methods=["GET"])
def get_users():
    week = request.args.get("week")

    # current week view
    if week == "current":
        set_current_week_rankings(users_dict)
        return jsonify({user.display_name: user.wins for user in users_dict.values()})
    
    # season view
    else:
        users_wins = get_users_wins()
        return jsonify(users_wins)

def main():
    get_users_wins()

if __name__ == "__main__":
    app.run(debug=True)
