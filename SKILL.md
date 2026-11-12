---
name: oc2-material-writer
description: 本 skill 把「雪」「冰」「金属」「透明蜂蜜」这类材质描述词转换成 Overcooked! 2 的 OC2ModelTest 模型替换 MOD 可直接使用的 material.txt 全量参数文件，并为每个词分配独立的 materialLibrary.txt 新编号。当用户只给出一个材质词、给出「湿雪」「生锈铁」等材质描述、或要求「写/生成/做 XX 材质」「材质文件 txt」「material.txt」「材质编号」时，应使用本 skill；也用于查询编号登记表、修改预设词库、跨项目核对 materialLibrary.txt 编号。自动触发，无需斜杠命令。
agent_created: true
---

# OC2 材质文件生成器（通用发行版）

## 目的

把一个材质描述词转成三样东西：一份可直接复制使用的 `material.txt` 全量参数文件、一个 `materialLibrary.txt` 新编号、一份「落地三步」清单。

本包**不含任何使用者的路径或编号数据**。所有路径、编号、默认材质ID 都必须在首次使用时向使用者询问并从其真实 `materialLibrary.txt` 现场核对。

## 首次配置（每次新项目必做）

开始生成之前，必须向使用者确认以下四项。**没拿到之前不要猜、不要假设、不要沿用任何示例里的编号。**

1. `materialLibrary.txt` 的绝对路径（通常在 `<游戏包>/BepInEx/plugins/OC2ModelTest/Model/materialLibrary.txt`）。
2. 输出目录的绝对路径（工作区里放生成 txt 的地方，游戏不会读它）。
3. `config.txt` 里目标物体的资源文件夹名，以及该物体有几个材质槽、要改第几槽。
4. 该项目的**默认材质ID**：库里 `bundle39 | mat_sk_crate_01` 的索引；库里没有这一行就请使用者指定一个。

把 `registry.example.json` 复制成 `registry.json` 后填入上述信息。`registry.json` 是本机私有数据，不应提交到版本库。

## 绝对约束（违反即产物失效）

1. **解析规则**（依据 OC2ModelTest 插件行为整理）：逐行 Trim → `#` 开头的整行跳过 → `KEYWORD=xxx` 走 `EnableKeyword` → 其余按 `=` 切成恰好 2 段，值含逗号且 ≥3 段走 `SetColor`（A 缺省 1），否则 `float.TryParse` 走 `SetFloat`；只有 `HasProperty` 为真的属性才生效，写错的属性名静默忽略。
2. **禁止行内注释**。解析器不剥离 `#` 之后的内容，`_Metallic=0.2  # 哑光` 会让整行失效，甚至中断该文件后续所有行。注释只能独占一行且以 `#` 开头。
3. **必须输出全量参数文件**，不能只写差异行。解析是覆盖式的，未写的参数保留基底材质原值；通用基底源自灭火器材质，带一堆暖红节点（`_MaskColor` 暗红、`_highlight_colour` 暖红、`_node_8633` 橙、`_node_9884` 奶油），玻璃基底的 `_EmissionColor` 原值甚至是绿色自发光。只改 `_Color` 的「雪」会是粉红雪，漏写 `_EmissionColor` 的「蜂蜜」会发绿光。
4. **只写模板里已存在的参数名**。绝不发明 `_node_XXXX` 或新参数；`KEYWORD` 一律保留模板自带的 6 个，唯一例外是「极哑光词」可额外追加 `_SPECULARHIGHLIGHTS_OFF` / `_GLOSSYREFLECTIONS_OFF`（见 `references/parameter-map.md` 第六节）。
5. **默认不修改任何插件现有文件**：`materialLibrary.txt`、`config.txt`、`Model/Resources/**` 一概不动；只写本包的 `registry.json` 与输出目录下的 txt。使用者单独授权落地时按「先备份再改」执行，这是对常规流程的显式例外。
6. 颜色一律 `R,G,B,A`，0～1 之间 3 位小数；标量 2 位小数；A 缺省 1（仅透明类词例外）。
7. **编号绝不跨项目复用**。每个项目（不同游戏包 / 工作区）各有自己的 `materialLibrary.txt`：同一个词「雪」在 A 项目是 9，在 B 项目可能压根不存在，也可能对应完全不同的行。任何涉及编号的回答都必须先运行 `scripts/check_library.py` 读真实库核对，禁止凭 `registry.json` 的记忆直接报号；`entries` 只对 `library_path` 指向的那一份库有效。

