# 参数映射规则（OC2ModelTest material.txt）

## 一、插件解析器行为（反编译 OC2ModelTest.dll 确认）

`Material` 由 `new Material(库材质)` 克隆得到，随后读取 `Model/Resources/<资源文件夹>/material.txt`（槽 0）或 `materialN.txt`（槽 N），逐行处理：

1. `Trim()`；空行、以 `#` 开头的整行 → 跳过。
2. 以 `KEYWORD=` 开头 → `EnableKeyword(后续内容.Trim())`。不支持的 keyword 静默跳过。
3. 其余按 `=` 切分，**必须恰好 2 段**，否则整行跳过。
4. 值含 `,` → 按逗号切，≥3 段且 `HasProperty(key)` → `SetColor(R,G,B[,A])`，A 缺省 1。
5. 否则 `float.TryParse` 且 `HasProperty(key)` → `SetFloat`。
6. 任何异常都在循环外的 catch 中记日志，**异常会中断该文件后续所有行**。

推论：

- 行内注释、值里多写一个 `=`、拼错属性名、写了 shader 不存在的属性，都不会报错，只会静默失效。
- 未写的参数保留基底材质原值 → 必须输出全量文件。
- `材质设定包/材质设定说明/*.txt` 是**带注释的说明文档**（含行内注释、`_SpecColor = 未知`、括号颜色写法），不可直接放进 Resources。可用模板只有本 skill 的 `assets/template_*.txt`。

## 二、语义维度

每个预设词用下列维度描述，展开时由公式换算成具体参数。未收录词按同样维度现推。

| 维度 | 记号 | 说明 |
| --- | --- | --- |
| 主色 | C | RGB，0～1；OC2 卡通风避免纯黑纯白 |
| 高光色 | H | 反射亮部颜色 |
| 边缘光色 | RC | 轮廓光颜色 |
| 金属度 | M | 0～1，非金属一律 0～0.2 |
| 粗糙度 | R | 0～1，越大越哑光 |
| 亮度 | B | 0～1，整体亮度补偿 |
| 边缘光强度 | I | 0～1 |
| 透明度 | A | 0～1，1 = 不透明；仅玻璃基底使用 |
| 自发光色 | E | 默认 `0,0,0`（黑＝不发光） |

辅助运算：`mix(C, W, t) = C*(1-t) + W*t`，W 为白色 `(1,1,1)`；`C*k` 为逐通道乘 k；所有结果保留 3 位小数。

## 三、通用基底（template_common.txt）展开公式

| 目标参数 | 公式 |
| --- | --- |
| `_Color` | `C, 1` |
| `_node_6281` | `mix(C, W, 0.60), 1` |
| `_node_9884` | `mix(C, W, 0.85), 1` |
| `_node_9905` | `mix(C, W, 0.70), 1` |
| `_MaskColor` | `C*0.45, 1` |
| `_node_918` | `C*0.65, 1` |
| `_highlight_colour` | `H_final, 1`，其中 `H_final = mix(H, RC, 0.5)` |
| `_node_8633` | `H_final*0.90, 1` |
| `_Metallic` | `M` |
| `_Roughness` | `R` |
| `_Glossiness` | `1 - R` |
| `_Brightness` | `B` |
| `_Brightness_Intensity` | `B * 0.8` |
| `_RimIntensity` | `I` |
| `_RimPower` / `_RimPower_copy` | 固定 `0.8` / `0.5` |
| `_EmissionColor` | `E, 1` |
| `_EmissionColour` | 固定 `1,1,1,1` |
| `_PreviewEmission` | `E` 非黑时 `1`，否则模板原值 `0` |
| `KEYWORD` 6 行 | 原样保留：`_DIFFUSEPREVIEW_ON` `_EMISSION` `_METALLICGLOSSMAP` `_NODE_1439_ON` `_PREVIEWAO_ON` `_RIMPREVIEW_ON` |

通用基底**没有独立边缘光颜色参数**，因此先算 `H_final = mix(H, RC, 0.5)`，再由 `_highlight_colour` / `_node_8633` 承担轮廓光色。其余所有参数（渲染模式、法线、AO、UV、内部 `_node_1439/2382/3545` 等）保持模板原值。

## 四、玻璃基底（template_glass.txt）展开公式

| 目标参数 | 公式 |
| --- | --- |
| `_node_3457` | `C, A` |
| `_Colour` | `C*0.85, A*0.8` |
| `_PosterizeColour` | `mix(C, W, 0.25), 1` |
| `_FresnelOutline` | `RC, 1` |
| `_highlight_colour` | `H, 1` |
| `_MaskColor` | 固定中性灰 `0.502,0.502,0.502,1.0` |
| `_node_7161` | `mix(C, (0.083,0.622,0.941), 0.35), 1` |
| `_node_8531` | `mix(C, (0.574,0.647,1.000), 0.35), 1` |
| `_Color` | `C, 1` |
| `_EmissionColor` | `E, 1` |
| `_Metal` | `M` |
| `_Roughness` | `R` |
| `_Gloss` | `clamp(1 - R, 0.20, 0.95)` |
| `_Brightness` | `B` |
| `_Opacity` | `A` |
| `_Cutoff` | 固定 `0.1` |
| `_FresnelOutlinePower` | `I * 0.26` |
| `_FresnelExp` / `_FresnelGlossImpact` / `_FresnelOutlineSize` | 保持模板 `0.78 / 0.337 / 2.93` |
| `_Posterize*`（5 项）、`_Tones`、`_WorldUVMultipllier`、`_WorldUVRotator`、`_ShadowDarkness`、`_Refraction`、`_power`、`_max` | 保持模板原值（OC2 原版卡通风格） |
| 全部 `_node_XXXX` 标量（约 17 项）、`_fresneldark` | **保持模板原值，禁止改动**：ShaderForge 生成，含义未知 |

