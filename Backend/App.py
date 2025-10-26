import requests

from User import User

from datetime import date

LEAGUE_ID = "1257085186806382592"

# id, User
users_dict: dict[str, User] = {}

# roster id, user id
roster_id_lookup_table: dict[str, str] = {}

rankings: list[User] = []

def calculate_current_nfl_week():
    season_start_date = date(2025, 9, 4)
    today = date.today()
    days_since_start = (today - season_start_date).days
    current_week = str(min((days_since_start // 7) + 1, 18))

    return int(current_week)

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
    for week in range(1, calculate_current_nfl_week() + 1):
        calculate_weekly_points(week)

        rankings = sorted(
            users_dict.values(),
            key=lambda u: u.points_per_week[week],
            reverse=False
        )  

        for i in range(len(users_dict)):
            rankings[i].wins += i

def main():
    users_url = f"https://api.sleeper.app/v1/league/{LEAGUE_ID}/users"
    users_response = requests.get(users_url)
    if users_response.ok:
        create_user_dictionary(users_response.json())
        determine_user_roster_numbers()
        set_season_rankings(users_dict)
    else:
        print("Failed to fetch users")

if __name__ == "__main__":
    main()
