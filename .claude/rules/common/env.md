# Environment Variables (.env) 规范

本规则用于让 agent 主动根据当前项目生成、更新和审计环境变量模板。默认目标是“最小必要、可解释、可复制、安全”，而不是把所有可能用到的服务都塞进 `.env.example`。

## 文件命名与用途

| 文件 | 用途 | 提交 Git |
|------|------|----------|
| `.env` | 默认环境变量 | ❌ |
| `.env.local` | 本地覆盖（个人） | ❌ |
| `.env.development` | 可共享的开发默认值，不含密钥 | ✅（仅非敏感值） |
| `.env.production` | 生产环境变量清单，不含密钥 | ✅（仅非敏感值） |
| `.env.example` | 变量文档/模板 | ✅ |
| `.env.*.local` | 环境特定本地覆盖 | ❌ |

## Agent 处理流程

当用户要求创建、优化、迁移或审计 `.env` / `.env.example` / 环境变量规则时，先按以下流程处理：

1. **识别项目类型**：读取根目录清单和入口文件，例如 `package.json`、`pnpm-lock.yaml`、`pyproject.toml`、`requirements.txt`、`Cargo.toml`、`go.mod`、`Dockerfile`、`docker-compose.yml`、`README.md`、`AGENTS.md`。
2. **扫描真实引用**：用 `rg` 查找环境变量读取点，默认排除 `.git/`、`.claude/`、`node_modules/`、`dist/`、`build/`、`.next/`、`coverage/`、`workspace/`。
   - JavaScript/TypeScript: `process.env.`, `import.meta.env`, `PUBLIC_`, `VITE_`, `NEXT_PUBLIC_`
   - Python: `os.getenv`, `os.environ`, `pydantic.BaseSettings`, `dotenv`
   - Shell/Docker: `${VAR}`, `$VAR`, `env_file`, `ARG`, `ENV`
   - Generic config: `DATABASE_URL`, `REDIS_URL`, `*_API_KEY`, `*_TOKEN`, `*_SECRET`
3. **分类变量**：按 Project、Runtime、Paths、Auth、Database、Cache、Storage、LLM、Observability、Feature Flags、Deployment 分组。
4. **只保留项目需要的变量**：代码或工作流没有用到的服务变量不要默认加入；可选集成放到明确的 Optional 区块，并保持空值。
5. **标注必填与来源**：必填变量用注释说明用途和获取来源；敏感变量只放空值或 `your-...-here`，禁止示例真实格式过于接近可用密钥。
6. **路径自适应**：所有项目内路径默认相对项目根目录；只有用户明确要发布到外部目录时，才允许在本地 `.env` 写绝对路径。
7. **同步规则**：如果修改 `.claude/rules/**`、`.claude/skills/**`、`.claude/agents/**` 或 `.claude/scripts/**`，按项目规则运行 `.claude/scripts/sync-codex-to-claude.sh`。

推荐扫描命令：

```bash
rg -n --hidden \
  -g '!.git/**' -g '!.claude/**' -g '!node_modules/**' \
  -g '!dist/**' -g '!build/**' -g '!.next/**' -g '!coverage/**' \
  'process\.env|import\.meta\.env|os\.getenv|os\.environ|\$[A-Z][A-Z0-9_]+|\$\{[A-Z][A-Z0-9_]+\}|[A-Z][A-Z0-9_]+_API_KEY|DATABASE_URL|REDIS_URL'
```

项目内可直接运行自检脚本：

```bash
.claude/scripts/check-env-template.sh
```

默认模式会在 `.env.example` 缺少真实引用变量或疑似包含真实敏感值时失败；`--strict` 还会把未被扫描文件引用的模板变量视为失败。

## 安全规则

1. **永远不提交** `.env`、`.env.local`、`.env.*.local`
2. **禁止**在代码中硬编码密钥、Token、密码
3. **禁止**在日志中打印环境变量值
4. `.env.example` 中只写空值或不可用占位符（如 `your-key-here`）
5. **禁止**把生产域名、内部服务地址、个人目录或 vault 绝对路径写进共享模板，除非它们本来就是公开配置
6. 变量名包含 `KEY`、`SECRET`、`TOKEN`、`PASSWORD`、`PRIVATE`、`DSN` 时，默认视为敏感

## 路径规范

