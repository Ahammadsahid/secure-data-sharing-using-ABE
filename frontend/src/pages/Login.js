// import axios from "axios";
// import { useState } from "react";
// import { useNavigate } from "react-router-dom";

// export default function Login() {
//   const [username, setUsername] = useState("");
//   const [password, setPassword] = useState("");
//   const navigate = useNavigate();

//   const login = async () => {
//     const res = await axios.post("http://127.0.0.1:8000/login", {
//       username,
//       password,
//     });

//     // STORE LOGIN INFO
//     localStorage.setItem("username", username);
//     localStorage.setItem("role", res.data.role);

//     // REDIRECT
//     if (res.data.role === "admin") {
//       navigate("/admin");
//     } else {
//       navigate("/dashboard");
//     }
//   };


//   return (
//     <div className="card">
//       <h2>Login</h2>
//       <input placeholder="Username" onChange={e => setUsername(e.target.value)} />
//       <input type="password" placeholder="Password" onChange={e => setPassword(e.target.value)} />
//       <button onClick={login}>Login</button>
//     </div>
//   );
// }


import axios from "axios";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const login = async () => {
    if (!username || !password) {
      alert("Please enter both username and password.");
      return;
    }

    setLoading(true);
    try {
      const res = await axios.post("http://127.0.0.1:8000/login", {
        username,
        password,
      });

      // Store backend-verified values
      localStorage.setItem("username", res.data.username);
      localStorage.setItem("role", res.data.role);
      localStorage.setItem("department", res.data.department || "IT");
      localStorage.setItem("clearance", res.data.clearance || "high");

      navigate("/dashboard");
    } catch (err) {
      alert((err.response?.data?.detail || "Invalid username or password."));
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") login();
  };

  return (
    <div className="page">
      <div className="container" style={{ maxWidth: 520 }}>
        <div className="panel">
          <div className="panel__header">
            <div>
              <h1 className="panel__title">Sign in</h1>
              <p className="panel__subtitle">Use your account to access encrypted files</p>
            </div>
          </div>

          <div className="section">
            <div className="section__title">Credentials</div>
            <label htmlFor="login-username">Username</label>
            <input
              id="login-username"
              type="text"
              placeholder="Enter your username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
              autoComplete="username"
            />

            <label htmlFor="login-password" style={{ marginTop: 12 }}>
              Password
            </label>
            <input
              id="login-password"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
              autoComplete="current-password"
            />

            <button className="btn btn--block" onClick={login} disabled={loading}>
              {loading ? "Signing in..." : "Sign in"}
            </button>

            <p className="help" style={{ marginTop: 12, marginBottom: 0, textAlign: "center" }}>
              Don’t have an account? Contact an admin to create one.
            </p>
            <p className="help" style={{ marginTop: 8, marginBottom: 0, textAlign: "center" }}>
              Forgot password? <Link to="/forgot-password">Reset with recovery code</Link>
            </p>
          </div>

          <div className="section">
            <div className="section__title">Test users</div>
            <div className="stat">
              <p className="help" style={{ marginTop: 0 }}>
                Use these for demo:
              </p>
              <ul className="help" style={{ margin: 0, paddingLeft: 18 }}>
                <li><strong>admin</strong> / admin123 (admin)</li>
                <li><strong>manager</strong> / manager123 (manager)</li>
                <li><strong>alice</strong> / alice123 (employee)</li>
                <li><strong>bob</strong> / bob123 (accountant)</li>
                <li><strong>charlie</strong> / charlie123 (worker)</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
