import { useEffect, useState, useRef } from "react";

type Users = { [key: string]: number };

function App() {
  const [users, setUsers] = useState<Users>({});
  const fetchedRef = useRef(false);

  useEffect(() => {
    if (fetchedRef.current) return;
    fetchedRef.current = true;

    fetch("http://localhost:5000/users")
      .then((res) => res.json())
      .then((data: Users) => setUsers(data))
      .catch((err) => console.error("Error fetching users:", err));
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