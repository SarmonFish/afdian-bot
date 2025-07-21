# 爱发电 (Afdian) x OpenAI 智能私信回复机器人

这是一个Python机器人，它集成了 LLM 模型，可以智能地自动回复在爱发电 (Afdian.com) 上收到的未读私信。

## 功能

- **监听未读消息**: 定期检查是否有新的未读私信。
- **AI智能回复**: 利用 OpenAI API 理解并生成对用户消息的回复。
- **标记已读**: 回复后，自动将对话标记为已读，避免重复回复。

## 工作原理

机器人通过模拟浏览器请求调用爱发电的内部API，并结合OpenAI API来实现智能回复。

1.  **加载配置**: 从 `config.json` 文件中读取用户的爱发电 `Cookie` 和 `OpenAI API Key`。
2.  **获取未读对话**: 调用爱发电的 `/api/message/dialogs` 接口，获取未读消息列表。
3.  **生成AI回复**: 对于每条未读消息，调用 OpenAI 的 ChatCompletion API，将用户消息作为提示 (Prompt) 来生成一个智能回复。
4.  **发送回复**: 调用爱发电的 `/api/message/send` 接口，将AI生成的回复发送给用户。
5.  **标记为已读**: 成功回复后，将对话标记为已读，以防重复处理。
6.  **循环执行**: 整个过程会以15秒为周期无限循环，直到手动停止脚本。

## 使用方法

### 1. 环境准备

- **安装 Python**: 请确保您的电脑上已经安装了 Python 3。
- **安装依赖库**: 需要 `requests` 和 `openai` 库。
  ```bash
  pip install requests openai
  ```

### 2. 配置

1.  **克隆或下载项目**: 将 `afdian_bot.py` 和 `config.json` 文件放在同一个文件夹下。
2.  **获取您的爱发电 Cookie**:
    - 在浏览器中登录您的爱发电账号。
    - 打开开发者工具 (通常按 `F12`)。
    - 切换到 “网络” (Network) 标签页。
    - 刷新页面，在任意一个网络请求 (如 `dialogs`) 的请求头 (Request Headers) 中找到 `Cookie` 字段，并复制其完整的值。
3.  **获取您的 OpenAI API Key**:
    - 登录您的 OpenAI 账户。
    - 前往 API Keys 页面 (https://platform.openai.com/account/api-keys)。
    - 创建一个新的 Secret Key 并复制它。
4.  **填写 `config.json`**:
    - 打开 `config.json` 文件。
    - 将您复制的 `Cookie` 和 `OpenAI API Key` 字符串分别粘贴到对应字段的值中。
    - (可选) 如果您需要使用代理或第三方的 OpenAI 兼容 API，请修改 `openai_api_base` 的值为您的 API 地址。
    - (可选) 您可以修改 `openai_model_name` 来指定使用的模型。
    - (可选) 您可以修改 `system_prompt` 来定义AI的性格、角色和行为。
    - 保存文件。

    ```json
    {
      "cookie": "在此处粘贴你的爱发电Cookie",
      "openai_api_key": "在此处粘贴你的OpenAI API Key",
      "openai_api_base": "https://api.openai.com/v1",
      "openai_model_name": "gpt-3.5-turbo",
      "system_prompt": "你是一个友好且乐于助人的助手。"
    }
    ```

### 3. 运行机器人

打开终端或命令行，进入项目所在的文件夹，然后运行脚本：

```bash
python afdian_bot.py
```

您会看到 "机器人已启动，开始监听新消息..." 的提示，之后机器人会开始工作。

## 使用 Docker 运行

为了方便部署，项目提供了 `Dockerfile`，您可以轻松构建和运行一个包含所有依赖的容器化应用。

### 1. 准备工作

- **安装 Docker**: 请确保您的系统上已经安装了 Docker。
- **准备 `config.json`**: 将您的 `config.json` 文件准备好，放在与 `Dockerfile` 同级的目录下。

### 2. 构建 Docker 镜像

在项目根目录下，打开终端或命令行，执行以下命令来构建镜像：

```bash
# 将 aifdian-bot 替换为您喜欢的镜像名称
docker build -t afdian-bot .
```

### 3. 运行 Docker 容器

使用以下命令来启动容器。这会将您本地的 `config.json` 文件挂载到容器内部，使得容器可以读取到您的配置。

```bash
# -d: 后台运行容器
# -v: 将本地的 config.json 挂载到容器的 /app/config.json
# --name: 给容器起一个名字，方便管理
docker run -d -v "$(pwd)/config.json:/app/config.json" --name my-afdian-bot afdian-bot
```

**注意**: `$(pwd)` 在 Linux/macOS/PowerShell 中代表当前目录。如果您在 Windows 的 CMD 中运行，需要将其替换为完整的绝对路径，例如 `C:\path\to\your\project\config.json`。

### 4. 管理容器

- **查看日志**: 
  ```bash
  docker logs -f my-afdian-bot
  ```
- **停止容器**:
  ```bash
  docker stop my-afdian-bot
  ```
- **重启容器**:
  ```bash
  docker restart my-afdian-bot
  ```

## 注意事项

- **凭证安全**: `Cookie` 和 `OpenAI API Key` 是重要凭证，请务必妥善保管，不要泄露给他人。
- **API 风险**: 爱发电的内部 API 可能会有变动，导致脚本失效。
- **自定义AI行为**: 您可以修改 `config.json` 文件中的 `system_prompt` 字段，或调整 `get_openai_reply` 函数中的模型参数，来自定义AI的性格和回复风格。
- **仅供学习**: 本项目主要用于学习和交流，请勿用于非法用途。