# TD Rubik Cube — 进度文档

## 项目目标
TouchDesigner 2025 (31550) 音乐驱动魔方动效 + Claude Code HTTP 桥实时控制。

**艺术概念：** 群论与强迫性重复 — 魔方的每一步构成数学群，无限拧动隐喻强迫重复。  
**视觉风格：** 全息虹彩 + 病理感 — 暖琥珀背景/彩虹渐变/半透明魔方，强迫性重复的失控观察者。

---

## ✅ 已完成

### 改版计划（NewProject.19.toe）— 2026-06-07 ~ 2026-06-08

#### 改版1：病理配色 ✅（2026-06-07）
- GLSL vertex shader 颜色方案更新至病理霓虹色

#### 改版2b：VHS背景 ✅（2026-06-07）
- `bg_glsl` GLSL TOP：暖琥珀底色 + 晕影 + CRT扫描线 + 颗粒噪声
- `bg_noise` Noise TOP → bg_glsl input 0

#### 改版3：几何 glitch ✅（2026-06-07）
- `cube_glitch_pos` / `cube_glitch_scl` sparse Noise CHOP
- rubik geo tx/ty/sx/sy 表达式驱动偶发拉伸、切边、只剩一角效果

#### 改版4：病态镜头 ✅（2026-06-07/08）
- `rubik_cam` 绕行轨道 0.30 rad/s
- `cam_twitch` sparse Noise → 偶发抽搐（±1.2 单位）
- `cam_zoom` hermite Noise period=1.5s → 半径 1.5（魔方内部）~8.0（远端）
- `cam.par.near = 0.02` 支持内部视角
- GLSL MAT `cullface = 'neither'` 进入内部时仍可见彩色面

#### 改版5：扫描栏 + 随机黑方块 ✅（2026-06-07）
- `scan_bar_pixel` GLSL TOP：uniform uScan 驱动上下循环暗带
- 偶发随机黑色小方块遮挡画面

#### 改版6：器官特征 ✅（2026-06-08）
- `rubik_glsl_pixel` SDF pixel shader
- 每 0.8s 换一次：27 个 cubie 中约 15% 出现眼睛/嘴巴/鼻子/耳朵/眉毛
- 用 `gl_VertexID / 24` 精确识别每个 cubie（648 顶点 ÷ 24 = 27）
- 深色 SDF 轮廓叠在彩色面上

#### 改版7：角落群论字符 ✅（2026-06-08）
- 4 个 Text TOP，Courier New 40px，sparse noise 独立驱动出现/消失
- 内容：`R  U  R' U'` / `(1  3  8  6)(2  5  7)` / `|G| = 43252003274489856000` / 重复序列
- Composite 'add' 模式叠在扫描层上

#### 改版8：全息虹彩配色 ✅（2026-06-08）
- `hologram_grade` GLSL TOP：亮度→颜色渐变映射（暗→琥珀→橙金→青绿→电蓝）
- 动态 hue drift：两组正弦叠加模拟薄膜干涉虹彩效果
- bg_glsl 底色从深紫黑改为暗琥珀 `rgb(0.12, 0.055, 0.008)`

#### 改版9：经典半透明魔方 ✅（2026-06-08）
- 顶点着色器改回经典六色：白/黄/红/橙/绿/蓝，alpha=0.65
- GLSL MAT：srcblend='sa', destblend='omsa', depthwriting=False
- rubik_render 背景 alpha=0（透明）
- 管线重构：
  ```
  bg_glsl → final_add → scan_mult → txt_overs → hologram_grade ─┐
                                                                   ├─ final_over → rubik_out
  rubik_render → rubik_bloom ────────────────────────────────────┘
  ```
- 效果：彩色玻璃魔方，背景全息渐变从面后透出

---

## 当前渲染管线

```
bg_noise → bg_glsl
              ↓
rubik_render → rubik_bloom ──────────────────────────────── final_over → movie_out
                              bg_glsl → final_add → scan_mult ↑
                              (scan_bar×) → txt_c0..3 → hologram_grade ↑
```

---

## 当前 GLSL Shaders

