# Fantasy League Leaderboard

An algorithmic back end plus animated front end that ranks fantasy football teams weekly and through playoffs.

## How scoring works
- Regular season: each week, total fantasy points are summed per team. Highest points earns 9, then 8, 7 … down to 0 for last place.
- Playoffs: top 4 cumulative-win teams enter the winners bracket; bottom 6 enter the losers bracket.
- Elimination: each playoff week the lowest scorer in winners is eliminated; the highest scorer in losers is eliminated. Play continues until one winner and one loser remain.

## Project layout
- `api/App.py` — Flask API (Sleeper data fetch, scoring, bracket logic).
- `api/User.py` — user model.
- `src` — Vite + React/TypeScript UI with animated tables.
- `api/tests` — pytest suite.

## Run locally
Backend:
- `cd api`
- (Optional) create venv, `pip install flask flask-cors requests pytest`
- `python3 App.py` (starts on `http://127.0.0.1:5000`)

Frontend:
- `npm install`
- `npm run dev` (Vite serves at `http://localhost:5173`)

By default the frontend calls `http://127.0.0.1:5000` in `src/App.tsx`. Set
`VITE_API_BASE_URL` when the API is hosted elsewhere.

## API endpoints
- `GET /users?year=2025` — season standings for a selected year, with wins, losses, bracket, and elimination info.
- `GET /users?week=current&year=2025` — current-week rank data for that year, including the resolved `week` number and `rankings` (wins/losses fields).

The available year tabs are defined in `src/App.tsx`. Add a year there when its season is ready.

## Testing
- Backend tests: `cd Backend && pytest -q`

## Screenshots
![Season standings](Images/UI%20Season%20Standings.png)
![Current week standings](Images/UI%20Current%20Week%20Standings.png)
