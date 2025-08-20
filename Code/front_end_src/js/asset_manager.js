path = "F:\\project\\Lilith\\Config\\static_src.json"

class AssetsManager {
  constructor(path) {
    this.assets = null;
    // config_path存储了配置文件的地址，这里需要重新填写一下
    this.config_path = path;
    // root_dir存储了整个项目根目录的在系统中的地址，从配置文件中读取
    this.root_dir = null;
  }

  // 加载资源配置
  async loadConfig() {
    try {
      const response = await fetch(this.config_path);
      if (!response.ok) throw new Error('加载资源配置失败');
      this.assets = await response.json();

      this.root_dir = this.assets["root directory"] || "";

      return this.assets;
    } catch (err) {
      console.error('资源配置加载错误:', err);
      throw err;
    }
  }

  // 获取资源路径
  getAsset(path) {
    if (!this.assets) {
      console.warn('资源配置未加载，请先调用loadConfig()');
      return '';
    }

    // 支持类似"images.logo"的路径访问
    // 这里的意思是对于你输入的"images.logo"你可以直接通过"."的方式来访问下一层级的内容
    const relativePath = path.split('.').reduce((obj, key) => {
      return obj && obj[key] ? obj[key] : '';
    }, this.assets);

    if (!relativePath) {
      console.warn(`找不到路径为${path}的资源配置`);
      return '';
    }

    // 拼接根目录和相对路径
    return this.root_dir + relativePath;
  }
}

// 实例化并导出
const assetsManager = new AssetsManager();
