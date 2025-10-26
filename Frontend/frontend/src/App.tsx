import { useEffect, useState } from "react";

type Users = { [key: string]: number | string }; // allow number or string from backend

function App() {
  const [users, setUsers] = useState<Users>({});

  useEffect(() => {
    fetch("http://localhost:5000/users")
      .then((res) => res.json())
      .then((data: Users) => {
        const numericData: Users = Object.fromEntries(
          Object.entries(data).map(([name, wins]) => [name, Number(wins)])
        );
        setUsers(numericData);
      })
      .catch((err) => console.error(err));
  }, []);

  return (
    <div>
      <h1>Fantasy League Users</h1>
      <ul>
        {Object.entries(users).map(([name, wins]) => (
          <li key={name}>
            {name}: {wins} wins
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;