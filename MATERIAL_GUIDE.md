# OC2 材质生成完整规则（平台无关）

本文件是 `oc2-material-writer` 的核心文档，**不依赖任何特定 AI 工具**：WorkBuddy、dsh、Claude、豆包、DeepSeek，只要能读取本地文件，按本文执行即可得到同样结果。若所用工具不能读取本地文件，改用 `PROMPT.md`（自包含，规则与模板全文都在里面）。

配套资料：`references/parameter-map.md`（参数展开公式与坑）、`references/presets.md`（预设词库）、`assets/template_common.txt` / `assets/template_glass.txt`（纯净全量模板）、`references/examples.md`（多材质槽示例）。

---

## 一、适用前提

1. 已安装 Overcooked! 2，且已安装 **OC2ModelTest 模型替换插件**。本包只产出该插件读取的 `material.txt` 参数文件，不提供模型、贴图或 DLL。
2. 模型在 Blender 里确实分出了对应数量的材质槽，且槽顺序与 OBJ 里 `usemtl` **首次出现顺序**一致（与 `Test.mtl` 里 `newmtl` 的声明顺序无关）。模型没多槽时插件只应用最后一个材质。
3. 使用者能提供本项目 `materialLibrary.txt` 的绝对路径。

---

## 二、开始前必须问使用者的四件事

**没拿到之前不要猜路径、不要假设编号、不要沿用任何示例里的编号。**

1. `materialLibrary.txt` 的绝对路径（通常在 `<游戏包>/BepInEx/plugins/OC2ModelTest/Model/materialLibrary.txt`）。
2. 输出目录绝对路径（放生成 txt 的地方，游戏不会读它）。
3. `config.txt` 里目标物体的资源文件夹名、材质槽数量、要改第几槽。
4. 该项目的**默认材质ID**：库里 `bundle39 | mat_sk_crate_01` 的索引；库里没有这一行则请使用者指定。

Steam 库位置与插件目录名因人而异，**不要做路径自动探测**。工作区里若存在插件的原版参考副本，只用来看模板 / 教程 / 说明文档，禁止拿它算编号或当作落地目标。

---

## 三、核对库并分配编号（每次生成前必做）

编号 = 本项目 `materialLibrary.txt` 中**非注释非空行**的序号，从 0 起。这是唯一权威来源。

### 有 Python 时

```bash
python scripts/check_library.py "<本项目 materialLibrary.txt>" --registry registry.json
python scripts/check_library.py "<本项目 materialLibrary.txt>" --json
```

脚本打印全部有效行、行数、下一个空号、内容 sha256 指纹，并检查默认材质ID 是否越界、每个已登记词的 id 是否真的对应它的基底行。退出码 0 = 一致 / 仅查询，1 = 发现不一致，2 = 用法或文件错误。

状态处理：

| 状态 | 处理 |
| --- | --- |
| `PASS` | 登记可复用；新词编号 = `next_id`（有效行数） |
| `NEW_PROJECT` | 库路径没有档案：**所有编号按本次库内容重新分配**，禁止复用其它项目编号 |
| `PROJECT_SWITCH` | 已载入该库档案，用档案里的 `entries` 与默认材质ID |
| `FINGERPRINT_CHANGED` | 库被改过，逐词重新核对，一律以库内容为准 |
| `MISMATCH` / `OUT_OF_RANGE` | 按 `base_line` 在库中的实际索引重算；库里没有则追加，编号 = 有效行数 |
| `DEFAULT_INVALID` | 默认材质ID 越界或指向别的材质 → 重新指定 |
| `NO_FINGERPRINT` | 核对通过后把本次 `line_count` / `sha256` 写入登记表 |

### 没有 Python 时（手工核对，AI 可直接照做）