玻璃基底模板**没有 KEYWORD 行**，不要生成。

玻璃基底有两个必须显式处理的模板原值（否则暖色液体会串色）：

| 参数 | 模板原值 | 处理 |
| --- | --- | --- |
| `_EmissionColor` | `0,1,0,1`（**绿色自发光**） | 除绿色发光词外一律显式写 `0,0,0,1`，漏写会让蜂蜜发绿光 |
| `_node_7161` / `_node_8531` / `_fresneldark` | 亮蓝 / 淡紫蓝 / 蓝 | 冷色词按上表 mix 公式；**暖色液体词**按 `presets.md` 的「暖色液体覆盖表」改成暖色，否则透光部分发灰发蓝 |

玻璃基底参数在 `config.txt` 里尽量不要放首位（教程 Q7 / 2026-11-08 更新说明）；放槽 1 及以后没问题。

## 五、数值规范

- 颜色：`0.920,0.950,1.000,1` 这种 3 位小数；A 可写 `1.0` 或 `1`。
- 标量：2 位小数（模板原值除外，保持其原有精度）。
- 允许负数的模板原值（如 `_node_372=-2.67`、`_max=-0.17`）照抄，不要把新写的值 clamp 到 0～1 之外。
- 文件以 UTF-8 保存，LF/CRLF 均可。

## 六、零反光 / 极哑光覆盖（matte）

**概念**：雪之所以白，是因为**漫反射**极强；「完全不反射光」的物体是纯黑的。游戏里让人觉得「反光」的是**镜面高光 + 环境反射 + 轮廓光**这三条方向性反射通道。要的是「关镜面、留漫反射」，不是把亮度调黑。

适用词列在 `presets.md` 的「极哑光覆盖表」；用户反馈「反光 / 太亮 / 发塑料感」时把该词加进表里，不改颜色节点（高光被关掉后高光色自然不再可见，改颜色只会让主体变灰）。

在第三节展开结果之上做**覆盖**：

| 参数 | 覆盖值 | 作用 |
| --- | --- | --- |
| `_Roughness` | `0.98` | 粗糙度拉满，光滑度归零 |
| `_Glossiness` | `0.02` | 与 R 配套（模板里与 R 不联动，必须同时写） |
| `_GlossMapScale` | `0` | 光泽贴图不贡献 |
| `_SpecularHighlights` | `0` | 关镜面高光 |
| `_GlossyReflections` | `0` | 关环境 / 反射探针 |
| `_RimIntensity` | `0.00` | 关轮廓光（这是反光最显眼的一路） |
| `_RimPreview` | `0` | 关轮廓光预览 |
| `_Metallic` | `0` | 保持非金属 |
| `KEYWORD` | 模板 6 行**全部保留**，末尾追加 `_SPECULARHIGHLIGHTS_OFF`、`_GLOSSYREFLECTIONS_OFF` | Unity 编译期关闭高光 / 反射变体 |

注意：

- 插件只有 `EnableKeyword`、没有 `DisableKeyword`。基底克隆后自带的 `_RIMPREVIEW_ON` **删掉也没用**，必须靠 `_RimIntensity=0` / `_RimPreview=0` 压住；同理「关闭」只能靠 Enable 这两个 `*_OFF` 变体。
- 两个 `*_OFF` 若 shader 没有对应变体会被静默忽略，无害；主要生效路径是上面 6 个 float。
- 游戏内置材质里 `_SpecularHighlights` / `_GlossyReflections` 全为 1、`_RimIntensity` 为 0.5～2（食材箱甚至 2），即**基底天生带高光**，不主动关就一定会反光。这是「雪有点反光」的根因。
- 若关完仍有亮边，剩下两个可能：`_highlight_colour`（靠近交互高亮，可压到 `0.600,0.630,0.680`）或基底 shader 本身太亮，此时考虑把该编号的库行换成更哑的 `bundle39 | mat_sk_crate_01`。

## 七、常见坑

| 现象 | 原因 |
| --- | --- |
| 模型纯白 | 材质ID 超出 `materialLibrary.txt` 行数，或库行未追加 |
| 模型发红/串色 | 只写了差异行，残留灭火器基底暖红节点 |
| 参数完全不生效 | 行内注释、属性名拼错、写到了另一套基底的参数 |
| 改了 A 却没变透明 | 通用基底 `_Mode` 为 0（Opaque），透明效果应改用玻璃基底 |
| 玻璃材质在多材质槽里异常 | 教程提示玻璃材质尽量不要放在材质栏首位 |
| 改 A 物体结果 B 也变 | 不会：插件每次 `new Material(...)` 克隆独立实例；但追加库行时仍要给独立编号 |
| 雪 / 布 / 纸这类哑光物仍反光 | 只调了 `_Roughness` 不够，`_SpecularHighlights` / `_GlossyReflections` / `_RimIntensity` 三个开关仍是模板原值 1 / 1 / 0.5 → 走第六节 matte 覆盖 |