## 默认材质ID（不调参的槽）

`config.txt` 里凡是没有显式指定新材质的槽，一律填**本项目核对过的默认材质ID**，且**不放参数文件**（插件用 `File.Exists` 判断，缺文件即用库材质原样）。只有要改的那个槽换成新编号。

- 默认值不是常量：先在该项目库里查 `bundle39 | mat_sk_crate_01` 的索引；查不到就让使用者指定。原作者的本机项目里它是 7，**其它项目不可照抄 7**。
- 单槽物体示例：`物体 | ... | 资源文件夹 | <默认ID> | TRUE`。
- 多槽物体写成 `<默认ID>,<新编号>` 这类形式；**不要**用 `0`、`-1` 或空着当默认。
- 这与「生成材质用的基底」是两件事：默认ID 是 config 的材质ID；新材质的基底仍按语义选通用（`bundle46`）或玻璃（`bundle166`）。透明类词必须走玻璃基底。
- 每次核对时都要检查默认ID 是否越界、该行是否仍是预期材质。`scripts/check_library.py` 会做这项检查。

## 路径约定（全部是占位符，不是真实路径）

| 用途 | 占位路径 |
| --- | --- |
| 权威 `materialLibrary.txt` / `config.txt` | `<游戏包>/BepInEx/plugins/OC2ModelTest/Model/` |
| 权威资源目录 | 同上 `Model/Resources/<资源文件夹>/` |
| 本包产物 | `<输出目录>/`（游戏不会读） |

本包不做路径自动探测：Steam 库位置、插件目录名因人而异，猜错比问一句更糟。工作区里若存在插件的**原版参考副本**，只能用来看模板、教程、说明文档，**禁止拿它算编号或当作落地目标**。

## 工作流

### 1. 解析描述词

把用户输入归一化成**一个词**（去掉「材质」「生成」「写一个」等填充词）。例如「给我写个雪的材质」→ `雪`，「湿雪」→ `湿雪`。
在 `references/presets.md` 里查该词：命中则用表中语义维度；未命中（含带修饰词的组合）则按 `references/parameter-map.md` 的语义规则现推，并在回复里列出所做的假设。描述词含糊（如「好看」）时不要追问，直接按 OC2 原版卡通默认出一版并列出假设。

### 2. 选基底

| 条件 | 基底 | 追加到库的那一行 |
| --- | --- | --- |
| 不透明词（默认） | 通用 / Standard 系 | `bundle46 \| mat_sk_fire_extinguisher_01` |
| 透明类词：冰、玻璃、水、水晶、蜂蜜、糖浆、果汁、液、透明、气泡、果冻、树脂、琥珀、夜光 | 玻璃 / ShaderForge 系 | `bundle166 \| mat_dlc2_smoothiemaker_glass_02` |

两套基底参数几乎不重叠，禁止混写。玻璃基底出现在多材质配置时，回复里附一句「玻璃材质尽量不要放在材质栏首位」。

### 3. 核对库并分配编号（每次必做）

**先核对、再编号。** 编号 = **本项目** `materialLibrary.txt` 中非注释非空行的序号（从 0 起）。

1. **确定库路径**：默认用 `registry.json` 的 `library_path`；使用者提到别的项目或给了新路径时改用那个路径。
2. **运行核对脚本**（有 Python 时必须跑，不得跳过）：

```bash
python "<本包目录>/scripts/check_library.py" "<本项目 materialLibrary.txt>" --registry "<本包目录>/registry.json"
```

   没有 Python 时按「无脚本核对步骤」手工完成：`MATERIAL_GUIDE.md` 第三节。

3. **按脚本结论处理**：

