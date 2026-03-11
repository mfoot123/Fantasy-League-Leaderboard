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
# roster id, user id
roster_id_lookup_table: dict[str, str] = {}

rankings: list[User] = []

def get_effective_season_data():
    state_url = "https://api.sleeper.app/v1/state/nfl"
    try:
        resp = requests.get(state_url).json()
        current_year = int(resp.get("season"))
        season_type = resp.get("season_type") 
        current_week = resp.get("week", 1)

        # If off-season, pre-season, or before week 1, look at last year's end
        if season_type in ["off", "pre"] or current_week < 1:
            return current_year - 1, 18 
        
        return current_year, current_week
    except Exception as e:
        print(f"Error determining season: {e}")
        return 2025, 18
    
def get_total_weeks(year):
    url = f"https://api.sleeper.app/v1/nfl/schedule/{year}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return len({game.get("week") for game in data})
    except:
        pass
    return 18

def get_current_nfl_week():
    nfl_state_url = "https://api.sleeper.app/v1/state/nfl"
    response = requests.get(nfl_state_url)

    if response.status_code == 200:
        data = response.json()
        
        if data.get("season_type") != "regular":
            return 18 
            
        return int(data.get("week", 1))
    else:
        print(f"Failed to fetch NFL state: {response.status_code}")
        return 18

def create_user_dictionary(users):
    users_dict.clear()
    roster_id_lookup_table.clear()

    for user in users:
        newUser = User(
            display_name=user.get("display_name"),
            user_id=user.get("user_id"),
            team_name=user.get("metadata", {}).get("team_name"),
            league_id=LEAGUE_ID
        )

        users_dict[newUser.user_id] = newUser

def determine_user_roster_numbers():
    rosters_url = f"https://api.sleeper.app/v1/league/{LEAGUE_ID}/rosters"
    response = requests.get(rosters_url)
    
    if response.status_code == 200:
        for roster in response.json():
            user_id = roster["owner_id"]
            if user_id in users_dict:
                users_dict[user_id].roster_id = roster["roster_id"]
                roster_id_lookup_table[roster["roster_id"]] = user_id

def calculate_weekly_points(target_dict, week: int):
    matchups_url = f"https://api.sleeper.app/v1/league/{LEAGUE_ID}/matchups/{week}"
    matchups_response = requests.get(matchups_url)

    if matchups_response.status_code == 200:
            for matchup in matchups_response.json():
                roster_id = matchup.get("roster_id")
                # Safety check: Only process rosters we know about
                if roster_id in roster_id_lookup_table:
                    user_id = roster_id_lookup_table[roster_id]
                    # Only update if the user is in the target_dict
                    if user_id in target_dict:
                        current_user = target_dict[user_id]
                        current_user.points_per_week[week] = matchup.get("points", 0.0)
    else:
        print(f"Failed to fetch matchups for week {week} (status code {matchups_response.status_code})")
    
def set_season_rankings(dict, min_week, max_week):
    for user in dict.values():
        user.wins = 0

    for week in range(min_week, max_week + 1):
        calculate_weekly_points(dict, week)

        weekly_rankings = sorted(
            dict.values(),
            key=lambda u: u.points_per_week.get(week, 0.0),
            reverse=False
        )
        for i, user in enumerate(weekly_rankings):
            user.wins += i

def set_current_week_rankings(dict):
    for user in dict.values():
        user.wins = 0

    week = get_current_nfl_week()
    calculate_weekly_points(dict, week)

    weekly_rankings = sorted(
        dict.values(),
        key=lambda u: u.points_per_week.get(week, 0.0),
        reverse=False
    )

    for i, user in enumerate(weekly_rankings):
        user.wins += i

def set_winners_and_losers():
    ranked_users = sorted(
            users_dict.values(),
            key=lambda u: (u.wins, sum(u.points_per_week.values())),
            reverse=True
        )
        
    for user in ranked_users[:WINNERS]:
        user.bracket = "winners"
    for user in ranked_users[-LOSERS:]:
        user.bracket = "losers"

def drop_week_extremes_from_brackets(week: int):
    active_winners = [u for u in users_dict.values() if u.bracket == "winners" and not u.is_eliminated]
    if len(active_winners) > 1:
        lowest = min(active_winners, key=lambda u: (u.points_per_week.get(week, 0.0), sum(u.points_per_week.values())))
        lowest.is_eliminated = True
        lowest.eliminated_week = week

    active_losers = [u for u in users_dict.values() if u.bracket == "losers" and not u.is_eliminated]
    if len(active_losers) > 1:
        highest = max(active_losers, key=lambda u: (u.points_per_week.get(week, 0.0), sum(u.points_per_week.values())))
        highest.is_eliminated = True
        highest.eliminated_week = week


def get_users_wins():
    target_year, active_week = get_effective_season_data()
    total_weeks = get_total_weeks(target_year)

    users_url = f"https://api.sleeper.app/v1/league/{LEAGUE_ID}/users"
    users_response = requests.get(users_url)

    if not users_response.ok:
        print("Failed to fetch users")
        return {}

    create_user_dictionary(users_response.json())
    determine_user_roster_numbers()

    playoff_start_week = total_weeks - LOSERS + 1 
    current_active_week = min(active_week, total_weeks)

    reg_season_end = min(current_active_week, playoff_start_week - 1)
    set_season_rankings(users_dict, 1, reg_season_end)

    if current_active_week >= playoff_start_week:
        set_winners_and_losers()

        for week in range(playoff_start_week, current_active_week + 1):
            calculate_weekly_points(users_dict, week)
            drop_week_extremes_from_brackets(week)

    return {
        user.display_name: {
            "wins": user.wins,
            "bracket": user.bracket,
            "is_eliminated": user.is_eliminated,
            "eliminated_week": user.eliminated_week
        } 
        for user in users_dict.values()
    }

@app.route("/users", methods=["GET"])
def get_users():
    week = request.args.get("week")

    if week == "current":
        if not users_dict:
            users_url = f"https://api.sleeper.app/v1/league/{LEAGUE_ID}/users"
            create_user_dictionary(requests.get(users_url).json())
            determine_user_roster_numbers()
            
        set_current_week_rankings(users_dict)
        return jsonify({user.display_name: user.wins for user in users_dict.values()})
    
    else:
        users_data = get_users_wins()
        return jsonify(users_data)

if __name__ == "__main__":
    app.run(debug=True)