1. 打开使用者的 `materialLibrary.txt`，逐行读取。
2. 丢掉空行与 `#` 开头的整行；剩下的**按原顺序从 0 编号**，逐行列出 `索引  内容`。
3. 记下总行数 `N`。**下一个空号 = N**。
4. 在这份列表里找 `bundle39 | mat_sk_crate_01` 的索引，作为默认材质ID；找不到就问使用者要一个。同时确认该索引 `< N`。
5. 若存在 `registry.json`，逐个检查 `entries`：登记的 `id` 那一行内容是否等于 `base_line`。不等 → 按 `base_line` 在列表里的实际索引重算；列表里没有 → 该词需要追加新行，编号 = N。
6. 若库内容与上次记录（行数或任意一行文本）不同 → **全部重算**，不复用旧编号。
7. 新词编号 = N；即使库里已有内容完全相同的行，也为该词单独追加一行（一词一号）。
8. 把本次 `N` 与各行列出的结果写回 `registry.json`（没有就从 `registry.example.json` 复制一份）。

> 最关键的一条：**编号绝不跨项目复用**。同一个词「雪」在 A 项目是 9，在 B 项目可能压根不存在，也可能对应完全不同的行。

---

## 四、选基底

| 条件 | 基底 | 追加到库的那一行 |
| --- | --- | --- |
| 不透明词（默认） | 通用 / Standard 系 | `bundle46 \| mat_sk_fire_extinguisher_01` |
| 透明类词：冰、玻璃、水、水晶、蜂蜜、糖浆、果汁、液、透明、气泡、果冻、树脂、琥珀、夜光 | 玻璃 / ShaderForge 系 | `bundle166 \| mat_dlc2_smoothiemaker_glass_02` |

两套基底参数几乎不重叠，禁止混写。`HasProperty` 为假的参数会被静默忽略，把 `_Metallic` 写进玻璃基底等于白写。玻璃材质尽量不要放在多材质配置的首位。

---

## 五、展开全量参数文件

1. 读 `assets/template_common.txt`（53 行，含 6 条 KEYWORD）或 `assets/template_glass.txt`（51 行，无 KEYWORD）。这是**纯净模板，没有注释**。
2. 把描述词归一化成一个词（去掉「材质」「生成」「写一个」等填充词），在 `references/presets.md` 查语义维度；未命中则按 `references/parameter-map.md` 的公式现推，并列出所做假设。
3. 按 `parameter-map.md` 的展开公式**覆盖**模板中对应项；未涉及的标量、内部节点参数一律保持模板原值；`KEYWORD` 行原样保留在末尾。
4. 极哑光词（见 `presets.md` 覆盖表）额外套用第六节零反光覆盖 + 追加 `_SPECULARHIGHLIGHTS_OFF` / `_GLOSSYREFLECTIONS_OFF`。
5. 暖色透明液体词（蜂蜜 / 糖浆 / 果汁）额外套用「暖色液体覆盖表」，并强制 `_EmissionColor=0,0,0,1`（模板原值是绿色自发光）。
6. 头部写 5～6 行整行注释（词 / 本次编号 / 基底 / 落地提示 / 生成标识），**正文零行内注释**。
7. 输出到 `<输出目录>/<词>.txt`，同名覆盖。

### 为什么必须全量

解析是覆盖式的，没写的参数保留基底材质原值。通用基底来自灭火器材质，带一堆暖红节点（`_MaskColor` 暗红、`_highlight_colour` 暖红、`_node_8633` 橙、`_node_9884` 奶油）；玻璃基底 `_EmissionColor` 原值是 `0,1,0,1` 绿色自发光，`_node_7161` / `_node_8531` / `_fresneldark` 全是蓝调。只改 `_Color` 的「雪」会是粉红雪，漏写 `_EmissionColor` 的「蜂蜜」会发绿光。

### 零反光 / 极哑光覆盖

雪之所以白，是因为**漫反射**极强；「完全不反射光」的物体是纯黑的。游戏里让人觉得「反光」的是镜面高光、环境反射、轮廓光三条方向性通道。要的是「关镜面、留漫反射」，不是把亮度调黑。

