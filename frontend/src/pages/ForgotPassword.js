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

export default function ForgotPassword() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [recoveryCode, setRecoveryCode] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const strength = useMemo(() => passwordRules(newPassword), [newPassword]);
  const passwordsMatch = newPassword && confirmPassword && newPassword === confirmPassword;

  const resetPassword = async () => {
    if (!username || !recoveryCode) {
      alert("Enter username and recovery code.");
      return;
    }
    if (!newPassword || !confirmPassword) {
      alert("Enter the new password twice.");
      return;
    }
    if (!strength.ok) {
      alert("Password is not strong enough.");
      return;
    }
    if (!passwordsMatch) {
      alert("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      await axios.post(`${API_BASE}/forgot-password/reset`, {
        username,
        recovery_code: recoveryCode,
        new_password: newPassword,
      });
      alert("Password reset successful. Please sign in.");
      navigate("/login");
    } catch (err) {
      alert(err.response?.data?.detail || "Password reset failed.");
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
              <h1 className="panel__title">Reset password</h1>
              <p className="panel__subtitle">Use your recovery code to set a new password</p>
            </div>
          </div>

          <div className="section">
            <div className="section__title">Account</div>
            <label htmlFor="fp-username">Username</label>
            <input
              id="fp-username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={loading}
              autoComplete="username"
            />

            <label htmlFor="fp-code" style={{ marginTop: 12 }}>
              Recovery code
            </label>
            <input
              id="fp-code"
              type="text"
              value={recoveryCode}
              onChange={(e) => setRecoveryCode(e.target.value.toUpperCase())}
              disabled={loading}
              placeholder="Example: 7F2K9M8Q1ABC"
            />
            <p className="help">Your recovery code is shown once after registration. Keep it safe.</p>
          </div>

          <div className="section">
            <div className="section__title">New password</div>
            <label htmlFor="fp-new">New password</label>
            <input
              id="fp-new"
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              disabled={loading}
              autoComplete="new-password"
            />

            <label htmlFor="fp-confirm" style={{ marginTop: 12 }}>
              Confirm new password
            </label>
            <input
              id="fp-confirm"
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

            <button className="btn btn--block" onClick={resetPassword} disabled={loading}>
              {loading ? "Resetting..." : "Reset password"}
            </button>

            <p className="help" style={{ marginTop: 12, marginBottom: 0, textAlign: "center" }}>
              Remembered your password? <Link to="/login">Sign in</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
