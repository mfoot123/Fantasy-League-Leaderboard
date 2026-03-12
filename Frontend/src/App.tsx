import { useEffect, useRef, useState } from "react";
import "./App.css";

type WeekWins = Record<
  string,
  {
    wins: number;
    losses: number;
  }
>;

type SeasonUser = {
  wins: number;
  losses: number;
  bracket: "winners" | "losers" | null;
  is_eliminated: boolean;
  eliminated_week: number | null;
};

type SeasonWins = Record<string, SeasonUser>;

function App() {
  const [seasonWins, setSeasonWins] = useState<SeasonWins>({});
  const [weekWins, setWeekWins] = useState<WeekWins>({});
  const fetchedRef = useRef(false);

  useEffect(() => {
    if (fetchedRef.current) return;
    fetchedRef.current = true;

    fetch("http://localhost:5000/users")
      .then(res => res.json())
      .then((data: SeasonWins) => setSeasonWins(data))
      .catch(err => console.error("Error fetching season data:", err));

    fetch("http://localhost:5000/users?week=current")
      .then(res => res.json())
      .then((data: WeekWins) => setWeekWins(data))
      .catch(err => console.error("Error fetching current week data:", err));
  }, []);

  const sortedSeason = Object.entries(seasonWins).sort(
    (a, b) => b[1].wins - a[1].wins
  );

  // lower rank number = better, so sort ascending
  const sortedWeek = Object.entries(weekWins).sort(
    (a, b) => a[1].wins - b[1].wins
  );

  return (
    <div className="page">
      <header className="hero">
        <div className="hero__pill">Live Synced</div>
        <h1>Fantasy League Leaderboard</h1>
      </header>

      <section className="panel">
        <div className="panel__title">
          <h2>Season Standings</h2>
          <span className="spark">Season overview</span>
        </div>
        <table className="table card table-card">
          <thead>
            <tr>
              <th>User</th>
              <th>Wins</th>
              <th>Losses</th>
              <th>Bracket</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {sortedSeason.map(([user, info], idx) => (
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
                  className={`status ${info.is_eliminated ? "eliminated" : ""
                    }`}
                >
                  {info.is_eliminated
                    ? `Eliminated (week ${info.eliminated_week ?? "?"})`
                    : "Active"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="panel">
        <div className="panel__title">
          <h2>Current Week Ranking</h2>
          <span className="spark">This week</span>
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
            {sortedWeek.map(([user, record], idx) => (
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
