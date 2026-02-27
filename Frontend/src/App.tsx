import { useEffect, useState, useRef } from "react";

type Users = { [key: string]: number };

function App() {
  const [seasonWins, setSeasonWins] = useState<Users>({});
  const [weekWins, setWeekWins] = useState<Users>({});

  const fetchedRef = useRef(false);

  useEffect(() => {
    if (fetchedRef.current) return;
    fetchedRef.current = true;
    fetch("http://localhost:5000/users")
      .then(res => res.json())
      .then((data: Users) => setSeasonWins(data))
      .catch(err => console.error("Error fetching season wins:", err));

    // fetch current week wins
    fetch("http://localhost:5000/users?week=current")
      .then(res => res.json())
      .then((data: Users) => setWeekWins(data))
      .catch(err => console.error("Error fetching week wins:", err));
  }, []);

  // Sort season wins from highest to lowest
  const sortedSeason = Object.entries(seasonWins).sort((a, b) => b[1] - a[1]);
  // Sort week wins from highest to lowest
  const sortedWeek = Object.entries(weekWins).sort((a, b) => b[1] - a[1]);

  return (
    <div>
      <h1>Fantasy League Leaderboard</h1>

      <h2>Season Wins</h2>
      <table border={1} cellPadding={5} style={{ borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th>User</th>
            <th>Wins</th>
          </tr>
        </thead>
        <tbody>
          {sortedSeason.map(([user, wins], index) => (
            <tr
              key={user}
              style={{
                border: index < 4 ? "2px solid blue" : "1px solid black"
              }}
            >
              <td>{user}</td>
              <td>{wins}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>Current Week Wins</h2>
      <table border={1} cellPadding={5} style={{ borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th>User</th>
            <th>Wins</th>
          </tr>
        </thead>
        <tbody>
          {sortedWeek.map(([user, wins]) => (
            <tr key={user}>
              <td>{user}</td>
              <td>{wins}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;