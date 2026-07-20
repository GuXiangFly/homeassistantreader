# syntax=docker/dockerfile:1

# 使用包含 uv 的官方镜像作为基础
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# 设置工作目录
WORKDIR /app

# 启用 uv 的编译字节码以加速启动
ENV UV_COMPILE_BYTECODE=1

# 将依赖文件复制到容器中
COPY pyproject.toml uv.lock ./

# 同步依赖（使用 --no-install-project 和 --no-dev 以仅安装生产依赖）
RUN uv sync --frozen --no-install-project --no-dev

# 复制项目源代码
COPY main.py ./
COPY src/ ./src/

# 复制 .env 文件（用户配置的环境变量）
COPY .env ./

# 再次同步以安装项目本身
RUN uv sync --frozen --no-dev

# 使用 uv run 启动应用
CMD ["uv", "run", "main.py"]