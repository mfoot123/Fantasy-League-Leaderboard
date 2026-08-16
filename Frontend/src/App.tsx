import { useEffect, useState } from "react";
import "./App.css";

const AVAILABLE_YEARS = [2025, 2026];
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:5000";

type WeekWins = Record<
  string,
  {
    wins: number;
    losses: number;
  }
>;

type WeekRankingsResponse = {
  week: number | null;
  rankings: WeekWins;
};

type SeasonUser = {
  wins: number;
  losses: number;
  bracket: "winners" | "losers" | null;
  is_eliminated: boolean;
  eliminated_week: number | null;
};

type SeasonWins = Record<string, SeasonUser>;

async function fetchApi<T>(path: string, signal: AbortSignal): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, { signal });

  if (!response.ok) {
    throw new Error(`Request failed with HTTP ${response.status}`);
  }

  return response.json() as Promise<T>;
}

function App() {
  const [seasonWins, setSeasonWins] = useState<SeasonWins>({});
  const [weekWins, setWeekWins] = useState<WeekWins>({});
  const [currentWeek, setCurrentWeek] = useState<number | null>(null);
  const [selectedYear, setSelectedYear] = useState(AVAILABLE_YEARS[0]);
  const [seasonError, setSeasonError] = useState<string | null>(null);
  const [weekError, setWeekError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    const query = `year=${selectedYear}`;
    let isCurrentRequest = true;

    setSeasonError(null);
    setWeekError(null);

    fetchApi<SeasonWins>(`/users?${query}`, controller.signal)
      .then(data => {
        if (isCurrentRequest) setSeasonWins(data);
      })
      .catch(err => {
        if (err.name !== "AbortError" && isCurrentRequest) {
          console.error("Error fetching season data:", err);
          setSeasonError("Could not load season standings. Check that the backend is running.");
        }
      });

    fetchApi<WeekRankingsResponse>(`/users?week=current&${query}`, controller.signal)
      .then(data => {
        if (isCurrentRequest) {
          setWeekWins(data.rankings);
          setCurrentWeek(data.week);
        }
      })
      .catch(err => {
        if (err.name !== "AbortError" && isCurrentRequest) {
          console.error("Error fetching current week data:", err);
          setWeekError("Could not load current-week rankings. Check that the backend is running.");
        }
      });

    return () => {
      isCurrentRequest = false;
      controller.abort();
    };
  }, [selectedYear]);

  const sortedSeason = Object.entries(seasonWins).sort(
    (a, b) => b[1].wins - a[1].wins
  );

  // lower rank number = better, so sort ascending
  const sortedWeek = Object.entries(weekWins).sort(
    (a, b) => a[1].wins - b[1].wins
  );

  const activeBracketUsers = Object.values(seasonWins).filter(
    info => info.bracket !== null && !info.is_eliminated
  );
  const hasFinalists =
    activeBracketUsers.length === 2 &&
    activeBracketUsers.some(info => info.bracket === "winners") &&
    activeBracketUsers.some(info => info.bracket === "losers");

  function getSeasonStatus(info: SeasonUser) {
    if (hasFinalists && !info.is_eliminated) {
      return info.bracket === "winners" ? "Winner" : "Loser";
    }

    if (info.is_eliminated) {
      return `Eliminated (week ${info.eliminated_week ?? "?"})`;
    }

    return "Active";
  }

  return (
    <div className="page">
      <header className="hero">
        <div className="hero__pill">Live Synced</div>
        <h1>Fantasy League Leaderboard</h1>
      </header>

      <nav className="year-tabs" aria-label="Season year">
        <div className="year-tabs__list" role="tablist">
          {AVAILABLE_YEARS.map(year => (
            <button
              key={year}
              className={`year-tabs__tab ${selectedYear === year ? "is-active" : ""}`}
              role="tab"
              type="button"
              aria-selected={selectedYear === year}
              onClick={() => setSelectedYear(year)}
            >
              {year}
            </button>
          ))}
        </div>
      </nav>

      <section className="panel">
        <div className="panel__title">
          <h2>{selectedYear} Season Standings</h2>
        </div>
        <table className="table card table-card">
          <thead>
            <tr>
              <th>User</th>
              <th>Total Wins</th>
              <th>Total Losses</th>
              <th>Bracket</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {seasonError ? (
              <tr>
                <td className="table-message" colSpan={5}>{seasonError}</td>
              </tr>
            ) : sortedSeason.map(([user, info], idx) => (
              <tr
                key={user}
                className="row-animate"
                style={{ animationDelay: `${idx * 60}ms` }}
              >
                <td>{user}</td>
                <td>{info.wins}</td>
                <td>{info.losses}</td>
                <td>
                  {info.bracket ? (
                    <span className={`badge ${info.bracket}`}>
                      {info.bracket}
                    </span>
                  ) : (
                    "—"
                  )}
                </td>
                <td
                  className={`status ${info.is_eliminated
                    ? "eliminated"
                    : hasFinalists && info.bracket === "winners"
                      ? "winner"
                      : hasFinalists && info.bracket === "losers"
                        ? "loser"
                        : ""
                    }`}
                >
                  {getSeasonStatus(info)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="panel">
        <div className="panel__title">
          <h2>
            {selectedYear} Current Week Ranking
            {currentWeek !== null ? ` — Week ${currentWeek}` : ""}
          </h2>
        </div>
        <table className="table card table-card">
          <thead>
            <tr>
              <th>User</th>
              <th>Weekly Wins</th>
              <th>Weekly Losses</th>
            </tr>
          </thead>
          <tbody>
            {weekError ? (
              <tr>
                <td className="table-message" colSpan={3}>{weekError}</td>
              </tr>
            ) : sortedWeek.map(([user, record], idx) => (
              <tr
                key={user}
                className="row-animate"
                style={{ animationDelay: `${idx * 60}ms` }}
              >
                <td>{user}</td>
                <td>{record.wins}</td>
                <td>{record.losses}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}

export default App;
