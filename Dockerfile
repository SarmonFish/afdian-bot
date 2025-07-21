# 使用官方 Python 运行时作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 将依赖文件复制到工作目录
COPY requirements.txt .

# 安装所需的包
RUN pip install --no-cache-dir -r requirements.txt

# 将项目文件复制到工作目录
COPY . .

# 确保 config.json 存在（使用模板）
# 用户在运行时应通过卷挂载自己的 config.json
RUN cp config.json config.json.template

# 容器启动时运行 afdian_bot.py
CMD ["python", "afdian_bot.py"]
