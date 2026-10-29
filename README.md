# xudongcc/skills

个人 AI Agent Skills 仓库，用于沉淀可复用的工程规范、工具集成和自动化工作流。

## 使用

建议在项目根目录中以项目级别安装本仓库中的所有 skills，并安装到通用 `.agents/skills/` 目录：

```sh
npx skills add https://github.com/xudongcc/skills \
  --agent universal \
  --copy \
  -y
```

如只需安装单个 skill，可以使用 `--skill <skill-name>` 指定名称：

```sh
npx skills add https://github.com/xudongcc/skills \
  --skill xudong-skill-creator \
  --agent universal \
  --copy \
  -y
```

## Skills 列表

<!-- BEGIN GENERATED SKILLS -->

| Skill                                                            | 描述                                                                                                                                                                                                                      |
| ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [xudong-code-review](skills/xudong-code-review/)                                 | Structured Codex code review when explicitly requested.                                                                                                                                         |
| [xudong-create-feature-prd](skills/xudong-create-feature-prd/) | 基于 Epic（史诗级需求）为新功能创建产品需求文档（PRD），将功能构想或技术支撑项细化为完整、可验收的需求。 |
| [xudong-i18next](skills/xudong-i18next/)                                       | Automatically maintain i18next during normal development, including runtime usage, keys and namespaces, local resources and translations, language loading, generated types, and i18next-cli extraction and verification. |
| [xudong-skill-creator](skills/xudong-skill-creator/)                           | Create new skills, modify and improve existing skills, and measure skill performance. Use for skill creation, editing, evals, benchmarking with variance analysis, and trigger-description optimization.                  |

<!-- END GENERATED SKILLS -->

## 维护

`skills/` 是所有 skill 的源码目录。需要在本仓库中直接使用的 skill 通过 `.agents/skills/` 下的相对软链接指向同一份源码。

修改 skill 后运行快速校验：

```sh
python3 skills/xudong-skill-creator/scripts/quick_validate.py skills/<skill-name>
```
