import { io } from 'socket.io-client'

// Connect to backend — in dev, Vite proxies /socket.io to :8000
// This forces the socket to use your Render backend variable.
const socket = io(import.meta.env.VITE_BACKEND_URL, {
  path: "/socket.io",
  transports: ["websocket", "polling"],
  withCredentials: true,
});

export default socket
