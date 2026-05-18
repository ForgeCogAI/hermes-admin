# Hermes Admin

> 一个用于批量管理 [Hermes Agent](https://github.com/NousResearch/hermes-agent) 实例的 Web 管理系统。管理员预配置默认模板（模型、API Key、推理强度等），为每个用户一键启动独立的 Hermes Docker 容器，用户可在各自页面中覆盖配置。

## ✨ 核心功能

- **用户管理** — 创建/删除用户，自动分配数据目录和端口
- **一键部署** — 点击启动按钮自动创建并拉起 Docker 容器（gateway + dashboard）
- **配置模板** — 管理员统一配置默认模型、API Key、推理强度、最大轮次等
- **用户自定义** — 每个用户可在自己的配置页覆盖模板字段（留空 = 继承模板）
- **实时状态** — 自动轮询容器状态，运行中可直接打开 Dashboard
- **日志查看** — 内嵌实时查看容器日志
- **配置合并** — 容器启动时自动合并 `模板 + 用户覆盖`，生成 `cli-config.yaml`

## 🛠 技术栈

| 层 | 技术 |
|---|---|
| 后端 | FastAPI + SQLAlchemy + SQLite + PyYAML |
| 前端 | Vue 3 + Vite + Tailwind CSS |
| 容器管理 | `docker compose` (subprocess 调用) |
| 数据存储 | SQLite (`~/.hermes-admin/admin.db`) |

## 📁 项目结构

```
hermes-admin/
├── backend/                    # FastAPI 后端
│   ├── main.py                 # 应用入口
│   ├── database.py             # SQLite + SQLAlchemy
│   ├── models.py               # ORM 模型 (User, AdminTemplate)
│   ├── schemas.py              # Pydantic 模型
│   ├── routers/
│   │   ├── users.py            # 用户 CRUD + 容器控制
│   │   └── template.py         # 默认模板 CRUD
│   ├── services/
│   │   ├── docker_service.py   # docker compose 封装
│   │   └── config_service.py   # 配置合并 & cli-config.yaml 生成
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── views/              # 页面 (Dashboard, Template, UserConfig)
│   │   ├── components/         # 组件 (UserCard, ConfigForm, CreateUserModal)
│   │   ├── api/                # API 客户端
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── Dockerfile
├── docker-compose.yml          # 管理系统自身部署
└── README.md
```

## 🚀 快速开始

### 前置条件

1. **Docker** 和 **Docker Compose**（用于运行 Hermes 容器）
2. **构建 Hermes 镜像**（管理系统会调用它）：
   ```bash
   git clone https://github.com/NousResearch/hermes-agent.git
   cd hermes-agent
   docker build -t hermes-agent .
   ```

### 方式一：开发模式

**后端：**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**前端（新开终端）：**
```bash
cd frontend
npm install
npm run dev
```

访问 [http://localhost:5173](http://localhost:5173) （Vite dev server 会自动代理 `/api` 到后端 8000）

### 方式二：Docker 部署

```bash
# 在项目根目录
docker compose up -d
```

- 前端访问：[http://localhost:3000](http://localhost:3000)
- 后端 API：[http://localhost:8000](http://localhost:8000)
- API 文档：[http://localhost:8000/docs](http://localhost:8000/docs)

## ⚙️ 环境变量

| 变量 | 默认值 | 说明 |
|---|---|---|
| `ADMIN_DATA_DIR` | `~/.hermes-admin` | 管理系统数据目录（SQLite + 各用户数据） |
| `HERMES_IMAGE` | `hermes-agent` | Hermes 镜像名（如已发布到 registry 可改） |

## 🔌 端口规划

| 服务 | 端口 |
|---|---|
| 管理系统后端 | `8000` |
| 管理系统前端（dev） | `5173` |
| 管理系统前端（prod） | `3000` |
| 用户 Hermes Dashboard | `9200 – 9399`（自动分配） |

## 📖 使用流程

1. **配置默认模板** — 打开「默认模板」页面，填写模型（如 `anthropic/claude-opus-4-5`）、API Key、推理强度等，点击「保存模板」
2. **创建用户** — 打开「用户管理」页，点击「+ 新建用户」，填写用户名（仅小写字母/数字/`-`/`_`）
3. **启动容器** — 在用户卡片上点击「▶ 启动」，等待状态变为「运行中」
4. **打开 Dashboard** — 点击卡片上的「打开 Dashboard →」直接访问该用户的 Hermes Web UI
5. **个性化覆盖**（可选） — 点击「⚙ 配置」进入用户配置页，覆盖模板中的任意字段，可选择「保存并重启容器」立即生效

## 📂 数据目录布局

每个用户的数据独立隔离：

```
~/.hermes-admin/
├── admin.db                    # 管理系统数据库
└── users/
    ├── alice/
    │   ├── docker-compose.yml  # 自动生成
    │   ├── cli-config.yaml     # 合并模板+用户覆盖后生成
    │   └── ...                 # Hermes 运行时数据 (/opt/data)
    └── bob/
        └── ...
```

## 🔧 API 接口

完整接口文档：启动后端后访问 [http://localhost:8000/docs](http://localhost:8000/docs)

**主要接口：**

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/users` | 列出所有用户（含容器状态） |
| POST | `/api/users` | 创建用户 |
| DELETE | `/api/users/{id}` | 删除用户 |
| POST | `/api/users/{id}/start` | 启动用户容器 |
| POST | `/api/users/{id}/stop` | 停止用户容器 |
| POST | `/api/users/{id}/restart` | 重启用户容器 |
| GET | `/api/users/{id}/status` | 查询容器状态 |
| GET | `/api/users/{id}/logs` | 查看容器日志 |
| GET / PUT | `/api/users/{id}/config` | 获取/更新用户配置覆盖 |
| GET / PUT | `/api/template` | 获取/更新默认模板 |

## ⚠️ 注意事项

- **修改模板不会自动更新已有用户**。如需同步，请在用户配置页手动调整或重启该用户容器（重启时会重新合并模板）
- **删除用户不会删除磁盘数据**，只会停止容器并标记为不活跃。需手动清理 `~/.hermes-admin/users/{username}/`
- **多用户并发**：所有用户的 Hermes 容器共用同一台宿主机的 Docker，注意内存和 CPU 资源
- **API Key 安全**：当前 API Key 以明文存储在 SQLite 和 cli-config.yaml，生产环境建议加密或对接密钥管理服务

## 📜 License

MIT
