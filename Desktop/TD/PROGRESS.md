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

### 魔方几何（当前状态）
- **文件**：`NewProject.12.toe`（bridge 连接此文件）
- **结构**：3个独立 Geo COMP，每层9个cubie，共27个

```
rubik_top (Geo COMP)          → 顶层 9个cubie，黄 #FFE500
  box1(0.9) → copy1(←grid1 3x3 ty=+1, orient=zx) → rot1[display]
  mat1: diff=(1.0,0.9,0.0) emit=(0.5,0.45,0.0)

rubik_mid (Geo COMP)          → 中层 9个cubie，青 #00FFFF
  box1(0.9) → copy1(←grid1 3x3 ty= 0, orient=zx) → rot1[display]
  mat1: diff=(0.0,1.0,1.0) emit=(0.0,0.5,0.5)

rubik_bot (Geo COMP)          → 底层 9个cubie，粉 #FF2D78
  box1(0.9) → copy1(←grid1 3x3 ty=-1, orient=zx) → rot1[display]
  mat1: diff=(1.0,0.18,0.47) emit=(0.5,0.09,0.24)
```

- rot1.ry.expr: `op("../lfo_top/mid/bot")["chan1"] * 180`（3层各自独立旋转）
- torus1：已删除（TD 新建 Geo COMP 自动生成，每次必须立刻删）

### 渲染链
```
rubik_render (geometry="rubik_top rubik_mid rubik_bot")
    → rubik_bloom (maxRadius=0.08, preBlack=0.0)
    → rubik_out
```

### 相机
- tx=0, ty=2, tz=7, rx=-16, ry=0（从正前方略俯视）
- **注意**：ry≠0 会导致相机偏离目标，渲染全黑

### 其他节点
- LFO：lfo_bot(0.08Hz) / lfo_mid(0.05Hz) / lfo_top(0.07Hz) / lfo_cam_x / lfo_cam_y
- 灯光：rubik_key / rubik_fill
- 旧单色 rubik Geo COMP：par.render=False（隐藏，保留备用）

---

## ⚠️ 未验证（明天第一件事）

- **3层颜色渲染未目视确认** — 相机/render geometry 刚修好，还没截图验证
- 所有调参都通过 bridge 做的，今天结束前没有看到最终效果截图

---

## 📋 下一步计划

### 明天第一步：确认视觉效果
1. 打开 `rubik_out` 确认3层颜色（黄/青/粉）正常显示
2. 确认方块形状，不是圆环

### 后续步骤
3. **背景**：深黑 + 透视网格地面（霓虹线框）
4. **灯光升级**：3点霓虹光（青色 key + 粉色 fill + 黄色 rim）
5. **整体旋转**：给3个 Geo COMP 加 ry/rx 表达式（lfo_cam_y/x），让魔方整体缓慢漂移
6. **后处理**：bloom 精调、色差 TOP、暗角
7. **音频驱动**：audiofilein1 → beat 触发旋转加速

---

## 🔴 今天踩坑备忘

| 坑 | 原因 | 教训 |
|----|------|------|
| 渲染全黑 | 相机 ry≠0，没对准立方体 | 相机 ry 必须=0（或明确对准目标） |
| 渲染全黑 | Render TOP 的 geometry 填了完整路径 `/project1/rubik_mid` 而不是名字 `rubik_mid` | geometry 只填节点名，不要填完整路径 |
| 渲染出圆环 | bloom maxRadius=1.0（全屏），任何形状都成圆 | maxRadius < 0.1 |
| 新建 Geo COMP 有圆环 | TD 自动加 torus1.display=True | 建完立刻 destroy() |
| Material SOP 不生效 | per-primitive 材质不被 3D Render 管线读取 | 每层独立 Geo COMP，直接挂 material |
| gridSOP orient | 有效值：`xy`/`yz`/`zx`（不是 `xz`） | 水平层用 `zx` |
| rows=2,cols=2 只有4个点 | rows/cols = 顶点数 | 9个cubie/层需要 rows=3,cols=3 |

---

## 关键文件
```
/Users/ruoleyi/Desktop/TD/
├── NewProject.12.toe        # 当前主文件
├── td_bridge_server.py      # HTTP 桥
├── td_claude.sh             # CLI 工具
├── PROGRESS.md              # 本文件
├── chat-log-2026-06-03.md
└── chat-log-2026-06-04.md
```

## TD API 备忘
```python
sop.display = True           # 设 display flag（不是 par.display）
geo.par.material = mat.path  # 材质挂到 Geo COMP
grid.par.orient = "zx"       # 水平面（ZX Plane）
geo.op("torus1").destroy()   # 新建 Geo COMP 后立刻删
r.par.geometry = "name1 name2"  # Render TOP：只填名字，不填路径
cam.par.ry = 0               # 相机默认朝 -Z，ry=0 才对准原点
```
