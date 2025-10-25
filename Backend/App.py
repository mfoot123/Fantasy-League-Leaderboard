import requests

from User import User

from datetime import date, timedelta

def CalculateCurrentNflWeek():

    season_start_date = date(2025, 9, 4)
    today = date.today()

    days_since_start = (today - season_start_date).days

    current_week = str(min((days_since_start // 7) + 1, 18))

    return current_week

def ProcessUsersFromJson(users):
    usersList = []
    for user in users:
        newUser = User(
            display_name=user.get("display_name"),
            user_id=user.get("user_id"),
            team_name=user.get("metadata", {}).get("team_name")
        )

        usersList.append(newUser)

    return usersList

league_id = "1257085186806382592"

users_url = "https://api.sleeper.app/v1/league/" + league_id  + "/users"
users_response = requests.get(users_url)

if users_response.status_code == 200:
    users = users_response.json()
    usersList = ProcessUsersFromJson(users)

else:
    print(f"Request failed with status code {users_response.status_code}")

matchups_url = "https://api.sleeper.app/v1/league/" + league_id + "/matchups/" + CalculateCurrentNflWeek()
matchups_response = requests.get(matchups_url)

if matchups_response.status_code == 200:
    matchups = matchups_response.json()
    for matchup in matchups:
        print(matchup)

else:
    print(f"Request failed with status code {users_response.status_code}")