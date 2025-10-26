class User:
    def __init__(self, display_name: str, user_id: str, team_name: str, league_id: str):
        self.display_name = display_name
        self.user_id = user_id
        self.team_name = team_name
        self.roster_id: int | None = None
        self.points_per_week: dict[int, float] = {}
        self.wins: int = 0
