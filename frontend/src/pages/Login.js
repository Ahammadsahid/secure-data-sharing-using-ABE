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
  const navigate = useNavigate();

  const login = async () => {
    try {
      const res = await axios.post("http://127.0.0.1:8000/login", {
        username,
        password,
      });

      // 🔥 STORE BACKEND-VERIFIED VALUES
      localStorage.setItem("username", res.data.username);
      localStorage.setItem("role", res.data.role);

      if (res.data.role === "admin") {
        navigate("/admin");
      } else {
        navigate("/dashboard");
      }
    } catch (err) {
      alert("Invalid username or password");
    }
  };

  return (
    <div className="card">
      <h2>Login</h2>
      <input placeholder="Username" onChange={e => setUsername(e.target.value)} />
      <input type="password" placeholder="Password" onChange={e => setPassword(e.target.value)} />
      <button onClick={login}>Login</button>
      <p>New user? <Link to="/register">Register</Link></p>
    </div>
  );
}
