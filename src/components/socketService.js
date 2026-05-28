import io from 'socket.io-client';

class SocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.listeners = new Map();
  }

  // Get the correct socket URL - ALWAYS use Render backend in production
  getSocketUrl() {
    // Production mode - always use Render backend
    if (import.meta.env.PROD) {
      const productionUrl = 'https://health-chatbot-backend-w4dl.onrender.com';
      console.log('🔌 Production mode - using:', productionUrl);
      return productionUrl;
    }
    
    // Development mode (localhost)
    console.log('🔌 Development mode - using: http://localhost:5000');
    return 'http://localhost:5000';
  }

  connect(userId, userName, userRole = 'user') {
    const SOCKET_URL = this.getSocketUrl();
    
    if (this.socket && this.socket.connected) {
      console.log('Socket already connected');
      return this.socket;
    }
    
    console.log('🔌 Connecting to socket server...', SOCKET_URL);
    
    this.socket = io(SOCKET_URL, {
      transports: ['websocket', 'polling'],
      auth: {
        userId: userId,
        userName: userName,
        role: userRole
      },
      reconnection: true,
      reconnectionAttempts: 10,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      timeout: 20000,
      withCredentials: true
    });

    this.socket.on('connect', () => {
      console.log('✅ Socket connected:', this.socket.id);
      console.log('✅ Connected to:', SOCKET_URL);
      this.isConnected = true;
      this.emit('user_connected', { userId, userName, role: userRole });
    });

    this.socket.on('disconnect', (reason) => {
      console.log('❌ Socket disconnected:', reason);
      this.isConnected = false;
      
      if (reason === 'io server disconnect') {
        setTimeout(() => {
          console.log('🔄 Attempting to reconnect...');
          this.socket.connect();
        }, 2000);
      }
    });

    this.socket.on('connect_error', (error) => {
      console.error('❌ Connection error:', error.message);
      this.isConnected = false;
    });

    this.socket.on('reconnect', (attemptNumber) => {
      console.log(`✅ Reconnected after ${attemptNumber} attempts`);
      this.isConnected = true;
      this.emit('user_connected', { userId, userName, role: userRole });
    });

    this.socket.on('reconnect_failed', () => {
      console.error('❌ Reconnection failed');
    });

    this.socket.on('connected', (data) => {
      console.log('✅ Server confirmed:', data);
    });

    return this.socket;
  }

  disconnect() {
    if (this.socket) {
      console.log('🔌 Disconnecting socket...');
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
      this.listeners.clear();
    }
  }

  emit(event, data) {
    if (this.socket && this.isConnected) {
      this.socket.emit(event, data);
      return true;
    } else {
      console.warn(`⚠️ Cannot emit '${event}': Socket not connected`);
      return false;
    }
  }

  on(event, callback) {
    if (this.socket) {
      if (this.listeners.has(event)) {
        this.socket.off(event, this.listeners.get(event));
      }
      this.socket.on(event, callback);
      this.listeners.set(event, callback);
    } else {
      console.warn(`⚠️ Cannot listen to '${event}': Socket not initialized`);
    }
  }

  off(event) {
    if (this.socket && this.listeners.has(event)) {
      this.socket.off(event, this.listeners.get(event));
      this.listeners.delete(event);
    }
  }

  getConnectionStatus() {
    return this.isConnected;
  }

  getSocketId() {
    return this.socket?.id || null;
  }

  reconnect(userId, userName, userRole = 'user') {
    this.disconnect();
    setTimeout(() => {
      this.connect(userId, userName, userRole);
    }, 500);
  }
}

const socketService = new SocketService();
export default socketService;