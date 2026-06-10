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

### v8 (2026-06-10) ← 当前版本
**达利时钟 — 铬合金表框 + 罗马数字 + 右侧不对称下垂（对标参考图）：**

| 部分 | 实现 |
|---|---|
| 表框 | 圆截面法线 → Blinn-Phong specular (shininess=120) + Schlick Fresnel (F0=0.95) |
| 颜色 | 冷银色 `(0.82, 0.86, 0.92)` + 高光两层（细亮点+宽散射）+ 蓝调边缘补光 |
| 熔化方向 | 右侧下垂（`smoothstep(-0.12, 0.82, q.x)` × 二次方下垂），左/顶保持圆形 |
| 罗马数字 | gI/gV/gX 三基元 SDF 组合出 I–XII，stroke=0.24 glyph单位 |
| 表盘 | 象牙色 + 边缘 AO + 中心微凹阴影 |
| 上弦旋钮 | 顶部小圆球，独立法线铬金属高光 |
| 可调参数 | `shininess=120`（高光锐度）、`strokeW=0.24`（数字粗细）、`RIM_IN/OUT=0.90/1.18`（表框宽度） |

### v7 (2026-06-10)

| 特性 | 说明 |
|---|---|
| 时钟平面 | z=2.0，位于第二云层中心，世界坐标 (0, 1.95, 2.0) |
| 半径 | 0.70 世界单位，帧中央醒目可见 |
| 熔化变形 | `unmelt()`: 下半部分二次方下垂，侧面随时间摆动 |
| 表盘颜色 | 过亮象牙色 (1.30, 1.26, 1.15) + 外发光晕，确保穿透云层 |
| 表针 | 时针 `uTime×0.07`，分针 `uTime×0.87`，12个刻度 |
| 合成方式 | 双轨：55% 受前方云层透射率影响 + 45% 保底亮度（绝不完全消失） |

**待确认：**
- 时钟是否在TD中清晰可见（如不可见需检查 `CLK_C` 位置是否在摄像机视野内）
- 熔化幅度是否合适（`droop * droop * 0.42` 可调）
- 可调参数：`CLK_C`（位置）、`CLK_R`（大小）、`vis = tr*0.55+0.45`（透明度平衡）

### v6 (2026-06-08)
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

- [ ] v7 TD中视觉确认 — 时钟是否可见，熔化形态是否自然
- [ ] 如有需要：调整时钟位置/大小/透明度平衡
- [ ] v6 云层本身视觉确认（独立云朵层叠是否清晰）
- [ ] 如云层仍模糊：考虑 Worley noise 或显式球形云团方案
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
