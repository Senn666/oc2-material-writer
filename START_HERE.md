# 先看这里：按你用的 AI 工具选入口

| 你用的工具 | 怎么做 | 需要读几个文件 |
| --- | --- | --- |
| **WorkBuddy / CodeBuddy**（支持 skill 目录） | 把整个仓库目录放到 `<工作区>/.workbuddy/skills/oc2-material-writer/`，或用户级 `~/.workbuddy/skills/oc2-material-writer/`。之后直接说「雪」「透明蜂蜜」即可自动触发。也可以解压 Release 里的 zip。 | 只装目录，`SKILL.md` 自动加载 |
| **dsh / Claude Code / 其它能读本地文件的 AI** | 把仓库目录放进工作区，开场先让 AI 读 `MATERIAL_GUIDE.md`，再按它的要求补充 `references/` 与 `assets/`。 | `MATERIAL_GUIDE.md` + 按需读附表和模板 |
| **豆包 / DeepSeek 网页版 / 任何纯对话 AI** | 打开 `PROMPT.md`，**全选复制整段**，粘进对话框发送；然后按它的第 0 节回答四个问题，再给材质词。 | 只有 `PROMPT.md` 一份，自包含 |

> `PROMPT.md` 里已经内嵌了完整规则、预设词库和两份全量模板，粘贴时不需要额外上传任何文件。新开一轮对话要重新粘一次。

---

## 不管用哪条路，首次都要准备四件事

1. 你的 `materialLibrary.txt` 绝对路径（通常在 `<游戏包>/BepInEx/plugins/OC2ModelTest/Model/materialLibrary.txt`）。
2. 输出目录绝对路径（放生成 txt 的地方，游戏不会读）。
3. `config.txt` 里目标物体的资源文件夹名、材质槽数量、要改第几槽。
4. 本项目的默认材质ID：库里 `bundle39 | mat_sk_crate_01` 的索引；没有就让 AI 问你。

**编号必须每次从你自己的库现算**，本包不含任何可直接照抄的编号。`references/examples.md` 里的编号只是示意。

## 前提

- 已装 Overcooked! 2 与 **OC2ModelTest 模型替换插件**。本包只产出该插件读取的 `material.txt`，不提供模型、贴图或 DLL。
- 模型在 Blender 里确实分出了对应数量的材质槽，槽顺序与 OBJ 里 `usemtl` 首次出现顺序一致。

完整说明见 `README.md`，规则细节见 `MATERIAL_GUIDE.md`。
