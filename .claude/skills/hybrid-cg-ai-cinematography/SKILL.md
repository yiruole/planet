---
name: hybrid-cg-ai-cinematography
description: Blender→AI→合成 的电影镜头管线:Blender 负责空间真值/机位/光照/控制通道,AI 负责表面丰富度(不可用时出完整 handoff package),合成端负责整合与光学质感。触发词:CG+AI 镜头、control passes、AI 视频交接、handoff、hybrid 电影镜头。
---

# Hybrid CG-AI Cinematography v0.1

前置:遵守 `~/.claude/skills/creative-rules/`。基于 Phase 6《最后一格阳光》街角镜头实测(previs→blocking→passes→handoff→comp 全链)。

## 0. 分工铁律

| 层 | 负责 | 不负责 |
|---|---|---|
| **Blender** | 空间真值:构图/透视/机位/焦段/blocking/物体关系/光照方向与时间轴/depth/normal/mask/运动信息 | 表面细节(浪费,AI 会重画) |
| **AI(i2v/ControlNet)** | 表面复杂度:材质历史/涂鸦/污渍/大气/难做的视觉细节/有限时间变换 | 空间结构(必须被 control passes 约束) |
| **合成** | 整合/遮罩/光学质感(halation/grain/黑位)/分级/时间清理/节奏 | 掩盖资产层错误(fidelity-rules 禁止) |

AI 通道不可用时:**不假装**,出完整 handoff package(见 §3),这是合法交付物。

## 1. Blocking 纪律(实测教训)

- 先 previs(film-development-previs 的 shot list/光照态直接变成 Blender 设定),每轮渲 2–3 静帧看图再继续,构图迭代平均 3–4 轮
- **影子施主先算再摆**:影高=施主高−距离×tan(仰角);水平漂移=距离×tan(方位角)。三次几何试错的案例:全遮挡(太阳仰角10°)→黑屏(相机进了遮挡体)→方位角25°+对街8m楼=对角影界
- 状态型光照(金时→夜)用 keyframe 到 energy/world color;灯光先后亮起错峰 0.8s
- 资产:blocking 用程序化原语即可;每个资产在 SHOT_SPEC 里记来源/授权/面数;外部资产(Poly Haven CC0 等)需要时下载前确认

## 2. Control passes:材质覆盖法(Blender 5.1 无头最稳)

**不要用无头合成器**(5.1 陷阱实测:`scene.node_tree` 没了、`compositing_node_group` 需手建、OutputFile 的 base_path 也变了)。改材质覆盖:
- depth:emission ← ShaderNodeCameraData『View Z Depth』→ MapRange(0–30m)
- normal:emission ← Geometry Normal × 0.5 + 0.5
- mask:按 `obj.pass_index` 分组,白/黑 emission 轮流赋给全场景
- 渲前:`view_transform='Standard'`、世界强度 0、灯全灭(清 animation_data);渲后恢复原材质
- 输出至少 first/hero/last 三帧的全套 passes

## 3. Handoff package 清单(AI 不可用时的标准交付)

HANDOFF.md 必含:镜头意图与质感目标参考图 / **时间结构表**(状态与帧号,AI 必须保持)/ first+last+hero 帧 / depth+normal+masks(标注编码约定)/ 运动信息(相机路径速度、物体零运动声明)/ prompt / negative constraints / continuity notes(影界形态、灯亮顺序、招牌不发光等)。`.blend` 一并交付(可重渲任意帧)。

## 4. 合成端(无 AE 自动化时的离线配方)

HALO(高光−0.72 阈值→blur18→暖色×0.5 加回)→ SOFT(35/65 blur1.1 混合)→ CHROMA noise 0.012 → TONE(×0.94+0.035 抬黑 + >0.8 段 ×0.65 滚降)→ 单色 GRAIN 0.022 → 晕影(1−0.28r^2.4)。夜态 CG 纯黑必须抬到蓝灰,否则一眼假。详见 after-effects-compositor。

## 5. 验收

三联对比:Blender raw | 质感目标(参考照片/AI 结果) | final comp。差距逐条归层(空间层/表面层/光学层),表面层差距=AI 侧工作,不在 blocking 层硬修。

## 6. 案例库

- **《最后一格阳光》街角**(完整闭环):`~/Desktop/Digital Art/test/results/phase6/`(build_corner_shot.py + SHOT_SPEC + HANDOFF + FIDELITY + final_shot_10s.mp4)
