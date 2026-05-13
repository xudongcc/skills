# xudongcc/skills

一个用于存放 AI Agent Skills 的个人仓库，使用 [skills](https://skills.sh) 工具进行管理。

## 使用

通过 `pnpm dlx skills@latest` 安装本仓库中的 skills：

```sh
pnpm dlx skills@latest add https://github.com/xudongcc/skills --skill <skill-name>
```

例如，安装 `openclaw-lark-send-message`：

```sh
pnpm dlx skills@latest add https://github.com/xudongcc/skills --skill openclaw-lark-send-message
```

## Skills 列表

| Skill | 描述 |
| --- | --- |
| [openclaw-lark-send-message](skills/openclaw-lark-send-message/) | 发送飞书/Lark 消息、处理原生 @ 提及、查找用户或机器人 ID 及排查提及渲染问题 |

## 管理 Skills

本仓库使用 [skills](https://skills.sh) CLI 工具进行管理。`.agents/skills/skill-creator` 是用于创建和优化 skills 的内置工具。

### 创建新 Skill

```sh
pnpm dlx skills@latest add https://github.com/anthropics/skills --skill skill-creator
```

### 更新 Skill

```sh
pnpm dlx skills@latest update <skill-name>
```

## 开发

本仓库使用 [Turborepo](https://turborepo.dev) 作为 monorepo 工具，使用 pnpm 管理依赖。

```sh
# 安装依赖
pnpm install

# 构建所有包
pnpm build

# 开发模式
pnpm dev
```
