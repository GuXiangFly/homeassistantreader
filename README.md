# HomeAssistant Reader

将 **Home Assistant** 传感器数据实时同步到 **PostgreSQL**，便于后续使用 **Grafana** 等工具进行可视化展示。

## ✨ 功能特性

- 🏠 从 Home Assistant REST API 采集传感器状态
- 🔄 每 **5 秒** 自动轮询，实时入库
- 🗄️ 数据持久化到 PostgreSQL，自带表结构自动初始化
- 🐳 支持 Docker 一键部署
- 📝 日志同时输出到文件和终端，北京时间显示
- ⚡ 使用 [uv](https://docs.astral.sh/uv/) 进行高效的 Python 包管理

## 📋 前置要求

- Python 3.12+（本地运行）
- [uv](https://docs.astral.sh/uv/getting-started/installation/)（本地运行）
- Docker（容器化部署）
- 一个运行中的 Home Assistant 实例
- 一个可用的 PostgreSQL 数据库

## 🔧 环境变量

复制 `.env.example` 为 `.env` 并按实际情况填写：

```bash
cp .env.example .env
```

| 变量名 | 必填 | 默认值 | 说明 |
|--------|------|--------|------|
| `HA_URL` | 是 | `http://192.168.31.222:8123` | Home Assistant 地址 |
| `HA_TOKEN` | 是 | - | Home Assistant 长期访问令牌（Long-Lived Access Token） |
| `PG_HOST` | 是 | `192.168.31.109` | PostgreSQL 主机地址 |
| `PG_PORT` | 否 | `5432` | PostgreSQL 端口 |
| `PG_DBNAME` | 否 | `homeassistant_reader_db` | 数据库名称 |
| `PG_USER` | 否 | `teslamate` | 数据库用户名 |
| `PG_PASSWORD` | 否 | `password` | 数据库密码 |

> 💡 **获取 HA_TOKEN**：在 Home Assistant 中进入「个人资料」→ 页面底部「长期访问令牌」→ 创建令牌。

## 🚀 快速开始

### 方式一：Docker 部署（推荐）

#### 1. 构建镜像

```bash
docker build -t homeassistantreader .
```

#### 2. 运行容器

```bash
docker run -d \
  --name ha-reader \
  --restart unless-stopped \
  -v $(pwd)/logs:/app/logs \
  homeassistantreader
```

#### 常用管理命令

```bash
# 查看日志
docker logs -f ha-reader

# 停止容器
docker stop ha-reader

# 启动容器
docker start ha-reader

# 删除容器
docker rm -f ha-reader
```

### 方式二：本地运行

```bash
# 安装依赖
uv sync

# 启动服务
uv run main.py
```

## 🗄️ 数据库表结构

程序启动时会自动创建以下表：

```sql
CREATE TABLE IF NOT EXISTS sensor_metrics (
    id              BIGSERIAL PRIMARY KEY,
    metric_time     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    sensor_name     VARCHAR(256) NOT NULL,
    sensor_value    DOUBLE PRECISION NOT NULL
);

-- 时间范围查询索引
CREATE INDEX idx_sensor_metrics_time ON sensor_metrics(metric_time DESC);
CREATE INDEX idx_sensor_metrics_name_time ON sensor_metrics(sensor_name, metric_time DESC);
```

## 📊 配合 Grafana 展示

1. 在 Grafana 中添加 PostgreSQL 数据源
2. 配置数据库连接信息（与 `.env` 中一致）
3. 创建 Dashboard，使用类似以下的 SQL 查询：

```sql
SELECT
  metric_time AS time,
  sensor_name AS metric,
  sensor_value AS value
FROM sensor_metrics
WHERE sensor_name = 'sensor.iot_cn_2047343303_padw2p_electric_power_p_3_3'
ORDER BY metric_time
```

## 📝 日志说明

- 日志文件位于 `logs/reader.log`
- 同时输出到终端，便于 Docker 环境下查看
- 所有日志时间均使用 **北京时间 (Asia/Shanghai)**
- 容器运行时可通过挂载卷持久化日志：`-v $(pwd)/logs:/app/logs`

## 🔌 默认采集的传感器

当前版本默认采集以下两个功率传感器：

| 传感器 entity_id | 说明 |
|------------------|------|
| `sensor.iot_cn_2047343303_padw2p_electric_power_p_3_3` | 米家智能插座功率 |
| `sensor.cuco_cn_534987372_cp5prd_electric_power_p_10_5` | 酷客智能插座功率 |

> 如需采集其他传感器，请修改 `src/service/homeassistant_reader_service.py` 中的 `entity_id_list`。

## 📁 项目结构

```
homeassistantreader/
├── main.py                          # 程序入口
├── pyproject.toml                   # 项目配置与依赖
├── uv.lock                          # 依赖锁定文件
├── .env                             # 环境变量（需自行配置）
├── Dockerfile                       # Docker 构建文件
├── src/
│   ├── config/log_config.py         # 日志配置
│   ├── dao/homeassistant_pgsql_dao.py   # 数据库访问层
│   └── service/homeassistant_reader_service.py  # 核心业务逻辑
└── logs/                            # 日志输出目录
```

## 📄 License

MIT