import axios from "axios";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

export default function Register() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [role, setRole] = useState("employee");
  const [department, setDepartment] = useState("IT");
  const [clearance, setClearance] = useState("medium");
  const [loading, setLoading] = useState(false);
  const [recoveryCode, setRecoveryCode] = useState("");
  const [registered, setRegistered] = useState(false);
  const navigate = useNavigate();

  const roles = ["manager", "accountant", "employee", "worker"];
  const departments = ["IT", "Finance", "HR", "Operations"];
  const clearances = ["high", "medium", "low"];

  const isStrongPassword = (pw) => {
    if (!pw || pw.length < 8) return false;
    if (!/[A-Z]/.test(pw)) return false;
    if (!/[a-z]/.test(pw)) return false;
    if (!/\d/.test(pw)) return false;
    if (!/[^A-Za-z0-9]/.test(pw)) return false;
    return true;
  };

  const register = async () => {
    if (!username || !password) {
      alert("Please enter username and password.");
      return;
    }

    if (password !== confirmPassword) {
      alert("Passwords do not match.");
      return;
    }

    if (username.length < 3) {
      alert("Username must be at least 3 characters.");
      return;
    }

    if (!isStrongPassword(password)) {
      alert("Use a stronger password: 8+ chars with uppercase, lowercase, a number, and a special character.");
      return;
    }

    setLoading(true);
    try {
      const res = await axios.post("http://127.0.0.1:8000/register", {
        username,
        password,
        role,
        department,
        clearance
      });
      setRecoveryCode(res.data?.recovery_code || "");
      setRegistered(true);
    } catch (err) {
      alert((err.response?.data?.detail || "Registration failed."));
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") register();
  };

  return (
    <div className="page">
      <div className="container" style={{ maxWidth: 620 }}>
        <div className="panel">
          <div className="panel__header">
            <div>
              <h1 className="panel__title">Create account</h1>
              <p className="panel__subtitle">Your attributes control which files you can decrypt</p>
            </div>
          </div>

          <div className="section">
            <div className="section__title">Credentials</div>
            <label htmlFor="register-username">Username</label>
            <input
              id="register-username"
              type="text"
              placeholder="Choose a username (min 3 chars)"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={loading || registered}
              autoComplete="username"
            />

            <label htmlFor="register-password" style={{ marginTop: 12 }}>
              Password
            </label>
            <input
              id="register-password"
              type="password"
              placeholder="Password (8+ chars, strong)"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading || registered}
              onKeyDown={handleKeyDown}
              autoComplete="new-password"
            />

            <label htmlFor="register-password-confirm" style={{ marginTop: 12 }}>
              Confirm password
            </label>
            <input
              id="register-password-confirm"
              type="password"
              placeholder="Re-enter password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              disabled={loading || registered}
              onKeyDown={handleKeyDown}
              autoComplete="new-password"
            />

            <p className="help" style={{ marginTop: 10 }}>
              Use at least 8 characters including uppercase, lowercase, a number, and a special character.
            </p>
          </div>

          <div className="section">
            <div className="section__title">Attributes</div>
            <div className="grid grid--2">
              <div className="stat">
                <div className="stat__label">Role</div>
                <select value={role} onChange={(e) => setRole(e.target.value)} disabled={loading || registered}>
                  {roles.map((r) => (
                    <option key={r} value={r}>
                      {r.charAt(0).toUpperCase() + r.slice(1)}
                    </option>
                  ))}
                </select>
              </div>

              <div className="stat">
                <div className="stat__label">Department</div>
                <select value={department} onChange={(e) => setDepartment(e.target.value)} disabled={loading || registered}>
                  {departments.map((d) => (
                    <option key={d} value={d}>
                      {d}
                    </option>
                  ))}
                </select>
              </div>

              <div className="stat">
                <div className="stat__label">Clearance</div>
                <select value={clearance} onChange={(e) => setClearance(e.target.value)} disabled={loading || registered}>
                  {clearances.map((c) => (
                    <option key={c} value={c}>
                      {c.charAt(0).toUpperCase() + c.slice(1)}
                    </option>
                  ))}
                </select>
              </div>

              <div className="stat">
                <div className="stat__label">Note</div>
                <p className="help" style={{ marginTop: 10, marginBottom: 0 }}>
                  These attributes are used by the policy engine and must match the policy embedded in encrypted files.
                </p>
              </div>
            </div>
          </div>

          <div className="section">
            {!registered ? (
              <>
                <button className="btn btn--block" onClick={register} disabled={loading}>
                  {loading ? "Creating..." : "Create account"}
                </button>
                <p className="help" style={{ marginTop: 12, marginBottom: 0, textAlign: "center" }}>
                  Already have an account? <Link to="/login">Sign in</Link>
                </p>
              </>
            ) : (
              <>
                <div className="stat">
                  <div className="stat__label">Recovery code</div>
                  <p className="help" style={{ marginTop: 10 }}>
                    Save this code now. It is shown only once and is required to reset your password.
                  </p>
                  <p
                    style={{
                      margin: 0,
                      padding: "10px 12px",
                      border: "1px dashed var(--border)",
                      borderRadius: 10,
                      fontFamily:
                        "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace",
                      letterSpacing: "0.08em",
                      fontWeight: 800,
                      textAlign: "center",
                    }}
                  >
                    {recoveryCode || "(not returned)"}
                  </p>
                </div>
                <button
                  className="btn btn--block"
                  onClick={() => {
                    alert("Registration complete. Keep your recovery code safe.");
                    navigate("/login");
                  }}
                  disabled={loading}
                >
                  Go to sign in
                </button>
                <p className="help" style={{ marginTop: 12, marginBottom: 0, textAlign: "center" }}>
                  Forgot password later? <Link to="/forgot-password">Reset with recovery code</Link>
                </p>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
