# 使用官方 Python 基础镜像
FROM python:3.9-alpine

# 设置工作目录
WORKDIR /app

# 将当前目录内容复制到工作目录中
COPY . /app

# 安装项目依赖
RUN pip3 install --no-cache-dir -r requirements.txt

# 运行应用程序
CMD ["python3", "./main.py"]
