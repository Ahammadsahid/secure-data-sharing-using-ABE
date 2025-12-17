import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",   // ✅ backend URL
});

/* REGISTER */
export const registerUser = (data) =>
  API.post("/register", data);

/* LOGIN */
export const loginUser = (data) =>
  API.post("/auth/login", data);   // ✅ THIS MUST BE EXACT

export default API;