1. **禁止**在代码中硬编码绝对路径（如 `/Users/xxx/data/`、`C:\Users\xxx\`）
2. **文件路径**应通过 `.env` 中的环境变量定义，使用相对路径（如 `./workspace`）
3. **示例**：路径变量统一在 `.env` 中管理，代码中通过 `process.env.WORKSPACE_PATH` + `path.resolve()` 引用
4. **自动配置**：运行项目时，路径基于当前工作目录自动解析，无需手动设置绝对路径
5. **外部发布路径**：Obsidian vault、云盘同步目录等外部路径只写入本地 `.env`，不要写入 `.env.example` 的真实值

## 变量命名

```bash
# 格式：大写下划线，前缀表示作用域
APP_NAME=study-system
APP_ENV=development
APP_PORT=3000

# API 密钥加供应商或服务前缀
OPENAI_API_KEY=
MINIMAX_API_KEY=

# 数据库
DATABASE_URL=

# 路径（相对路径，不硬编码绝对路径）
WORKSPACE_PATH=./workspace
OUTPUT_PATH=${WORKSPACE_PATH}/output
CHAPTERS_PATH=${WORKSPACE_PATH}/chapters

# 布尔值用小写
DEBUG=true
FEATURE_X_ENABLED=false
```

## .env.example 模板

```bash
# === Project Identity ===
APP_NAME=study-system
APP_ENV=development
NODE_ENV=development
APP_PORT=3000
APP_URL=http://localhost:3000

# === Workspace Paths ===
# Paths are relative to the project root.
WORKSPACE_PATH=./workspace
OUTPUT_PATH=${WORKSPACE_PATH}/output
CHAPTERS_PATH=${WORKSPACE_PATH}/chapters
WORKFLOW_RUNS_PATH=${WORKSPACE_PATH}/workflow-runs

# Optional external publishing.
OBSIDIAN_VAULT_PATH=
OBSIDIAN_NOTES_DIR=
OBSIDIAN_MOC_PATH=

# === Runtime Behavior ===
LOG_LEVEL=info
DEBUG=false
DRY_RUN=false
AUTO_CONFIRM=false
CODEX_AUTO_GIT=0
CODEX_AUTO_GIT_PUSH=0

# === LLM / Research Providers ===
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
MINIMAX_API_KEY=
DEFAULT_LLM_PROVIDER=
DEFAULT_LLM_MODEL=

# === Optional Services ===
DATABASE_URL=
REDIS_URL=
SENTRY_DSN=
```

## 代码中使用

```javascript
// Node.js
const apiKey = process.env.API_KEY;

// 必需变量启动时校验
const required = ['API_KEY', 'DATABASE_URL'];
for (const key of required) {
  if (!process.env[key]) {
    throw new Error(`Missing required env: ${key}`);
  }
}

// 路径解析：使用 path.resolve 相对路径
const path = require('path');
const workspacePath = path.resolve(process.env.WORKSPACE_PATH);
const outputPath = path.resolve(process.env.NOTES_OUTPUT_PATH);
```

## 更新 `.env.example` 的判断标准

- 新变量必须能追溯到代码引用、脚本引用、工作流需要或用户明确要求。
- 删除变量前先确认没有引用点，避免破坏部署。
- 可选集成变量默认空值；必填变量用注释说明什么时候需要填写。
- 如果项目使用 Vite、Next.js、Nuxt、Expo 等前端框架，只有可以暴露到浏览器的变量才能使用 `PUBLIC_` / `VITE_` / `NEXT_PUBLIC_` 前缀。
- 如果 dotenv 实现不支持 `${VAR}` 展开，不要在模板里依赖变量嵌套；改用完整相对路径或在启动脚本中解析。
- 每次变更后检查 `.gitignore` 是否覆盖真实 `.env` 文件。

## .gitignore 确保覆盖

```gitignore
# 已配置
.env
.env.local
.env.*.local
```

## 检查清单

- [ ] `.env` 在 `.gitignore` 中
- [ ] `.env.example` 提交到仓库（无真实密钥）
- [ ] 敏感变量命名带 `_KEY`、`_SECRET`、`_TOKEN` 后缀
- [ ] 启动时校验必需变量
- [ ] 不在 `console.log` 中打印环境变量
- [ ] 文件路径通过环境变量配置，不硬编码绝对路径
- [ ] `.env.example` 只包含当前项目真实需要或明确可选的变量
- [ ] agent 已先扫描项目栈和 env 引用，再改模板
- [ ] `.claude/scripts/check-env-template.sh` 通过
