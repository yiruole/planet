---
name: image-to-video-director
description: 把单张图片导演成镜头:分析图片承载力(可动什么/不可动什么)→运动与状态设计→本地照片态动画或 AI i2v 交接。触发词:图生视频、image to video、让这张图动起来、单图镜头。
---

# Image-to-Video Director v0.1

前置:遵守 `~/.claude/skills/creative-rules/`。基于 Phase 5 照片态 animatic +《最后一格阳光》handoff 实测。

## 1. 图片承载力分析(先于一切运动设计)

逐项判定这张图允许什么动:
- **光照可动性**:图里有明确光源逻辑(太阳方向/灯具)→ 光照状态变化是最便宜且最有叙事力的运动(实测首选)
- **相机可动性**:透视强、层次多 → 推拉有视差感;平面化构图 → 只适合极缓慢 scale(假 dolly)
- **内容可动性**:区域性微运动(living-painting 位移场,见 footage-transform-lab)适合织物/水面/植被;人脸/文字/结构线是禁区(一动就假)
- **状态可动性**:图里隐含的时间轴(黄昏的图→入夜)= 最高级的"动"

## 2. 三条执行路线

| 路线 | 适用 | 工具 |
|---|---|---|
| **照片态动画**(本地,已实测) | 光照状态变化为主的镜头 | 同一照片做 N 个分级态 + 几何 mask 扫掠 + 灯位 glow 渐亮(配方见 film-development-previs §2) |
| **区域位移场**(本地,已实测) | 表面内容微动 | footage-transform-lab 的 living-painting 配方 |
| **AI i2v 交接** | 需要真新内容(人物动作/大气/复杂视差) | hybrid-cg-ai-cinematography §3 的 handoff package 格式;单图版必含:原图、运动指令(每个运动一句话+禁动清单)、时长/节奏表、negative constraints |

## 3. 运动设计纪律

- 单图镜头的运动预算:**一个主运动 + 至多一个次运动**;运动之间要有因果(影子爬行→灯亮)
- 时间结构先写表(状态×帧号)再动手,AI 路线里这张表就是 continuity notes
- 禁动清单和运动指令同等重要——AI i2v 最常见失败是动了不该动的(文字/结构边缘/人脸)

## 4. 案例库

- **《最后一格阳光》**:街角照片→12s 三镜头 animatic(本地照片态)+ 10s CG 重建镜头 handoff(AI 路线),`~/Desktop/Digital Art/test/results/phase5/`、`phase6/`
