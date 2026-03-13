# Fantasy League Leaderboard

An algorithmic back end plus animated front end that ranks fantasy football teams weekly and through playoffs.

## Screenshots
![Season standings](Images/UI%20Season%20Standings.png)
![Current week standings](Images/UI%20Current%20Week%20Standings.png)

## How scoring works
- Regular season: each week, total fantasy points are summed per team. Highest points earns 9, then 8, 7 … down to 0 for last place.
- Playoffs: top 4 cumulative-win teams enter the winners bracket; bottom 6 enter the losers bracket.
- Elimination: each playoff week the lowest scorer in winners is eliminated; the highest scorer in losers is eliminated. Play continues until one winner and one loser remain.

## Project layout
- `Backend/App.py` — Flask API (Sleeper data fetch, scoring, bracket logic).
- `Backend/User.py` — user model.
- `Frontend/src` — Vite + React/TypeScript UI with animated tables.
- `Backend/tests` — pytest suite.

## Run locally
Backend:
- `cd Backend`
- (Optional) create venv, `pip install flask flask-cors requests pytest`
- `python3 App.py` (starts on `http://127.0.0.1:5000`)

Frontend:
- `cd Frontend`
- `npm install`
- `npm run dev` (Vite serves at `http://localhost:5173`)

API base is hard-coded to `http://localhost:5000` in `src/App.tsx`; adjust if needed.

## API endpoints
- `GET /users` — season standings with wins, losses, bracket, elimination info.
- `GET /users?week=current` — current-week ranks (wins/losses fields).

## Testing
- Backend tests: `cd Backend && pytest -q`
