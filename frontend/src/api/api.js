import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",   // backend URL
});

/* LOGIN */
export const loginUser = (data) =>
  API.post("/login", data);

export default API;
