# 快速开始指南

> 🎓 **Python 新手？** 建议先看 [新手指南.md](新手指南.md) - 有更详细的说明和常见问题解答

## 5 分钟快速上手

### 步骤 1：安装（2 分钟）

#### Windows 用户
双击运行 `install.bat`

#### macOS/Linux 用户
```bash
chmod +x install.sh
./install.sh
```

或手动安装：
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
```

### 步骤 2：配置 API Key（1 分钟）

1. 访问 [火山引擎控制台](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey)
2. 创建 API Key
3. 编辑 `.env` 文件，替换 API Key：

```env
DOUBAO_API_KEY=你的实际API密钥
```

### 步骤 3：配置 Cursor（2 分钟）

1. 打开 Cursor 设置
2. 找到 MCP 配置
3. 添加配置（**记得替换路径和 API Key**）：

```json
{
  "mcpServers": {
    "douyin-analyzer": {
      "command": "python",
      "args": ["-m", "src"],
      "env": {
        "DOUBAO_API_KEY": "你的实际API密钥"
      },
      "cwd": "D:\\work\\my-project\\douyin_to_notion"
    }
  }
}
```

### 步骤 4：开始使用！

在 Cursor 中输入：

```
分析这个抖音视频：https://v.douyin.com/DGHl69ciWp4/
```

或：

```
帮我看看这个抖音视频讲的什么：0.05 09/23 III:/ https://v.douyin.com/DGHl69ciWp4/ 复制此链接...
```

## 测试服务器

在命令行中测试服务器是否正常运行：

```bash
# 激活虚拟环境
source venv/bin/activate  # Windows: venv\Scripts\activate

# 运行服务器
python -m src
```

服务器启动后，可以通过 MCP 客户端调用。

## 常见使用场景

### 场景 1：分析烹饪视频

```
这是一个做菜的抖音视频，帮我整理食材和步骤：https://v.douyin.com/xxx/
```

返回：
- 所需食材清单
- 详细制作步骤
- 关键提示

### 场景 2：分析教程视频

```
分析这个手工教程视频：https://v.douyin.com/xxx/
```

返回：
- 所需材料
- 制作步骤
- 注意事项

### 场景 3：分析普通视频

```
这个抖音视频讲了什么内容：https://v.douyin.com/xxx/
```

返回：
- 视频简介
- 主要内容
- 关键信息点

## 故障排查

### ❌ 问题：无法提取链接

**原因**：链接格式不正确或不完整

**解决**：确保链接包含 `https://v.douyin.com/` 或 `https://www.douyin.com/`

### ❌ 问题：API Key 错误

**原因**：未设置或设置错误

**解决**：
1. 检查 `.env` 文件中的 `DOUBAO_API_KEY`
2. 检查 MCP 配置中的 `env.DOUBAO_API_KEY`

### ❌ 问题：找不到 Python

**原因**：Python 未安装或未添加到 PATH

**解决**：
1. 安装 Python 3.10+
2. 确保添加到系统 PATH

## 下一步

- 查看 [README.md](README.md) 了解详细文档
- 查看 [cursor_mcp_settings.md](cursor_mcp_settings.md) 了解配置细节
- 遇到问题？提交 Issue！

## 技巧

💡 **技巧 1**：直接粘贴完整的抖音口令，无需手动提取链接

💡 **技巧 2**：分析教程视频时，AI 会自动识别类型并提供结构化内容

💡 **技巧 3**：可以在自然语言中添加具体要求，如"只要食材清单"

---

🎉 **开始享受智能视频分析吧！**

