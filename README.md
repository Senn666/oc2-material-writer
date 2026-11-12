# oc2-material-writer

给 **Overcooked! 2 / OC2ModelTest 模型替换插件** 用的材质文件生成资料包：丢一个描述词（「雪」「冰」「金属」「透明蜂蜜」），产出该插件可直接读取的 `material.txt` **全量参数文件**，外加一个 `materialLibrary.txt` 新编号和落地清单。

**跨平台**：WorkBuddy / CodeBuddy、dsh、Claude、豆包、DeepSeek 都能用。核心规则与模板是纯文本，不依赖任何特定 AI 工具；Python 脚本只是可选加速，没有也能手工完成。

> 不确定走哪条路 → 先看 [`START_HERE.md`](START_HERE.md)。

---

## 适用前提

1. 已安装 Overcooked! 2 与 **OC2ModelTest 模型替换插件**。本包只产出插件读取的参数文件，不提供模型、贴图或 DLL。
2. 模型在 Blender 里确实分出了对应数量的材质槽，槽顺序与 OBJ 里 `usemtl` **首次出现顺序**一致（与 `Test.mtl` 里 `newmtl` 的声明顺序无关）。
3. 你知道本项目 `materialLibrary.txt` 在哪。

## 三种用法

| 工具 | 用法 |
| --- | --- |
| WorkBuddy / CodeBuddy | 整个目录放进 `<工作区>/.workbuddy/skills/oc2-material-writer/`（或用户级 `~/.workbuddy/skills/`）。`SKILL.md` 自动触发，直接说材质词即可。 |
| 能读本地文件的 AI（dsh / Claude Code 等） | 开场让 AI 读 `MATERIAL_GUIDE.md`，按其中流程执行；需要查表时再让它读 `references/` 与 `assets/`。 |
| 纯对话 AI（豆包 / DeepSeek 网页版等） | 把 `PROMPT.md` **全文复制粘贴**进对话框即可。它自包含了规则、预设词库和两份模板全文，不需要上传任何文件。 |

Release 里的 `oc2-material-writer.zip` 是整个目录的压缩包，既能解压成 skill，也能直接转发给别人——**不访问 GitHub 也能用**。

## 首次使用

把 `registry.example.json` 复制成 `registry.json`（本机私有数据，别提交），然后按 AI 的提问提供四项：

1. `materialLibrary.txt` 绝对路径。
2. 输出目录绝对路径（游戏不会读它）。
3. `config.txt` 里目标物体的资源文件夹名、材质槽数量、要改第几槽。
4. 本项目默认材质ID：库里 `bundle39 | mat_sk_crate_01` 的索引；没有这一行就自己指定。

**编号绝不跨项目复用**：编号 = 该库非注释非空行的序号，从 0 起，每次生成前现算。同一个词在 A 项目是 9，在 B 项目可能不存在或对应完全不同的行。本包不含任何可直接照抄的编号，`references/examples.md` 里的编号只是示意。

## 输出长什么样

`material.txt` = 5～6 行头部整行注释 + 全量参数正文（通用基底 53 行 / 玻璃基底 51 行）。

```text
# OC2 材质：雪
# 材质ID: <本次核对得到的编号>（新编号，需追加到 materialLibrary.txt）
# 基底: bundle46 | mat_sk_fire_extinguisher_01（通用 / 不透明）
# 落地: ① 库末尾追加上面基底行 ② config 对应行材质ID 改成本次编号 ③ 本文件复制到 Model/Resources/<资源文件夹>/material.txt
# 生成: oc2-material-writer | OC2 原版卡通风
_Metallic=0.00
_Roughness=0.98
...
```

三条最容易踩的坑（详见 `MATERIAL_GUIDE.md`）：

- **禁止行内注释**：解析器不剥离 `#` 之后的内容，`_Metallic=0.2  # 哑光` 会让整行失效甚至中断后续所有行。
- **必须全量**：解析是覆盖式的，没写的参数保留基底原值；通用基底来自灭火器材质、带暖红节点，只改 `_Color` 的「雪」会是粉红雪；玻璃基底 `_EmissionColor` 原值是绿色自发光，漏写的「蜂蜜」会发绿光。
- **只写模板已有的参数名**：写错的属性名被 `HasProperty` 静默忽略；两套基底的参数集几乎不重叠。

