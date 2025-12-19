import axios from "axios";
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

export default function Register() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("employee");
  const navigate = useNavigate();

  const register = async () => {
    await axios.post("http://127.0.0.1:8000/register", {
      username,
      password,
      role,
    });
    alert("Registration successful");
    navigate("/login");
  };

  return (
    <div className="card">
      <h2>Register</h2>

      <input placeholder="Username" onChange={e => setUsername(e.target.value)} />
      <input type="password" placeholder="Password" onChange={e => setPassword(e.target.value)} />

      <select onChange={e => setRole(e.target.value)}>
        <option value="admin">Admin</option>
        <option value="manager">Manager</option>
        <option value="accountant">Accountant</option>
        <option value="employee">Employee</option>
        <option value="worker">Worker</option>
      </select>

      <button onClick={register}>Register</button>

      <p className="link">
        Already have an account? <Link to="/login">Login</Link>
      </p>
    </div>
  );
}