| 参数 | 覆盖值 | 作用 |
| --- | --- | --- |
| `_Roughness` | `0.98` | 粗糙度拉满 |
| `_Glossiness` | `0.02` | 与 R 配套（模板里与 R 不联动，必须同时写） |
| `_GlossMapScale` | `0` | 光泽贴图不贡献 |
| `_SpecularHighlights` | `0` | 关镜面高光 |
| `_GlossyReflections` | `0` | 关环境 / 反射探针 |
| `_RimIntensity` | `0.00` | 关轮廓光（最显眼的一路） |
| `_RimPreview` | `0` | 关轮廓光预览 |
| `_Metallic` | `0` | 保持非金属 |
| `KEYWORD` | 模板 6 行全保留，末尾追加两个 `*_OFF` | 编译期关闭高光 / 反射变体 |

插件只有 `EnableKeyword`、没有 `DisableKeyword`，基底克隆自带的 `_RIMPREVIEW_ON` 删掉也没用，必须靠 `_RimIntensity=0` / `_RimPreview=0` 压住。颜色节点不要改：高光被关掉后高光色自然不可见，改颜色只会让主体变灰。

---

## 六、自检清单

生成后逐项检查（有 Python 时跑 `scripts/validate_material.py <文件> common|glass`）：

- 每行恰好一个 `=`；没有行内注释（`#` 只能独占一行且位于行首）。
- 参数名必须以 `_` 开头，且**全部来自对应基底模板**；不能发明新参数名。
- 颜色值是 3 或 4 段数字，每段 0～1；标量是数字。
- 模板里的每一项参数都出现了（全量，不能只写差异行）。
- 通用基底保留模板自带 6 条 `KEYWORD`（极哑光词可多 2 条）；玻璃基底**不应有** `KEYWORD` 行。
- 头部注释写明词、本次核对得到的编号、基底。
- 文件 UTF-8 保存。

常见故障：模型纯白 → 材质ID 越界或库行未追加；模型发红 → 只写了差异行；参数完全不生效 → 行内注释 / 属性名拼错 / 写到了另一套基底；改了 A 却没变透明 → 通用基底 `_Mode` 是 Opaque，透明要换玻璃基底。

---

## 七、落地三步

1. 在**本项目** `materialLibrary.txt` 末尾追加该词的基底行；追加后的索引 = 第三节核对得到的编号。
2. 把同目录 `config.txt` 里目标物体那行的材质ID 列改成对应编号：单槽写新编号，多槽写 `<默认ID>,<新编号>`，顺序必须与 OBJ 的 `usemtl` 顺序一致。**不调参的槽填默认材质ID 且不放参数文件**。
3. 把 `<输出目录>/<词>.txt` 复制到 `<游戏包>/BepInEx/plugins/OC2ModelTest/Model/Resources/<资源文件夹>/material.txt`（槽 N 用 `materialN.txt`），重启游戏验证。`<资源文件夹>` 必须与 config 第 11 列完全一致；输出目录不会被游戏读取。

落地前先备份 `config.txt` 与 `materialLibrary.txt`。原有编号条目一个字都不动。

### 中文命名边界

| 场景 | 能否用中文 |
| --- | --- |
| 描述词 / 预设词库 / txt 头部整行注释 | 可以 |
| 输出文件名 `雪.txt` | 可以，但只是暂存名，放进资源文件夹必须改名 `material.txt` / `materialN.txt` |
| 参数行 key / value、`KEYWORD=` 的值 | 不可以，必须 ASCII |
| `config.txt` 名称列、OBJ / MTL 里的材质名 | 可以（解析器按字符串处理） |
| 资源文件夹名 | 不建议，未在游戏内实测中文路径 |

---

## 八、模板来源

`assets/template_*.txt` 的参数取值整理自 OC2ModelTest 插件随附的「材质设定包」纯净模板；`references/parameter-map.md` 记录的是依据插件行为整理的解析规则与展开经验。游戏素材与插件本身的权利归原权利人，本仓库的 MIT 许可只覆盖自写的文档、词库与脚本。模板仅供 MOD 调参使用。
