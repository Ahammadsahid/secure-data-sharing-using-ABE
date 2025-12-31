import axios from "axios";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function AdminUsers() {
  const navigate = useNavigate();
  const backendUrl = "http://127.0.0.1:8000";

  const [adminPassword, setAdminPassword] = useState("");
  const [users, setUsers] = useState([]);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [creatingUser, setCreatingUser] = useState(false);
  const [resettingUser, setResettingUser] = useState(false);
  const [createdResult, setCreatedResult] = useState(null);
  const [resetResult, setResetResult] = useState(null);
  const [resettingRecovery, setResettingRecovery] = useState(false);
  const [recoveryPayload, setRecoveryPayload] = useState({ username: "" });
  const [recoveryResult, setRecoveryResult] = useState(null);

  const [newUser, setNewUser] = useState({
    username: "",
    role: "employee",
    department: "IT",
    clearance: "medium",
    password: "",
  });

  const [resetPayload, setResetPayload] = useState({
    username: "",
    new_password: "",
  });

  const isAdmin = (localStorage.getItem("role") || "").toLowerCase() === "admin";

  const getBasicAuthHeader = () => {
    const adminUsername = localStorage.getItem("username") || "";
    const token = btoa(`${adminUsername}:${adminPassword}`);
    return { Authorization: `Basic ${token}` };
  };

  const loadUsers = async () => {
    if (!isAdmin) {
      alert("Only admins can manage users.");
      return;
    }
    if (!adminPassword) {
      alert("Enter your admin password to continue.");
      return;
    }

    setLoadingUsers(true);
    setCreatedResult(null);
    setResetResult(null);
    try {
      const res = await axios.get(`${backendUrl}/admin/users`, {
        headers: {
          ...getBasicAuthHeader(),
        },
      });
      setUsers(res.data?.items || []);
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to load users");
    } finally {
      setLoadingUsers(false);
    }
  };

  const createUser = async () => {
    if (!isAdmin) {
      alert("Only admins can create users.");
      return;
    }
    if (!adminPassword) {
      alert("Enter your admin password to continue.");
      return;
    }
    if (!newUser.username || newUser.username.trim().length < 3) {
      alert("Username must be at least 3 characters.");
      return;
    }

    setCreatingUser(true);
    setCreatedResult(null);
    try {
      const payload = {
        username: newUser.username.trim(),
        role: newUser.role,
      };
      if (newUser.role !== "admin") {
        payload.department = newUser.department;
        payload.clearance = newUser.clearance;
      }
      if (newUser.password && newUser.password.trim()) {
        payload.password = newUser.password;
      }

      const res = await axios.post(`${backendUrl}/admin/users`, payload, {
        headers: {
          ...getBasicAuthHeader(),
        },
      });

      setCreatedResult(res.data);
      setNewUser({ username: "", role: "employee", department: "IT", clearance: "medium", password: "" });
      await loadUsers();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to create user");
    } finally {
      setCreatingUser(false);
    }
  };

  const resetUserPassword = async () => {
    if (!isAdmin) {
      alert("Only admins can reset passwords.");
      return;
    }
    if (!adminPassword) {
      alert("Enter your admin password to continue.");
      return;
    }
    if (!resetPayload.username || resetPayload.username.trim().length < 3) {
      alert("Enter a valid username to reset.");
      return;
    }

    setResettingUser(true);
    setResetResult(null);
    try {
      const payload = {};
      if (resetPayload.new_password && resetPayload.new_password.trim()) {
        payload.new_password = resetPayload.new_password;
      }

      const res = await axios.post(
        `${backendUrl}/admin/users/${encodeURIComponent(resetPayload.username.trim())}/reset-password`,
        payload,
        {
          headers: {
            ...getBasicAuthHeader(),
          },
        }
      );
      setResetResult(res.data);
      setResetPayload({ username: "", new_password: "" });
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to reset password");
    } finally {
      setResettingUser(false);
    }
  };

  const resetUserRecoveryCode = async () => {
    if (!isAdmin) {
      alert("Only admins can reset recovery codes.");
      return;
    }
    if (!adminPassword) {
      alert("Enter your admin password to continue.");
      return;
    }
    if (!recoveryPayload.username || recoveryPayload.username.trim().length < 3) {
      alert("Enter a valid username.");
      return;
    }

    setResettingRecovery(true);
    setRecoveryResult(null);
    try {
      const res = await axios.post(
        `${backendUrl}/admin/users/${encodeURIComponent(recoveryPayload.username.trim())}/reset-recovery-code`,
        {},
        {
          headers: {
            ...getBasicAuthHeader(),
          },
        }
      );
      setRecoveryResult(res.data);
      setRecoveryPayload({ username: "" });
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to reset recovery code");
    } finally {
      setResettingRecovery(false);
    }
  };

  if (!isAdmin) {
    return (
      <div className="page">
        <div className="container">
          <div className="panel">
            <div className="panel__header">
              <div>
                <h1 className="panel__title">User management</h1>
                <p className="panel__subtitle">Administrators only</p>
              </div>
              <span className="badge badge--warning">Access denied</span>
            </div>
            <p className="muted" style={{ margin: 0 }}>
              Your current role: <strong>{localStorage.getItem("role") || "Unknown"}</strong>
            </p>
            <div className="section">
              <button className="btn btn--secondary" onClick={() => navigate("/dashboard")}>Back to dashboard</button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="container">
        <div className="panel">
          <div className="panel__header">
            <div>
              <h1 className="panel__title">User management</h1>
              <p className="panel__subtitle">Create users, add admins, reset passwords</p>
            </div>
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap", justifyContent: "flex-end" }}>
              <button className="btn btn--secondary" onClick={() => navigate("/dashboard")}>Dashboard</button>
            </div>
          </div>

          <div className="section">
            <div className="section__title">Admin authentication</div>
            <p className="help">
              Enter your admin password to perform user-management operations.
              Passwords are stored securely (hashed), so existing passwords cannot be viewed.
            </p>

            <label htmlFor="admin-password">Admin password</label>
            <input
              id="admin-password"
              type="password"
              placeholder="Enter your admin password"
              value={adminPassword}
              onChange={(e) => setAdminPassword(e.target.value)}
              autoComplete="current-password"
            />

            <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginTop: 12 }}>
              <button className="btn btn--secondary" onClick={loadUsers} disabled={loadingUsers}>
                {loadingUsers ? "Loading..." : "Load users"}
              </button>
            </div>
          </div>

          <div className="section">
            <div className="section__title">Create user</div>
            <div className="grid grid--2">
              <div className="stat">
                <div className="stat__label">Username</div>
                <input
                  type="text"
                  placeholder="e.g. user1"
                  value={newUser.username}
                  onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                />
              </div>

              <div className="stat">
                <div className="stat__label">Role</div>
                <select value={newUser.role} onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}>
                  <option value="employee">employee</option>
                  <option value="worker">worker</option>
                  <option value="accountant">accountant</option>
                  <option value="manager">manager</option>
                  <option value="admin">admin</option>
                </select>
              </div>

              {newUser.role !== "admin" ? (
                <>
                  <div className="stat">
                    <div className="stat__label">Department</div>
                    <select value={newUser.department} onChange={(e) => setNewUser({ ...newUser, department: e.target.value })}>
                      <option value="IT">IT</option>
                      <option value="Finance">Finance</option>
                      <option value="HR">HR</option>
                      <option value="Operations">Operations</option>
                    </select>
                  </div>

                  <div className="stat">
                    <div className="stat__label">Clearance</div>
                    <select value={newUser.clearance} onChange={(e) => setNewUser({ ...newUser, clearance: e.target.value })}>
                      <option value="high">high</option>
                      <option value="medium">medium</option>
                      <option value="low">low</option>
                    </select>
                  </div>
                </>
              ) : (
                <div className="stat" style={{ gridColumn: "1 / -1" }}>
                  <div className="stat__label">Admin account</div>
                  <p className="help" style={{ marginTop: 10, marginBottom: 0 }}>
                    Department and clearance are not required for admins.
                  </p>
                </div>
              )}

              <div className="stat" style={{ gridColumn: "1 / -1" }}>
                <div className="stat__label">Optional: set initial password</div>
                <input
                  type="password"
                  placeholder="Set a basic initial password (user can change later)"
                  value={newUser.password}
                  onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                  autoComplete="new-password"
                />
                <p className="help" style={{ marginBottom: 0 }}>
                  If empty, the backend returns a basic temporary password.
                </p>
              </div>
            </div>

            <button className="btn btn--block" onClick={createUser} disabled={creatingUser}>
              {creatingUser ? "Creating..." : "Create user"}
            </button>

            {createdResult ? (
              <div className="stat" style={{ marginTop: 12 }}>
                <div className="stat__label">Share these with the user</div>
                <p className="help" style={{ marginTop: 10, marginBottom: 0 }}>
                  Username: <strong>{createdResult.username}</strong>
                </p>
                <p className="help" style={{ marginTop: 6, marginBottom: 0 }}>
                  Temporary password: <strong>{createdResult.temporary_password}</strong>
                </p>
                <p className="help" style={{ marginTop: 6, marginBottom: 0 }}>
                  Recovery code: <strong>{createdResult.recovery_code}</strong>
                </p>
              </div>
            ) : null}
          </div>

          <div className="section">
            <div className="section__title">Reset user password</div>
            <div className="grid grid--2">
              <div className="stat">
                <div className="stat__label">Username</div>
                <input
                  type="text"
                  placeholder="e.g. alice"
                  value={resetPayload.username}
                  onChange={(e) => setResetPayload({ ...resetPayload, username: e.target.value })}
                />
              </div>
              <div className="stat">
                <div className="stat__label">Optional new password</div>
                <input
                  type="password"
                  placeholder="Leave empty to auto-generate"
                  value={resetPayload.new_password}
                  onChange={(e) => setResetPayload({ ...resetPayload, new_password: e.target.value })}
                />
              </div>
            </div>

            <button className="btn btn--block btn--danger" onClick={resetUserPassword} disabled={resettingUser}>
              {resettingUser ? "Resetting..." : "Reset password"}
            </button>

            {resetResult ? (
              <div className="stat" style={{ marginTop: 12 }}>
                <div className="stat__label">Share these with the user</div>
                <p className="help" style={{ marginTop: 10, marginBottom: 0 }}>
                  Username: <strong>{resetResult.username}</strong>
                </p>
                <p className="help" style={{ marginTop: 6, marginBottom: 0 }}>
                  Temporary password: <strong>{resetResult.temporary_password}</strong>
                </p>
                <p className="help" style={{ marginTop: 6, marginBottom: 0 }}>
                  New recovery code: <strong>{resetResult.recovery_code}</strong>
                </p>
              </div>
            ) : null}
          </div>

          <div className="section">
            <div className="section__title">Reset recovery code</div>
            <p className="help">
              Recovery codes are stored securely (hashed), so the old code cannot be shown again.
              This will generate a NEW recovery code for the user.
            </p>

            <div className="grid grid--2">
              <div className="stat">
                <div className="stat__label">Username</div>
                <input
                  type="text"
                  placeholder="e.g. alice"
                  value={recoveryPayload.username}
                  onChange={(e) => setRecoveryPayload({ username: e.target.value })}
                />
              </div>
              <div className="stat" style={{ display: "flex", alignItems: "flex-end" }}>
                <button className="btn btn--block btn--secondary" onClick={resetUserRecoveryCode} disabled={resettingRecovery}>
                  {resettingRecovery ? "Generating..." : "Generate new recovery code"}
                </button>
              </div>
            </div>

            {recoveryResult ? (
              <div className="stat" style={{ marginTop: 12 }}>
                <div className="stat__label">Share this with the user</div>
                <p className="help" style={{ marginTop: 10, marginBottom: 0 }}>
                  Username: <strong>{recoveryResult.username}</strong>
                </p>
                <p className="help" style={{ marginTop: 6, marginBottom: 0 }}>
                  New recovery code: <strong>{recoveryResult.recovery_code}</strong>
                </p>
              </div>
            ) : null}
          </div>

          <div className="section">
            <div className="section__title">Users</div>
            {users.length === 0 ? (
              <p className="help" style={{ marginTop: 0 }}>
                Click <strong>Load users</strong> to fetch the list.
              </p>
            ) : (
              <div className="stat">
                <div style={{ overflowX: "auto" }}>
                  <table style={{ width: "100%", borderCollapse: "collapse" }}>
                    <thead>
                      <tr>
                        <th style={{ textAlign: "left", padding: "10px 8px", borderBottom: "1px solid var(--border)" }}>Username</th>
                        <th style={{ textAlign: "left", padding: "10px 8px", borderBottom: "1px solid var(--border)" }}>Role</th>
                        <th style={{ textAlign: "left", padding: "10px 8px", borderBottom: "1px solid var(--border)" }}>Department</th>
                        <th style={{ textAlign: "left", padding: "10px 8px", borderBottom: "1px solid var(--border)" }}>Clearance</th>
                      </tr>
                    </thead>
                    <tbody>
                      {users.map((u) => (
                        <tr key={u.username}>
                          <td style={{ padding: "10px 8px", borderBottom: "1px solid var(--border)" }}>{u.username}</td>
                          <td style={{ padding: "10px 8px", borderBottom: "1px solid var(--border)", textTransform: "capitalize" }}>{u.role}</td>
                          <td style={{ padding: "10px 8px", borderBottom: "1px solid var(--border)" }}>{u.department}</td>
                          <td style={{ padding: "10px 8px", borderBottom: "1px solid var(--border)", textTransform: "capitalize" }}>{u.clearance}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
