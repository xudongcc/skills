# xudongcc/skills

一个用于存放 AI Agent Skills 的个人仓库，使用 [skills](https://skills.sh) 工具进行管理。

## 使用

通过 `pnpm dlx skills@latest` 安装本仓库中的 skills：

```sh
pnpm dlx skills@latest add https://github.com/xudongcc/skills --skill <skill-name>
```

例如，安装 `nest-boot-best-practices`：

```sh
pnpm dlx skills@latest add https://github.com/xudongcc/skills --skill nest-boot-best-practices
```

## Skills 列表

| Skill | 描述 |
| --- | --- |
| [nest-boot-best-practices](skills/nest-boot-best-practices/) | 使用 `@nest-boot` 框架构建 NestJS 应用时的代码组织与架构规范 |
| [nest-boot-bullmq](skills/nest-boot-bullmq/) | 使用 `nest-boot-bullmq` 实现类型安全的异步任务队列 |
| [nest-boot-graphql](skills/nest-boot-graphql/) | 使用 `nest-boot-graphql` 构建 GraphQL API |
| [nest-boot-logger](skills/nest-boot-logger/) | 使用 `nest-boot-logger` 实现结构化日志 |
| [nest-boot-mikro-orm](skills/nest-boot-mikro-orm/) | 使用 `nest-boot-mikro-orm` 进行数据库操作的最佳实践 |

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
