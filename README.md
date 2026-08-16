# Fantasy League Leaderboard

An algorithmic back end plus animated front end that ranks fantasy football teams weekly and through playoffs.

## How scoring works
- Regular season: each week, total fantasy points are summed per team. Highest points earns 9, then 8, 7 … down to 0 for last place.
- Playoffs: top 4 cumulative-win teams enter the winners bracket; bottom 6 enter the losers bracket.
- Elimination: each playoff week the lowest scorer in winners is eliminated; the highest scorer in losers is eliminated. Play continues until one winner and one loser remain.

## Project layout
- `src` — Vite + React/TypeScript UI with animated tables.
- `public` — static assets for the frontend.
- Separate Vercel project — Flask API (Sleeper data fetch, scoring, bracket logic).

## Run locally
Frontend:
- `npm install`
- `npm run dev` (Vite serves at `http://localhost:5173`)

The frontend expects a public backend URL via `VITE_API_BASE_URL` in `src/App.tsx`.
For local development, you can set:
- `VITE_API_BASE_URL=http://127.0.0.1:5000`

If the API is hosted elsewhere, set it to that host instead.

## API endpoints
- `GET /users?year=2025` — season standings for a selected year, with wins, losses, bracket, and elimination info.
- `GET /users?week=current&year=2025` — current-week rank data for that year, including the resolved `week` number and `rankings` (wins/losses fields).

The available year tabs are defined in `src/App.tsx`. Add a year there when its season is ready.

## Testing
- Frontend build verification: `npm run build`
- Backend tests run in the separate API repo/project

## Screenshots
![Season standings](Images/UI%20Season%20Standings.png)
![Current week standings](Images/UI%20Current%20Week%20Standings.png)