| 状态 | 处理 |
| --- | --- |
| `PASS` | 登记可复用；新词编号 = `next_id`（即有效行数） |
| `NEW_PROJECT` | 没有该项目档案：**所有编号按本次库内容重新分配**，禁止复用其它项目的编号；确认后把该项目写入 `projects` |
| `PROJECT_SWITCH` | 已载入该库的项目档案，用档案里的 `entries` 与默认材质ID |
| `FINGERPRINT_CHANGED` | 库被改过，逐词重新核对，一律以库内容为准 |
| `MISMATCH` / `OUT_OF_RANGE` | 登记的 id 与库不符：按 `base_line` 在库中的实际索引重算；库里没有该行则要追加，编号 = 有效行数 |
| `DEFAULT_INVALID` | 默认材质ID 越界或指向了别的材质 → 重新指定 |
| `NO_FINGERPRINT` | 登记表尚未记录指纹，核对通过后补齐 |

4. **新词**：即使库里已有相同 `bundle | 材质名` 行，也要为该词**单独追加一行**（保持一词一号），编号 = 当前有效行数 N；写回 `entries`，`next_id` 设为 N+1。
5. **收尾**：把本次 `line_count` / `sha256` 写回 `registry.json` 的 `library_fingerprint`（脚本 `--json` 可直接取）。
6. 头部注释、落地清单、config 里写的编号一律取**本次核对结果**；与旧记录不一致时，在回复里明确列出「旧 X → 新 Y」的差异。

### 4. 展开全量文件

1. 读 `assets/template_common.txt` 或 `assets/template_glass.txt`（纯净模板，无注释）。
2. 按 `references/parameter-map.md` 把语义维度展开成具体参数值，**覆盖**模板中对应项；未涉及的标量、内部节点参数一律保持模板原值；`KEYWORD` 行原样保留在末尾。若该词在 `references/presets.md` 的「极哑光覆盖表」中，再按 parameter-map 第六节套用零反光覆盖（并追加 2 个 `*_OFF` KEYWORD）。
   - 使用者反馈「XX 有点反光 / 太亮」时，不要只调 `_Roughness`：直接把该词加入极哑光覆盖表，重生成并覆盖输出文件；若已落地到游戏包，同步覆盖对应 `materialN.txt`（先备份）。
   - 玻璃基底的暖色透明液体词（蜂蜜、糖浆、果汁）还要套用 `presets.md` 的「暖色液体覆盖表」，并强制 `_EmissionColor=0,0,0,1`（模板原值是绿色自发光）。
3. 生成 5～6 行头部整行注释，正文零行内注释：

```
# OC2 材质：雪
# 材质ID: <本次核对得到的编号>（新编号，需追加到 materialLibrary.txt）
# 基底: bundle46 | mat_sk_fire_extinguisher_01（通用 / 不透明）
# 落地: ① 库末尾追加上面基底行 ② config 对应行材质ID 改成本次编号 ③ 本文件复制到 Model/Resources/<资源文件夹>/material.txt（多材质槽 N 改名为 materialN.txt）
# 生成: oc2-material-writer | OC2 原版卡通风
```

### 5. 写文件并校验

核对脚本报 FAIL 时先按步骤 3 解决，再生成。写到 `<输出目录>/<词>.txt`（同名直接覆盖）。随后必须运行：

```bash
python "<本包目录>/scripts/validate_material.py" "<输出文件>" common
# 玻璃基底把 common 换成 glass；省略第二参数时脚本从头部注释推断
```

校验不通过就修正文件并重跑，不得把未通过校验的产物交给使用者。

### 6. 回复使用者

按顺序给出：① 文件全文（代码块，便于直接复制）② 3～5 行「为什么这么调」的参数解读 ③ 落地三步清单（写明具体追加行、config 改几号、复制目标路径）④ 核对脚本结论与参数校验结果 ⑤ 若走了现推路径，列出假设并说明可用一句话改。解读与清单只放对话里，不写进文件。

## 参考资源

| 文件 | 用途 |
| --- | --- |
| `MATERIAL_GUIDE.md` | 平台无关的完整规则（含无 Python 时的手工核对步骤） |
| `PROMPT.md` | 自包含提示词，给不能读取本地文件的 AI 对话工具整段粘贴使用 |
| `START_HERE.md` | 按所用 AI 工具选择入口 |
| `assets/template_common.txt` | 0 号通用基底纯净全量模板（53 行，含 6 条 KEYWORD） |
| `assets/template_glass.txt` | 2 号玻璃基底纯净全量模板（51 行，无 KEYWORD） |
| `references/parameter-map.md` | 解析规则、语义维度 → 参数展开公式、数值规范、零反光覆盖、坑清单 |
| `references/presets.md` | 预设词语义维度表 + 极哑光覆盖表 + 暖色液体覆盖表 |
| `references/examples.md` | 多材质槽落地示例。**里面的编号是示例，禁止照抄** |
| `scripts/check_library.py` | 读真实库、算指纹、核对登记编号与默认材质ID、识别跨项目切换（可选） |
| `scripts/validate_material.py` | 语法、行内注释、参数白名单、全量完整性、头部元信息校验（可选） |
| `registry.example.json` | 空登记表模板，复制成 `registry.json` 后填写 |

