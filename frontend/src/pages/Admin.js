import axios from "axios";
import { useState } from "react";

export default function Admin() {
  const [username, setUsername] = useState("");
  const [role, setRole] = useState("");

  const assign = async () => {
    await axios.put(
      `http://127.0.0.1:8000/auth/assign/${username}`,
      { role }
    );
    alert("Attributes assigned");
  };

  return (
    <div className="container">
      <h2>Admin Panel</h2>
      <input placeholder="Username" onChange={(e) => setUsername(e.target.value)} />
      <input placeholder="Role (admin/user)" onChange={(e) => setRole(e.target.value)} />
      <button onClick={assign}>Assign</button>
    </div>
  );
}
