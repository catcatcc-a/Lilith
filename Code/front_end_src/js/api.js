// 配置 FastAPI 后端地址（根据你的实际地址修改）
const API_BASE_URL = "http://localhost:8000";

// 实例化 Axios（通过 CDN 引入）
const api = {
  // 用户注册
  register: async (username, password) => {
    const response = await axios.post(`${API_BASE_URL}/register`, {
      username,
      password
    });
    return response.data;
  },

  // 用户登录
  login: async (userId, password) => {
    const response = await axios.post(`${API_BASE_URL}/login`, {
      user_id: userId,
      password
    });
    return response.data;
  },

  // 发送聊天消息
  sendMessage: async (userId, inputText) => {
    const response = await axios.post(`${API_BASE_URL}/chat`, {
      user_id: userId,
      input_text: inputText
    });
    return response.data;
  },

  // 获取聊天历史
  getChatHistory: async (userId, hoursAgo = 1) => {
    const response = await axios.get(`${API_BASE_URL}/history/${userId}`, {
      params: { hours_ago: hoursAgo }
    });
    return response.data;
  },

  // 获取用户总结
  getUserSummary: async (userId) => {
    const response = await axios.get(`${API_BASE_URL}/user-summary/${userId}`);
    return response.data;
  }
};

// 存储用户状态（localStorage 持久化）
const userStore = {
  setUser: (userData) => {
    localStorage.setItem("user", JSON.stringify(userData));
  },
  getUser: () => {
    const user = localStorage.getItem("user");
    return user ? JSON.parse(user) : null;
  },
  logout: () => {
    localStorage.removeItem("user");
  }
};