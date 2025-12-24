import axios from "axios";
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

export default function Register() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("employee");
  const [department, setDepartment] = useState("IT");
  const [clearance, setClearance] = useState("medium");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const roles = ["admin", "manager", "accountant", "employee", "worker"];
  const departments = ["IT", "Finance", "HR", "Operations"];
  const clearances = ["high", "medium", "low"];

  const register = async () => {
    if (!username || !password) {
      alert("❌ Please enter username and password");
      return;
    }

    if (username.length < 3) {
      alert("❌ Username must be at least 3 characters");
      return;
    }

    if (password.length < 6) {
      alert("❌ Password must be at least 6 characters");
      return;
    }

    setLoading(true);
    try {
      await axios.post("http://127.0.0.1:8000/register", {
        username,
        password,
        role,
        department,
        clearance
      });
      alert("✅ Registration successful! Please login.");
      navigate("/login");
    } catch (err) {
      alert("❌ " + (err.response?.data?.detail || "Registration failed"));
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      register();
    }
  };

  return (
    <div style={{
      maxWidth: "500px",
      margin: "0 auto",
      marginTop: "40px"
    }}>
      <div className="card">
        <h2 style={{
          textAlign: "center",
          color: "#2c3e50",
          marginBottom: "30px",
          fontSize: "28px"
        }}>
          📝 Create Account
        </h2>

        {/* Username */}
        <div style={{ marginBottom: "20px" }}>
          <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold", color: "#34495e" }}>
            👤 Username
          </label>
          <input
            type="text"
            placeholder="Choose a username (min 3 chars)"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={loading}
            style={{
              width: "100%",
              padding: "12px",
              border: "2px solid #bdc3c7",
              borderRadius: "6px",
              fontSize: "14px"
            }}
          />
        </div>

        {/* Password */}
        <div style={{ marginBottom: "20px" }}>
          <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold", color: "#34495e" }}>
            🔑 Password
          </label>
          <input
            type="password"
            placeholder="Password (min 6 chars)"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={loading}
            onKeyPress={handleKeyPress}
            style={{
              width: "100%",
              padding: "12px",
              border: "2px solid #bdc3c7",
              borderRadius: "6px",
              fontSize: "14px"
            }}
          />
        </div>

        {/* Role */}
        <div style={{ marginBottom: "20px" }}>
          <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold", color: "#34495e" }}>
            👔 Role
          </label>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            disabled={loading}
            style={{
              width: "100%",
              padding: "12px",
              border: "2px solid #bdc3c7",
              borderRadius: "6px",
              fontSize: "14px",
              backgroundColor: "white",
              cursor: "pointer"
            }}
          >
            {roles.map((r) => (
              <option key={r} value={r}>
                {r.charAt(0).toUpperCase() + r.slice(1)}
              </option>
            ))}
          </select>
        </div>

        {/* Department */}
        <div style={{ marginBottom: "20px" }}>
          <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold", color: "#34495e" }}>
            🏢 Department
          </label>
          <select
            value={department}
            onChange={(e) => setDepartment(e.target.value)}
            disabled={loading}
            style={{
              width: "100%",
              padding: "12px",
              border: "2px solid #bdc3c7",
              borderRadius: "6px",
              fontSize: "14px",
              backgroundColor: "white",
              cursor: "pointer"
            }}
          >
            {departments.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </div>

        {/* Clearance */}
        <div style={{ marginBottom: "25px" }}>
          <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold", color: "#34495e" }}>
            🔐 Clearance Level
          </label>
          <select
            value={clearance}
            onChange={(e) => setClearance(e.target.value)}
            disabled={loading}
            style={{
              width: "100%",
              padding: "12px",
              border: "2px solid #bdc3c7",
              borderRadius: "6px",
              fontSize: "14px",
              backgroundColor: "white",
              cursor: "pointer"
            }}
          >
            {clearances.map((c) => (
              <option key={c} value={c}>
                {c.charAt(0).toUpperCase() + c.slice(1)}
              </option>
            ))}
          </select>
        </div>

        {/* Register Button */}
        <button
          onClick={register}
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
            marginTop: 0
          }}
        >
          {loading ? "⏳ Registering..." : "✅ Create Account"}
        </button>

        {/* Login Link */}
        <div style={{ marginTop: "20px", textAlign: "center", paddingTop: "20px", borderTop: "1px solid #ecf0f1" }}>
          <p style={{ color: "#666", fontSize: "14px", margin: "0 0 10px 0" }}>
            Already have an account?
          </p>
          <Link
            to="/login"
            style={{
              color: "#667eea",
              fontWeight: "bold",
              textDecoration: "none",
              transition: "color 0.3s ease"
            }}
            onMouseOver={(e) => e.target.style.color = "#764ba2"}
            onMouseOut={(e) => e.target.style.color = "#667eea"}
          >
            🔐 Login here
          </Link>
        </div>

        {/* Info */}
        <div style={{
          marginTop: "25px",
          padding: "15px",
          backgroundColor: "#e8f4f8",
          borderRadius: "6px",
          border: "1px solid #d0e8f2",
          fontSize: "13px"
        }}>
          <strong style={{ color: "#2980b9" }}>ℹ️ Important:</strong>
          <p style={{ margin: "8px 0 0 0", color: "#555" }}>
            Your attributes (role, department, clearance) determine which files you can access. Choose carefully!
          </p>
        </div>
      </div>
    </div>
  );
}
