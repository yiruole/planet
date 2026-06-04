# TD Rubik Cube — 进度文档

## 项目目标
TouchDesigner 2025 (31550) 音乐驱动魔方动效 + Claude Code HTTP 桥实时控制。

**艺术概念：** 群论与强迫性重复 — 魔方的每一步构成数学群，无限拧动隐喻强迫重复。  
**视觉风格：** 80年代 vaporwave / synthwave 霓虹美学。

---

## ✅ 已完成

### 基础设施
- HTTP 桥：`td_bridge_server.py` → TD Web Server DAT (端口 9980)
- CLI：`td_claude.sh`

### 魔方几何（正常工作）
- **文件**：`NewProject.14.toe`（bridge 连接此文件）
- **结构**：单 rubik Geo COMP，内部：
  ```
  grid_bot/mid/top (orient=zx, rows=3, cols=3, ty=-1/0/+1)
      → copy_bot/mid/top (← box1, size=0.9)
      → color_bot/mid/top (Script SOP，目前有 Cd 属性问题)
      → rot_bot/mid/top (ry = lfo 表达式)
      → merge1 [display=True]
  ```
- **27个 cubie**（3层 × 9个），旋转正常
- **相机公转**：tx/tz 使用 sin/cos 绕魔方旋转，lookat 始终对准 rubik
- **音频驱动**：audiofilein1 → audio_env(envelopeCHOP) → audio_math(mathCHOP, gain=5)  
  → cam.par.ty 和 cam.par.tz 随音量变化

### 渲染链
```
rubik_render → rubik_bloom (maxRadius=0.05, preBlack=0.3) → rubik_out
```

### 视频输出
- `movie_out` (moviefileoutTOP)：mpeg4, MP4, 30fps, 30秒, 无音轨
- 已录制一段（rubik_30s.mp4），但颜色方案未完成前录的

---

## 🔴 进行中：计划1 — 真实魔方6面配色

### 目标配色
| 面 | 颜色 | Hex |
|---|---|---|
| 顶 +Y | 电光黄 | `#FFE500` |
| 底 -Y | 热粉红 | `#FF2D78` |
| 前 +Z | 霓虹青 | `#00FFFF` |
| 后 -Z | 电橙 | `#FF6B35` |
| 左 -X | 霓虹绿 | `#39FF14` |
| 右 +X | 电蓝 | `#0080FF` |
| 内面 | 近黑 | `#0A0A0A` |

### 当前状态
- **Script SOP 方案**：在 copy→rot 之间插入 color_bot/mid/top Script SOP，  
  逻辑正确（用面重心坐标判断外表面）但 `addPointAttr('Cd',...)` 在 TD 2025 里无效，  
  geometry 里没有 Cd 属性产生
- **GLSL MAT 方案**：创建了 `rubik_glsl`，但 shader 编译报错  
  核心发现：**TD 建 GLSL MAT 时自动生成 `rubik_glsl_vertex` 和 `rubik_glsl_pixel` Text DAT，  
  应该编辑这两个，而不是自己创建的 rubik_vert/rubik_frag**

### 明天第一步
1. 查看 `rubik_glsl_vertex.text` 和 `rubik_glsl_pixel.text` 的默认内容和格式
2. 在这两个 DAT 里写入颜色逻辑（用 P.xyz 判断面方向）
3. 把 `rubik_glsl` 的 vdat/pdat 设为这两个默认 DAT
4. 验证颜色显示正确

---

## 📋 后续计划（颜色解决后）

1. 背景：深黑 + 透视网格地面（霓虹线框）
2. 灯光升级：3点霓虹光（青色 key + 粉色 fill + 黄色 rim）
3. 相机动画精调：更戏剧化的远近变化
4. 后处理：bloom 精调、色差 TOP、暗角
5. 音频驱动进阶：beat 触发旋转加速
6. 录制最终 30 秒视频（含音频）

---

## 🔴 踩坑备忘（2026-06-04~05）

| 坑 | 教训 |
|----|------|
| bloom maxRadius=1.0 | 任何形状变圆，必须 < 0.1 |
| 新建 Geo COMP 有 torus1.display=True | 建完立刻 destroy() |
| TD gridSOP orient | 有效值：`zx`（水平），不是 `xz` |
| rows=2,cols=2 只有4个点 | 9cubie/层需要 rows=3,cols=3 |
| 相机 ry≠0 | 不对准立方体，渲染全黑 |
| Script SOP addPointAttr('Cd',...) | 在 TD 2025 无效，Cd 属性不会被创建 |
| Script SOP prim.points | td.Poly 对象用 prim.verts（但只在 SOP 上下文有效） |
| GLSL MAT 自己建 DAT | 应用 TD 自动创建的 rubik_glsl_vertex/pixel |
| audioenvelopeCHOP | 不能直接 create，用 envelopeCHOP + mathCHOP 代替 |
| Render TOP geometry 填完整路径 | 只填节点名，不填路径 |

---

## 关键文件

```
/Users/ruoleyi/Desktop/TD/
├── NewProject.14.toe            # 当前主文件
├── backup_before_plan1_20260605_0047.toe  # 计划1执行前备份
├── rubik_30s.mp4                # 已录制视频（颜色未完成）
├── td_bridge_server.py
├── td_claude.sh
├── PROGRESS.md                  # 本文件
├── chat-log-2026-06-03.md
└── chat-log-2026-06-04.md
```

## TD API 备忘

```python
# Script SOP 内部可用（exec上下文不可用）
prim.verts          # ✅ SOP上下文
prim.points         # ❌ td.Poly没有这个属性

# GLSL MAT
mat.par.vdat = "rubik_glsl_vertex"   # 用TD自动生成的DAT
mat.par.pdat = "rubik_glsl_pixel"    # 用TD自动生成的DAT
# 不要自己建 DAT 给 GLSL MAT

# 音频
envelopeCHOP → mathCHOP(gain=5)     # 提取音量
audioenvelopeCHOP                    # ❌ 不能直接 create

# 相机公转
cam.par.lookat = "/project1/rubik"   # 始终看着魔方
cam.par.tx.expr = "math.sin(absTime.seconds*0.25)*6"
cam.par.tz.expr = "math.cos(absTime.seconds*0.25)*6 - op('audio_math')[0]*2"
```
