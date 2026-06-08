# TDcloud — 3D Volumetric Cloud Progress Log

## 目标
TouchDesigner GLSL raymarching 3D体积云，随音乐强弱动态变化形状。

**最终效果要求：**
- 边界清晰的积云，能看出一朵朵层叠结构
- 形状不停移动变换，音乐响则快，音乐弱则慢
- 深蓝色天空背景

**音乐来源：** `audiofilein1` → `/Users/ruoleyi/Desktop/output.flac`

---

## 技术架构

```
audiofilein1 (CHOP)
  → cloud_analyze_rms (Analyze CHOP, RMS)
  → cloud_lag_growth  (Lag CHOP)
  → cloud_growth_chop (Script CHOP) ← cloud_growth_dat (callbacks)
      输出: cloud_time (累积时间轴，音量越大推进越快)

cloud_glsl (GLSL TOP)
  uniform uTime = cloud_growth_chop['cloud_time']
  uniform uBeat = lag_beat['chan1'] * 10
  → cloud_out (Out TOP)
```

**GLSL版本：** 4.30，需要 `layout(location=0) out vec4 fragColor;`

---

## 版本历史

### v1–v2 (初版)
- 结果：只有蓝色静态天空，无云
- 问题：uniform名称用错（`uniname0` 应为 `vec0name`），fragColor未声明

### v3
- 引入 FBM domain warping
- 结果：有云但形状是规则三角形
- 问题：horizontal envelope用了渐变锥形，warp幅度1.8太大导致模糊

### v4 (2026-06-07)
- 引入 Script CHOP 累积 cloud_time（替代 uGrowth 生长逻辑）
- 改为"云始终存在，形状随音乐速度变换"
- `pow(excess,1.5)*14` 试图做锐边
- 深蓝天空配色
- **结果：有云但仍然模糊，几乎不动**
- 根因分析见v6

### v5 (2026-06-08)
- `excess*30` 线性斜坡替换 `pow(x,1.5)`
- Beer-Lambert系数降至4.5
- Script CHOP baseline提升至0.15/s
- **结果：未部署即升级v6**

### v6 (2026-06-08) ← 当前版本
**三个根因彻底修复：**

| 根因 | v4症状 | v6修复 |
|---|---|---|
| `pow(x,1.5)` 边界导数=0 | 云边缘柔化无法变硬 | `excess*45` 线性，边界立即起跳 |
| FBM scale=0.42，特征~2.4wu | 整片视野只有1个大模糊团 | scale=0.85，每朵~1.2wu，3-4朵/层 |
| cloud_time 推进速度≈0.10puff/s | 肉眼看不出任何移动 | baseline=0.8/s，安静时也能看到移动 |
| Beer-Lambert coeff=14 太高 | 整片云瞬间不透明，看不出结构 | coeff=3.5，边缘2-3步渐变显立体 |

**v6关键参数：**
- 3个云层：yBase=0.10, 1.50, 2.85，zOffset=-0.5, 2.0, 5.0（深度视差）
- 每层独立noise seed + 不同时间倍数（×1.0, ×1.22, ×1.45）
- Script CHOP: `rate = 0.8 + rms * 20.0`（silence→0.8/s，loud→3.8/s）
- 摄像机：`ro=(0.5,-0.7,-4.8)` 仰视，`tg=(0,1.8,1.5)`

---

## 待解决

- [ ] v6部署后视觉确认 — 是否出现独立云朵层叠
- [ ] 如果仍模糊：考虑换 Worley noise 或显式球形云团方案
- [ ] 录制最终版本视频

---

## 部署方式

```bash
# 终端里：
source /Users/ruoleyi/Desktop/TDcloud/td_claude.sh
td_ping   # 确认TD WebServer DAT在线（port 9980）
td_execfile /Users/ruoleyi/Desktop/TDcloud/deploy_v6.py
```

---

## 已知TD坑

- `par.pause` 不存在于 audiodeviceinCHOP → 用 `try_set()` 包裹
- `par.resolution` 不存在 → 用 `par.resolutionw` / `par.resolutionh`
- Script CHOP 必须有输入才会每帧cook → 连接 rms_op 作为输入
- Analyze CHOP 输出通道名是 `chan1`/`chan2`，不是 `v1`
- GLSL 4.30: `const vec3 v = normalize(...)` 非法，normalize不是常量表达式
- uniform参数名：`vec0name` / `vec0valuex`（不是 `uniname0` / `unival0x`）
