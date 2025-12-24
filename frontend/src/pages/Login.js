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
import { useNavigate, Link } from "react-router-dom";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const login = async () => {
    if (!username || !password) {
      alert("❌ Please enter both username and password");
      return;
    }

    setLoading(true);
    try {
      const res = await axios.post("http://127.0.0.1:8000/login", {
        username,
        password,
      });

      // 🔥 STORE BACKEND-VERIFIED VALUES
      localStorage.setItem("username", res.data.username);
      localStorage.setItem("role", res.data.role);
      localStorage.setItem("department", res.data.department || "IT");
      localStorage.setItem("clearance", res.data.clearance || "high");

      navigate("/dashboard");
    } catch (err) {
      alert("❌ " + (err.response?.data?.detail || "Invalid username or password"));
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      login();
    }
  };

  return (
    <div style={{
      maxWidth: "400px",
      margin: "0 auto",
      marginTop: "60px"
    }}>
      <div className="card">
        <h2 style={{
          textAlign: "center",
          color: "#2c3e50",
          marginBottom: "30px",
          fontSize: "28px"
        }}>
          🔐 Secure Login
        </h2>

        <div style={{ marginBottom: "20px" }}>
          <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold", color: "#34495e" }}>
            👤 Username
          </label>
          <input
            type="text"
            placeholder="Enter your username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={loading}
            style={{
              width: "100%",
              padding: "12px",
              border: "2px solid #bdc3c7",
              borderRadius: "6px",
              fontSize: "14px",
              transition: "all 0.3s ease"
            }}
          />
        </div>

        <div style={{ marginBottom: "20px" }}>
          <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold", color: "#34495e" }}>
            🔑 Password
          </label>
          <input
            type="password"
            placeholder="Enter your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={loading}
            style={{
              width: "100%",
              padding: "12px",
              border: "2px solid #bdc3c7",
              borderRadius: "6px",
              fontSize: "14px",
              transition: "all 0.3s ease"
            }}
          />
        </div>

        <button
          onClick={login}
          disabled={loading}
          style={{
            width: "100%",
            padding: "12px",
            backgroundColor: loading ? "#bdc3c7" : "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            color: "white",
            border: "none",
            borderRadius: "6px",
            fontSize: "16px",
            fontWeight: "bold",
            cursor: loading ? "not-allowed" : "pointer",
            transition: "all 0.3s ease",
            marginTop: "10px"
          }}
        >
          {loading ? "⏳ Logging in..." : "🚀 Login"}
        </button>

        <div style={{ marginTop: "20px", textAlign: "center", paddingTop: "20px", borderTop: "1px solid #ecf0f1" }}>
          <p style={{ color: "#666", fontSize: "14px", margin: "0 0 10px 0" }}>
            Don't have an account?
          </p>
          <Link
            to="/register"
            style={{
              color: "#667eea",
              fontWeight: "bold",
              textDecoration: "none",
              transition: "color 0.3s ease"
            }}
            onMouseOver={(e) => e.target.style.color = "#764ba2"}
            onMouseOut={(e) => e.target.style.color = "#667eea"}
          >
            📝 Register here
          </Link>
        </div>

        {/* Test Users Info */}
        <div style={{
          marginTop: "30px",
          padding: "15px",
          backgroundColor: "#f0f4ff",
          borderRadius: "6px",
          border: "1px solid #d0deff",
          fontSize: "12px"
        }}>
          <strong style={{ color: "#667eea" }}>📌 Test Users Available:</strong>
          <ul style={{ margin: "8px 0 0 0", paddingLeft: "20px", color: "#555" }}>
            <li><strong>admin</strong> / admin123 (admin)</li>
            <li><strong>alice</strong> / alice123 (IT user)</li>
            <li><strong>bob</strong> / bob123 (Finance user)</li>
            <li><strong>charlie</strong> / charlie123 (HR user)</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
