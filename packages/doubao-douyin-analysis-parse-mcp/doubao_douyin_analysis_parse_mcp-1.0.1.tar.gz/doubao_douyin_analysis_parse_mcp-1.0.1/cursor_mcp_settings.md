# Cursor MCP 配置说明

## 配置步骤

1. 打开 Cursor 设置
2. 找到 MCP 配置区域
3. 添加以下配置：

```json
{
  "mcpServers": {
    "douyin-analyzer": {
      "command": "python",
      "args": ["-m", "src"],
      "env": {
        "DOUBAO_API_KEY": "your_actual_api_key"
      },
      "cwd": "D:\\work\\my-project\\douyin_to_notion"
    }
  }
}
```

## 配置项说明

- `command`: 运行命令，使用 `python`
- `args`: 参数，`["-m", "src"]` 表示运行 src 模块
- `env.DOUBAO_API_KEY`: **必须替换为你的实际豆包 API Key**
- `cwd`: **必须替换为你的项目实际路径**

## 获取豆包 API Key

1. 访问 [火山引擎控制台](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey)
2. 登录并创建 API Key
3. 将 API Key 复制并替换上面配置中的 `your_actual_api_key`

## VSCode 配置

如果使用 VSCode with MCP，配置文件位置通常在：
- Windows: `%APPDATA%\Code\User\settings.json`
- macOS: `~/Library/Application Support/Code/User/settings.json`
- Linux: `~/.config/Code/User/settings.json`

在 settings.json 中添加：

```json
{
  "mcp.servers": {
    "douyin-analyzer": {
      "command": "python",
      "args": ["-m", "src"],
      "env": {
        "DOUBAO_API_KEY": "your_actual_api_key"
      },
      "cwd": "D:\\work\\my-project\\douyin_to_notion"
    }
  }
}
```