### rubik_glsl_vertex（经典六色 + alpha 0.65）
```glsl
out vec4 vColor;
out vec2 vFaceUV;
out float vCubieID;
void main() {
    vec3 n = N; float t = 0.7; float a = 0.65;
    if      (n.y >  t) vColor = vec4(0.96, 0.96, 0.96, a);  // 白
    else if (n.y < -t) vColor = vec4(1.0,  0.88, 0.0,  a);  // 黄
    else if (n.z >  t) vColor = vec4(0.9,  0.06, 0.06, a);  // 红
    else if (n.z < -t) vColor = vec4(1.0,  0.50, 0.0,  a);  // 橙
    else if (n.x < -t) vColor = vec4(0.05, 0.75, 0.20, a);  // 绿
    else if (n.x >  t) vColor = vec4(0.05, 0.30, 0.90, a);  // 蓝
    else               vColor = vec4(0.04, 0.04, 0.04, 0.3); // 内面
    vCubieID = float(gl_VertexID / 24);
    vFaceUV  = uv[0].st;
    gl_Position = TDWorldToProj(TDDeform(TDPos()));
}
```

### rubik_glsl_pixel（器官 SDF + 时间 uniform）
- 5 种器官：眼睛（两圆）/ 嘴巴（V折线）/ 鼻子（三角）/ 耳朵（半圆）/ 眉毛（斜段）
- uniform `uTime.x = me.time.seconds`
- 15% 概率出现，每 0.8s 切换一次

### hologram_grade pixel（虹彩背景映射）
- 5 色阶：深琥珀 → 暖琥珀 → 橙金 → 青绿 → 浅电蓝
- hue drift = sin(x*5.2+y*3.7+t*0.22)*0.07 + sin(y*7.1-x*2.5+t*0.38)*0.04
- 饱和度 ×1.15

---

## 相机参数（rubik_cam）
- 轨道速度：0.30 rad/s
- 半径范围：1.5（内部）~8.0（远端），cam_zoom hermite 周期 1.5s
- 抽搐：cam_twitch sparse noise → ±1.2 单位
- near clip：0.02

---

## 录制
- `rubik_hologram_30s.mov`（MJPA, 30fps, 30s, 74.2MB）— 2026-06-08 完成
- 录制方法：`movie_out.par.addframe.pulse()` × 900 帧（record=True toggle 本身不触发写帧）

---

## 踩坑备忘

| 坑 | 教训 |
|----|------|
| bloom maxRadius=1.0 | 任何形状变圆，必须 < 0.1 |
| TD render background | `par.bgcolora`（不是 bgcoloralpha） |
| GLSL TOP TDTime | GLSL TOP 无此 uniform，用 me.time.seconds 经 vec uniform 传入 |
| Composite 'over' 输入顺序 | Input 0 = 前景（A），Input 1 = 背景（B） |
| Text TOP 分辨率 | `outputresolution='custom'` + resolutionw/h，否则用 useinput 无 input 则默认分辨率 |
| Text TOP 字号 | 必须用 `fontsizexunit='pixels'` + 40px，points 单位实际像素极小 |
| movie_out record toggle | `par.record=True` 不写帧！必须用 `par.addframe.pulse()` 手动触发每帧 |
| 透明几何体渲染 | srcblend='sa', destblend='omsa', depthwriting=False |
| GLSL MAT cubie 识别 | 用 `gl_VertexID / 24`（648顶点÷24=27cubie），不能用位置（层旋转后坐标混乱） |
| Text TOP 可见性 | 用 Composite 'add' 模式叠字体（不依赖 alpha 通道） |

---

## 关键文件
```
/Users/ruoleyi/Desktop/TD/
├── NewProject.19.toe            # 当前主文件
├── rubik_hologram_30s.mov       # 最新视频（30s, 74.2MB, MJPA）
├── rubik_v2.mov                 # 旧版视频
├── td_bridge_server.py          # HTTP 桥服务器
├── td_claude.sh                 # CLI 工具
├── PROGRESS.md                  # 本文件
└── rubik_build.py               # 初始构建脚本（历史参考）
```
