import { io } from 'socket.io-client'

// Connect to backend — in dev, Vite proxies /socket.io to :8000
const socket = io('/', {
  path: '/socket.io',
  transports: ['websocket', 'polling'],
  autoConnect: true,
})

export default socket
