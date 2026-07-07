---
name: after-effects-compositor
description: 合成职能(AE 角色):成像链/分级/整合/遮罩/时间清理。本机 AE 无自动化通道——离线用 numpy/ffmpeg 配方,实时用 TD;真需要 AE 手工步骤时输出操作清单。触发词:合成、compositing、调色、成像链、grain、把 CG 合进实拍、AE。
---

# After-Effects Compositor v0.1

前置:遵守 `~/.claude/skills/creative-rules/`。**AE 2025 本机无自动化通道**(ExtendScript 桥未建)——本 skill 是"合成职能"的路由与已验证配方;AE 本体只在需要其独有能力时给手工步骤清单。

## 0. 路由

| 需求 | 路线 |
|---|---|
| 批量成像链/分级(离线) | **numpy/scipy 逐帧**(实测 2 案例:backrooms、街角镜头)或 ffmpeg 滤镜链 |
| 实时合成/音频驱动混合 | **TD**(touchdesigner-effect-builder 成像链配方) |
| 精细 roto/planar tracking/人物抠像/表达式绑定 | **真 AE 手工**——输出步骤清单给用户;这是当前系统三大能力缺口(roto/tracking/segmentation)的官方归属地 |

## 1. 成像链配方("拍出来的"质感,顺序重要,两案例验证)

HALO → SOFT → CHROMA → TONE → GRAIN → 晕影/HSV:
1. **HALO**:`clip(lum-0.72)` → gaussian σ18 → ×暖色(1.0,0.75,0.45)×0.5 加回(halation 在软化前)
2. **SOFT**:原图 35% + blur σ1.1 65%(吃 CG 锐边)
3. **CHROMA**:彩色噪声 ±0.012
4. **TONE**:×0.94 + 0.035 抬黑位;>0.8 高光段斜率×0.65 滚降——**夜景 CG 纯黑必须抬到蓝灰,否则一眼假**
5. **GRAIN**:单色噪声 ±0.022(grain 永远最后加,在所有几何/模糊操作之后)
6. 晕影 `1-0.28·r^2.4`
模板:`~/Desktop/Digital Art/test/results/phase6/comp_grade.py`(300 帧 960x640 约 2min)

## 2. 已验证的合成端小配方

- **曝光锁定**:手机素材自动曝光泵动→取画面静止基准区逐帧增益归一(footage-transform-lab Phase 2)
- **合成端救暗部**:先加(lift)后乘,乘法分级救不了近 0 值(blender-effect-builder 夜景条款)
- **状态切换合成**:同底板多状态+时序混合,替代连续动画(reference-reverse-engineer 判别启发)
- **对比验收**:raw|target|comp 三联;分层归因(空间/表面/光学),不许用光学层掩盖资产层问题

## 3. 何时真的开 AE(手工清单模式)

roto 人物/毛发、planar tracking 贴屏、复杂 matte 交互、逐帧手绘修补。给用户的清单必须含:输入文件路径、目标、逐步操作、导出设定(ProRes/H.264、色彩空间)、回传路径。

## 4. 缺口台账(诚实记录)

- ExtendScript/UXP 自动化桥:未建(future)
- ML segmentation(人物抠像自动化):无 opencv/torch,arm64 环境未建
- 光流工具:未引入
这三项解锁前,涉及它们的需求一律走"AE 手工清单"或明确告知不可行。

## 5. 案例库

- **街角镜头合成**:`~/Desktop/Digital Art/test/results/phase6/`(comp_grade.py + raw_vs_comp.png)
- **backrooms TD 实时链**:`~/Desktop/Digital Art/reverse/xhs_test1/`
- **AE 双测试**(位移场/2.5D 面片,合成职能由 Python 承担):`~/Desktop/Digital Art/AE/video1、video2/results/`