## 落地三步

1. 在本项目 `materialLibrary.txt` 末尾追加该词基底行；追加后的索引 = 本次核对的编号。
2. `config.txt` 目标物体那行材质ID 改成对应编号：单槽写新编号，多槽写 `<默认ID>,<新编号>`，顺序必须与 OBJ `usemtl` 一致。**不调参的槽填默认材质ID 且不放参数文件**。
3. 把生成的 txt 复制到 `<游戏包>/BepInEx/plugins/OC2ModelTest/Model/Resources/<资源文件夹>/material.txt`（槽 N 用 `materialN.txt`），重启游戏验证。资源文件夹名必须与 config 第 11 列完全一致。

**落地前先备份** `config.txt` 与 `materialLibrary.txt`。本包默认不替你改任何插件文件。

## 目录结构

```text
oc2-material-writer/
├─ START_HERE.md          按 AI 工具选入口
├─ README.md              本文件
├─ PROMPT.md              自包含提示词（纯对话 AI 用，内嵌两份模板全文）
├─ MATERIAL_GUIDE.md      平台无关完整规则（含无 Python 的手工核对步骤）
├─ SKILL.md               WorkBuddy / CodeBuddy 入口
├─ SYNC.md                维护说明：哪些内容属于通用规则、哪些不能带进发行版
├─ assets/
│   ├─ template_common.txt   通用基底纯净全量模板（53 行）
│   └─ template_glass.txt    玻璃基底纯净全量模板（51 行）
├─ references/
│   ├─ presets.md            预设词库 + 极哑光覆盖表 + 暖色液体覆盖表
│   ├─ parameter-map.md      解析规则、展开公式、零反光覆盖、坑清单
│   └─ examples.md          多材质槽示例（编号禁止照抄）
├─ scripts/               【可选】需要 Python 3
│   ├─ check_library.py      读真实库、算指纹、核对编号与默认材质ID
│   └─ validate_material.py  校验产物语法与全量完整性
├─ registry.example.json  空登记表模板
└─ dist/                  本地打包生成的 zip（不入库）
```

## 可选脚本

```bash
python scripts/check_library.py "<本项目 materialLibrary.txt>" --registry registry.json
python scripts/check_library.py "<本项目 materialLibrary.txt>" --json
python scripts/validate_material.py "<输出文件>" common   # 玻璃基底用 glass
```

`check_library.py` 打印全部有效行、行数、下一个空号、sha256 指纹，并检查默认材质ID 是否越界、每个登记词的 id 是否真对应它的基底行；识别 `NEW_PROJECT` / `PROJECT_SWITCH` / `FINGERPRINT_CHANGED` / `MISMATCH` 等状态。`validate_material.py` 检查行内注释、单等号、参数白名单、全量完整性、KEYWORD 合法性。

**没有 Python 也能用**：`MATERIAL_GUIDE.md` 第三节写了逐步手工核对法，`PROMPT.md` 第 2 节同样内嵌了这套步骤。

## 贡献

最欢迎的补充：在 `references/presets.md` 里加新材质词（填满 11 个字段）、补充「极哑光覆盖表」或「暖色液体覆盖表」的新词、以及反馈某个材质在游戏里的实际效果。改了词库后请同步更新 `PROMPT.md` 的附录 A（它是预设词库的全文副本）。

规则来源与本机版同步策略见 [`SYNC.md`](SYNC.md)。

## 许可与来源

- 本仓库自写的文档、词库、脚本采用 **MIT**，见 [`LICENSE`](LICENSE)。
- `assets/template_*.txt` 的参数取值整理自 OC2ModelTest 插件随附的「材质设定包」纯净模板；`references/parameter-map.md` 记录的是依据插件行为整理的解析规则与展开经验。
- **游戏素材与 OC2ModelTest 插件本身的权利归原权利人**，MIT 许可不覆盖它们。模板仅供 MOD 调参使用，请勿将游戏原始资源打包分发。
