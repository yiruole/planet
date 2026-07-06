---
name: touchdesigner-effect-builder
description: 在 TouchDesigner 中搭建实时视觉效果(feedback/displace/glitch/audio-reactive/GLSL/生成式动画/实时交互)。接收 reference-reverse-engineer 路由或直接的 TD 需求,通过 touchdesigner MCP 执行:规划 OP 网络→构建→调参→截图验证→迭代。触发词:用 TD/TouchDesigner 做、实时效果、audio reactive、feedback、glitch。
---

# TouchDesigner Effect Builder v0.1

前置:遵守 `~/.claude/skills/creative-rules/`。基于魔方全息项目(NewProject.19)与 liquid chrome 案例实测提炼。本机 TD 2025.31550。

## 0. 连接方式

1. **touchdesigner MCP**(已注册,`mcp__touchdesigner__td_*`:td_health/td_connect/td_create_op/td_set_par/td_eval/td_exec 等)——先 `td_health` 检查
2. **HTTP 后备**(MCP 连不上时,已实测):`POST localhost:9980/mcp`,**JSON 里不能有裸换行**(代码要 `\n` 转义)
3. TD 端需要 bridge 组件在工程里运行;bridge 实体在 `Digital Art old/universe drive/touchdesigner-mcp/`(**不可移动**)

## 1. TOP / CHOP / SOP / COMP 路线判断

| 需求 | 家族 | 依据 |
|---|---|---|
| 像素级效果(调色/glitch/扫描线/晕影/合成) | TOP,复杂逻辑直接写 GLSL TOP | 魔方:背景/扫描栏/全息 grade 全是 GLSL TOP |
| 时间驱动/随机触发/参数动画 | CHOP(Noise CHOP + 表达式引用) | 魔方:相机抽搐/glitch/字幕闪现全靠 sparse Noise CHOP |
| 3D 几何/实例化 | SOP + GLSL MAT(几何逻辑重的考虑让路 Houdini) | 魔方 27 cubie 用 vertex shader 按 `gl_VertexID/顶点数` 识别,别用位置(变换后坐标乱) |
| 网络组织/复用 | COMP;渲染链 Render TOP → 后处理 TOP 串 → 输出 | — |

**GLSL 优先原则**:3 个以上原生 TOP 串联能被 1 个 pixel shader 替代时,写 GLSL(可控、快、参数集中)。CHOP 负责"何时/多少",TOP/GLSL 负责"什么样"。

## 2. 效果使用边界(避免画面脏的核心)

- **bloom**:`maxRadius < 0.1`(实测 1.0 会把任何形状糊成圆);bloom 只点缀高光——先关 bloom 调对光比和对比度,最后再开
- **noise**:每层噪波必须说得出负责的尺度(背景颗粒/几何抖动/时间触发是三件事,别用一个 noise 全包);sparse 型用于"偶发事件",hermite 用于连续漂移
- **feedback**:衰减 <0.97,否则画面积累发白;feedback 内容要有运动才有意义
- **材质单一**→ 用亮度→色相映射(gradient grade)加层次:魔方案例的 hologram_grade 就是亮度分 5 档映射不同色温
- **画面脏**→ 检查:黑位是否压住(背景别用纯灰)、发光元素数量(≤3 个视觉焦点)、glitch 频率(偶发才有效,常驻就是噪音)

## 3. 参数启发式(魔方项目实测)

- 相机轨道:0.3 rad/s 是"缓慢观察"量级;抽搐 ±1.2 单位、sparse noise 驱动
- 偶发事件频率:0.8s 换一次 + 15% 概率 ≈ "病理感";更高频率变成杂乱
- 半透明几何:`srcblend='sa', destblend='omsa', depthwriting=False` 三件套,缺一渲染错
- 穿入几何内部:`near clip 0.02` + MAT `cullface='neither'`
- Text TOP:必须 `outputresolution='custom'` 显式设分辨率 + `fontsizexunit='pixels'`(points 单位小到不可见);叠字幕用 Composite **add** 模式(不依赖 alpha)
- Composite 'over':**Input 0 = 前景,Input 1 = 背景**(反了就是黑屏或只见背景)

## 4. MVP 与迭代

首版:静态网络 + 单一运动源,截图确认构图;逐个开启效果层(每次 1 层),每层截图对比;audio-reactive 最后接(先用 LFO/Noise 模拟驱动信号调好视觉,再换真音频)。

## 5. 失败修正表(全部实测)

| 症状 | 原因 | 修法 |
|---|---|---|
| 形状全部变圆/糊 | bloom maxRadius 过大 | 降到 <0.1 |
| 录制的 mov 是空的/1帧 | `record=True` toggle 不写帧 | 每帧 `par.addframe.pulse()`,循环 N 次 |
| GLSL TOP 里时间不动 | GLSL TOP 无 TDTime uniform | 自建 uniform,`me.time.seconds` 经 vec 传入 |
| 文字看不见 | Text TOP 默认分辨率/points 字号 | custom 分辨率 + pixels 单位字号;add 模式合成 |
| 透明物体渲染成实心/黑块 | blend/depth 设置不全 | sa/omsa/depthwriting=False 三件套 |
| 逐元素识别错乱 | 用位置判断元素 | 用 `gl_VertexID / 每元素顶点数` |
| render 背景参数无效 | 参数名记错 | 是 `par.bgcolora`(不是 bgcoloralpha) |
| bridge JSON 报错 | 代码含裸换行 | 全部 `\n` 转义后再发 |

## 6. 边界:什么时候不用 TD

- 高质量离线渲染(SSS/GI/微距 DOF)→ **Houdini/Blender**(TD 是实时管线,画质天花板低)
- 重几何程序化(生长/破碎/大量个性化元素)→ **Houdini**
- 场景/摄像机/实拍混合的"电影帧" → **Blender**
- 精细合成/roto/tracking → **AE**
- TD 赢面:实时反馈回路、音频驱动、交互输入、长时间运行的生成系统、现场演出

## 7. 案例库

- **魔方全息**(完整闭环,含 30s 录制):工程与 GLSL 源码记录在 git 历史 `Desktop/TD/PROGRESS.md`(文件已删但 `git show eef4e80:Desktop/TD/PROGRESS.md` 可取);录制成品 rubik_hologram_30s.mov
- **liquid chrome**:`~/Desktop/Digital Art/TD/transball/liquid_chrome.toe`(REGEN.Prod 复刻)
