import axios from "axios";
import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

const API_BASE = "http://127.0.0.1:8000";

function passwordRules(password) {
  const rules = {
    length: password.length >= 8,
    upper: /[A-Z]/.test(password),
    lower: /[a-z]/.test(password),
    digit: /\d/.test(password),
    special: /[^A-Za-z0-9]/.test(password),
  };
  const ok = Object.values(rules).every(Boolean);
  return { ok, rules };
}

export default function ChangePassword() {
  const navigate = useNavigate();
  const username = localStorage.getItem("username") || "";

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const strength = useMemo(() => passwordRules(newPassword), [newPassword]);
  const passwordsMatch = newPassword && confirmPassword && newPassword === confirmPassword;

  const submit = async () => {
    if (!username) {
      alert("You must be logged in.");
      navigate("/login");
      return;
    }
    if (!currentPassword) {
      alert("Enter your current password.");
      return;
    }
    if (!strength.ok) {
      alert("New password is not strong enough.");
      return;
    }
    if (!passwordsMatch) {
      alert("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      await axios.post(`${API_BASE}/change-password`, {
        username,
        current_password: currentPassword,
        new_password: newPassword,
      });
      alert("Password updated.");
      navigate("/dashboard");
    } catch (err) {
      alert(err.response?.data?.detail || "Password change failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="container" style={{ maxWidth: 620 }}>
        <div className="panel">
          <div className="panel__header">
            <div>
              <h1 className="panel__title">Change password</h1>
              <p className="panel__subtitle">Update your account password</p>
            </div>
            <span className="badge">{username || "Not signed in"}</span>
          </div>

          <div className="section">
            <div className="section__title">Current password</div>
            <label htmlFor="cp-current">Current password</label>
            <input
              id="cp-current"
              type="password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              disabled={loading}
              autoComplete="current-password"
            />
          </div>

          <div className="section">
            <div className="section__title">New password</div>
            <label htmlFor="cp-new">New password</label>
            <input
              id="cp-new"
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              disabled={loading}
              autoComplete="new-password"
            />

            <label htmlFor="cp-confirm" style={{ marginTop: 12 }}>
              Confirm new password
            </label>
            <input
              id="cp-confirm"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              disabled={loading}
              autoComplete="new-password"
            />

            <div className="stat" style={{ marginTop: 12 }}>
              <div className="stat__label">Password requirements</div>
              <ul className="help" style={{ margin: "10px 0 0 0", paddingLeft: 18 }}>
                <li>{strength.rules.length ? "✓" : "–"} At least 8 characters</li>
                <li>{strength.rules.upper ? "✓" : "–"} One uppercase letter</li>
                <li>{strength.rules.lower ? "✓" : "–"} One lowercase letter</li>
                <li>{strength.rules.digit ? "✓" : "–"} One number</li>
                <li>{strength.rules.special ? "✓" : "–"} One special character</li>
              </ul>
              <p className="help" style={{ marginTop: 10, marginBottom: 0 }}>
                {passwordsMatch ? (
                  <span className="badge badge--success">Passwords match</span>
                ) : confirmPassword ? (
                  <span className="badge badge--warning">Passwords do not match</span>
                ) : (
                  <span className="badge">Enter the same password twice</span>
                )}
              </p>
            </div>

            <button className="btn btn--block" onClick={submit} disabled={loading}>
              {loading ? "Saving..." : "Update password"}
            </button>

            <p className="help" style={{ marginTop: 12, marginBottom: 0, textAlign: "center" }}>
              Forgot your password? <Link to="/forgot-password">Reset with recovery code</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
