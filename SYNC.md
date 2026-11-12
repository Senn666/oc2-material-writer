# 维护说明：本机专用版 → 通用发行版

发行版与维护者本机的工作区 skill 是**两份独立副本**：

- **本机专用版**：写死了权威游戏包路径、当前项目的库快照与已落地状态、默认材质ID 7、以及 Oven / Cakemixer 等具体物体的落地记录。日常干活用它，不对外发布。
- **本发行版**：不含任何路径、编号、项目数据，所有值由使用者首次运行时提供并现场核对。

本机版出新规则后，按下面的清单**手动摘录**到发行版。发行版的改动不反向覆盖本机版。

## 可以原样带过来的（通用知识）

| 内容 | 落地位置 |
| --- | --- |
| 插件解析规则、`HasProperty`、行内注释陷阱 | `MATERIAL_GUIDE.md` 一/六、`PROMPT.md` 第 1 节 |
| 语义维度 → 参数展开公式 | `references/parameter-map.md`、`PROMPT.md` 第 4 节 |
| 预设词库、极哑光覆盖表、暖色液体覆盖表 | `references/presets.md`，**并同步 `PROMPT.md` 附录 A** |
| 两份纯净全量模板 | `assets/*.txt`，**并同步 `PROMPT.md` 附录 B / C** |
| 编号 = 库有效行序号、跨项目不复用、指纹核对逻辑 | `MATERIAL_GUIDE.md` 三、`PROMPT.md` 第 2 节 |
| OBJ `usemtl` 槽顺序规则、多材质槽落地、中文命名边界 | `MATERIAL_GUIDE.md` 七、`SKILL.md` |
| 校验脚本的算法 | `scripts/*.py`（去掉任何本机路径依赖） |

## 绝不能带过来的（本机专属）

| 内容 | 发行版里怎么处理 |
| --- | --- |
| 游戏包、工作区的绝对路径（任何盘符路径） | 全部换成 `<游戏包>/...`、`<输出目录>/` 占位符 |
| 具体编号（如「雪=9 / 金属=10 / 透明蜂蜜=11」） | 删掉；改为「按本次库核对结果」 |
| 当前库的条目数、sha256 指纹、`next_id` | 删掉；`registry.example.json` 里这些字段为空 |
| 默认材质ID 7 | 改为「在该库查 `bundle39 | mat_sk_crate_01` 的索引，查不到就问」 |
| 具体物体（Oven / Cakemixer_Body）的落地状态、测试日期 | 只能进 `references/examples.md`，且开头大字标明编号禁止照抄 |
| 本机 `registry.json` 的 `entries` / `projects` / `library_fingerprint` | 全部清空 |
| 使用者名字、机器目录结构、备份路径 | 全删 |

## 每次同步后必查

1. `PROMPT.md` 附录 A 与 `references/presets.md` 内容一致（它是全文副本，不是摘要）。
2. `PROMPT.md` 附录 B / C 与 `assets/template_*.txt` **逐行一致**（通用 53 行、玻璃 51 行）。
3. 全仓扫描无绝对路径、无具体编号、无本机项目名：

```bash
grep -rInE "[A-Za-z]:[/\\\\]" --exclude-dir=dist .
```

4. 跑一次 `python scripts/validate_material.py` 的正例/反例，以及 skill 结构打包校验。

## 版本号

本包不设复杂版本机制。改动词库或规则时，在 commit message 里写清改了哪一类内容，别人 `git diff` 就能看到；发布 zip 时按日期命名 Release 即可。
