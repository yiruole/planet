---
name: blender-effect-builder
description: 在 Blender 中搭建视觉效果(Geometry Nodes 程序化/材质/灯光/摄像机/场景渲染/实拍+CG 混合)。接收 reference-reverse-engineer 路由或直接的 Blender 需求,通过 blender MCP 或 socket 桥执行:规划→构建→调参→渲帧验证→迭代。触发词:用 Blender 做/复刻、Geometry Nodes、GN、Blender 材质/渲染。
---

# Blender Effect Builder v0.1

前置:遵守 `~/.claude/skills/creative-rules/`。基于水环案例(NeXus Follow Curve 复刻)实测提炼。本机 Blender 5.1.2。

## 0. 连接方式(三条通道)

0. **无头脚本循环**(Blender 未运行/批量迭代首选,已两次实测):把建场景+渲染写成一个 `build_x.py`,`blender -b --python build_x.py -- <outdir>` 一条命令完成"改脚本→重建→渲帧"整轮迭代,完全可 git 管理。注意:无头下部分 bpy.ops 缺 context(如 shade_smooth),用数据 API 替代(逐 polygon `use_smooth=True`)

1. **blender MCP**(`mcp__blender__*`,uvx blender-mcp,user scope 已注册)——新会话可用
2. **Socket 直连**(MCP 未加载时的后备,已实测):Blender 插件 `blender_mcp_addon.py`(已装,监听 `localhost:9876`),协议 `JSON {"type": "execute_code", "params": {"code": "..."}}`,一次 socket 连接一条命令,读到完整 JSON 为止

连接排查:`nc -z localhost 9876` → 失败则让用户在 Blender N 面板 BlenderMCP 里点 Connect(插件已启用时端口自动开)。

## 1. 视觉特征 → Blender 技术路线(实测)

| 特征 | 路线 |
|---|---|
| 粒子/液体沿曲线流动+融合表面 | GN:Points + Sample Curve(factor=fract(index/N+time×speed))+ Points to Volume → Volume to Mesh。**无需模拟,纯程序化可循环** |
| 表面外观(水/玻璃/金属/SSS) | Shader:Principled 一层解决为主;水=transmission 1.0 + rough 0.03 + IOR 1.33 |
| 发光/颗粒/暗角/辉光 | Compositor(v0.1 未实测,标记 thin)或 Eevee bloom |
| 场景组装/摄像机/打光/最终渲染 | Blender 主场:object 层直接 Python API 摆放 |
| 实拍+CG 混合 | Blender(motion tracking + compositing)——未实测,待案例 |

**GN vs Shader vs Compositor 选择逻辑**:动"形"用 GN,动"面"用 Shader,动"全画面"用 Compositor。能在 GN 里用 Scene Time 驱动的动画,不要 keyframe(可循环、可调速、无烘焙)。

## 2. 构建纪律(与 Houdini 不同点)

- Blender 无 dry_run 类工具:**每步小验证**——建完 node group 立即用 depsgraph evaluate 数 verts;渲一帧看图再继续
- **按类型找节点,不按名字**:`n.type=='BSDF_PRINCIPLED'`——默认节点名随版本/语言变,按名字查会 None
- **5.1 API 迁移**:不少节点属性变成了 MENU 输入 socket(如 Points to Volume 的 Resolution Mode,设法:`node.inputs['Resolution Mode'].default_value='Size'`);属性设置失败时先 introspect:列出 `n.inputs` 和 bl_rna.properties 再动手
- 摆相机/灯用 look-at 矩阵(z=pos-target 归一,x=up×z,y=z×x → extractRotates 等价的 Matrix→euler)
- 工程文件保存用绝对路径 `bpy.ops.wm.save_as_mainfile(filepath=...)`

## 3. 参数启发式(水环实测值,同类效果起点)

**GN 液体环**(单位:环半径 2.0 的场景)
- 点数 1400 起步,平滑需要时加到 2600;截面散布 ±0.11;点半径 random 0.07–0.11
- Points to Volume voxel 0.055 草稿 / 0.04 成品;再小显著变慢
- 表面波动:4D Noise scale 1.6–2.2,振幅 0.32–0.5(W=frame×0.06 驱动流动感)
- 流速 0.004/帧 ≈ 250 帧一整圈无缝循环
- 粗细起伏:低频 Noise(scale 0.55)→ Map Range 0.55–1.5 乘到半径

**夜景/暗调场景**
- ⚠️ AgX 色彩变换会把低值压黑:想在成片里读出"深蓝夜空",世界/材质数值要比直觉亮 3–5 倍;渲完必须看图,别信数值
- 渲染端补救太贵时可在合成端做亮度遮罩提升(暗部+画面上部 → 加深蓝),先加(lift)后乘,乘法分级救不了近 0 值

**水/透明材质(Eevee)**
- ⚠️ **透明材质在暗环境里 = 隐形/像黑岩石**(实测教训):world 至少 (0.12,0.15,0.18)×1.2,或给强反射对象;先调环境再怀疑材质
- 必开:`scene.eevee.use_raytracing=True` + `mat.use_raytrace_refraction=True`(5.1 属性名,老版本叫 use_screen_refraction,hasattr 探测)
- 三灯:暖 key(强)+ 冷 rim + 弱 fill;反光地板给透明体提供形状线索

**渲染**:Eevee 960×540 单帧秒级~分钟级,迭代用它;Cycles 只在需要真 GI/SSS 质量时上

## 4. MVP 与迭代

首版 = 静帧 + 灰模/基础材质,确认形态;第二版加材质灯光;动画验证渲 2–3 个错开的帧(如 f60/f140)确认运动连续。每轮 ≤3 个变量。

## 5. 失败修正表(全部实测)

| 症状 | 原因 | 修法 |
|---|---|---|
| `'NoneType' has no attribute 'inputs'` | 按名字找节点失败 | 按 `n.type` 遍历查找 |
| `object has no attribute 'resolution_mode'` | 5.1 属性迁移为 menu socket | introspect inputs,用 `inputs['...'].default_value='...'` |
| 透明材质渲成黑色岩石 | 环境太暗+未开光追折射 | 提亮 world;开 eevee raytracing + 材质折射开关 |
| 表面碎块状不连贯 | 点太少/散布太大/voxel 太粗 | 点数↑、散布↓、voxel↓ 三管齐下 |
| socket 桥无响应 | Blender 端服务未启动 | N 面板 BlenderMCP → Connect;检查 9876 端口 |
| MCP 工具不存在 | 服务器注册后未重启会话 | 用 socket 直连,或新开会话 |

## 6. 边界:什么时候不用 Blender

- 真流体模拟(FLIP/碰撞飞溅)、大规模破碎、pyro → **Houdini**(Mantaflow 可用但可控性差)
- 复杂逐元素程序化逻辑(深嵌套循环/群体个性化)→ **Houdini Python SOP**(GN 表达嵌套时序很痛苦,牡丹案例即此判断)
- 实时交互/audio-reactive/feedback 流 → **TouchDesigner**
- Blender 赢面:快速程序化小品(GN 20 节点级)、场景+摄像机+渲染一体、实拍混合、免费管线

## 7. 案例库

- **水环**(完整闭环):`~/Desktop/Digital Art/blender/waterring/water_ring_nexus_style.blend`,GN 节点组 `WaterRingGN`,复刻自 NeXus Follow Curve 教程效果