## 落地三步清单模板

1. 在**本项目**的 `materialLibrary.txt` 末尾追加该词的基底行（例如 `bundle166 | mat_dlc2_smoothiemaker_glass_02`）；追加后的索引 = 步骤 3 核对得到的编号，**不要照抄任何示例或旧项目的编号**。
2. 把同目录 `config.txt` 里目标物体那行的材质ID 列改成对应编号：单槽写新编号，多槽如 `<默认ID>,<新编号>`（顺序必须与 OBJ 的 `usemtl` 顺序一致）。**不调参的槽一律填本项目核对过的默认材质ID 且不放参数文件**。
3. 把 `<输出目录>/<词>.txt` 复制到 `<游戏包>/BepInEx/plugins/OC2ModelTest/Model/Resources/<资源文件夹>/material.txt`（槽 N 用 `materialN.txt`），重启游戏验证。`<资源文件夹>` 必须与 config 第 11 列完全一致；输出目录不会被游戏读取。

原有编号条目一个字都不动。

## 多材质槽落地

`config.txt` 材质ID 列用逗号分隔，从左到右对应槽 0/1/2…。

- 参数文件按槽位命名：槽 0 `material.txt`、槽 1 `material1.txt`、槽 2 `material2.txt`…。**不需要调参的槽不要放文件**：插件用 `File.Exists` 判断，缺文件就用材质库原样。
- 每个槽各自 `new Material(...)` 克隆，参数不会互串；多个编号指向同一个 `bundle | 材质名` 也合法，靠行号区分编号。
- 模型必须在 Blender 里真的分出对应数量的材质槽，且槽顺序与 OBJ 里 `usemtl` 出现顺序一致。插件教程 Q7：模型没多槽时插件只应用**最后一个**材质，前面的槽全白做。
- **槽顺序以 OBJ 里 `usemtl` 首次出现顺序为准**（解析器用 `List.IndexOf(材质名)`，首次出现才追加 submesh），与 `Test.mtl` 里 `newmtl` 的声明顺序无关。
- 玻璃材质尽量不要放在首位。
- 追加库行时每个新词各占一行，两行内容完全相同也可以。

具体示例见 `references/examples.md`。

## 路径与中文命名规则

插件按 `Path.Combine(插件目录, Model, Resources, 资源文件夹, "material.txt")` 拼路径并 `File.Exists` 判断，文件名是硬编码常量；名字不匹配时整个文件被静默跳过，等于没放。

| 场景 | 能否用中文 | 说明 |
| --- | --- | --- |
| 描述词 / 预设词库 | 可以 | 词库本身就是中文 |
| 输出文件名 `雪.txt` | 可以，但只是暂存名 | 放进资源文件夹必须改名 `material.txt` / `materialN.txt` |
| txt 头部整行注释 | 可以 | `#` 开头整行被跳过，中文与编码都不影响参数 |
| 参数行（key / value） | 不可以 | 参数名须为 `_Xxx` ASCII，值只能是数字或逗号分隔数字 |
| `KEYWORD=` 的值 | 不可以 | 必须是 shader 支持的 ASCII 关键字 |
| config.txt 名称列 | 可以 | 现有配置全是中文，仅用于日志显示 |
| OBJ / MTL 里的材质名 | 可以 | 解析器按字符串处理，无 ASCII 过滤 |
| 资源文件夹名 | 不建议 | 代码直接 `Path.Combine`、无 ASCII 过滤，理论可行，但未在游戏内实测中文路径；优先用英文或拼音 |

文件统一 UTF-8 保存（有无 BOM 均可）；中文注释即使编码有偏差也无影响，因为整行被跳过。
