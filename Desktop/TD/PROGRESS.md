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

### 魔方几何 ✅
- **文件**：`NewProject.14.toe` 或更高版本
- **结构**：单 rubik Geo COMP
  - `grid_bot/mid/top` (orient=zx, rows=3, cols=3, ty=-1/0/+1)
  - → `copy_bot/mid/top` (← box1, size=0.9)
  - → `rot_bot/mid/top` (ry = lfo 表达式)
  - → `merge1` [display=True]
- **27个 cubie**，三层独立旋转

### 6面霓虹配色 ✅（计划1完成）
- **方案**：GLSL MAT，用面法线 `N` 判断颜色
  - threshold=0.7：法线分量 > 0.7 认定为该方向外表面
  - 用 TD 自动创建的 `rubik_glsl_vertex` / `rubik_glsl_pixel` DAT
  - Box SOP 使用非共享顶点 → 同一面所有顶点法线相同 → 面颜色无渐变
- **颜色方案**：
  | 面 | 颜色 | Hex |
  |---|---|---|
  | 顶 +Y (法线y>0.7) | 电光黄 | `#FFE500` |
  | 底 -Y (法线y<-0.7) | 热粉红 | `#FF2D78` |
  | 前 +Z (法线z>0.7) | 霓虹青 | `#00FFFF` |
  | 后 -Z (法线z<-0.7) | 电橙 | `#FF6B35` |
  | 左 -X (法线x<-0.7) | 霓虹绿 | `#39FF14` |
  | 右 +X (法线x>0.7) | 电蓝 | `#0080FF` |
  | 内面 | 近黑 | `#0A0A0A` |
- 颜色随层旋转而变化（层转时法线随几何体转动，颜色自然跟着走）

### 渲染链
```
rubik_render → rubik_bloom (maxRadius=0.05) → rubik_out
```

### 相机动画（音频驱动）
- 绕魔方公转：`tx = sin(t*0.25)*6`, `tz = cos(t*0.25)*6 - audio*2`
- 高度随音量：`ty = 2 + audio*2`
- `cam.par.lookat = "/project1/rubik"`
- 音频链：audiofilein1 → envelopeCHOP → mathCHOP(gain=5)

### 视频输出
- `rubik_v2.mp4`（mpeg4, 30fps, 30s）— 录制中 / 已完成

---

## 📋 下一步

1. **视觉精调**：
   - bloom 参数（当前 preBlack=0.3, radius=0.05）
   - 背景：深黑 + 可选透视网格地面
   - 加霓虹自发光（当前颜色较暗，可增加 emission 效果）
2. **灯光升级**：多点霓虹灯光（青/粉/黄）
3. **音频驱动进阶**：beat 触发旋转加速
4. **录制最终带音轨视频**（当前 mpeg4 不支持 AAC，需后期合并音频）

---

## 🔴 踩坑备忘（完整）

| 坑 | 教训 |
|----|------|
| bloom maxRadius=1.0 | 任何形状变圆，必须 < 0.1 |
| 新建 Geo COMP 有 torus1.display=True | 建完立刻 destroy() |
| TD gridSOP orient | 有效值：`zx`（水平），不是 `xz` |
| rows=2,cols=2 只有4个点 | 9cubie/层需要 rows=3,cols=3 |
| 相机 ry≠0 不对准 | 用 `lookat` 参数而不是手动设 ry |
| Script SOP addPointAttr('Cd',...) | TD 2025 无效，Cd 属性不会被创建 |
| GLSL MAT：自己建 DAT | 应用 TD 自动创建的 `name_vertex` / `name_pixel` |
| GLSL flat + position | 角落 cubie 两个三角形取不同顶点颜色 → 花格 |
| Geometry Shader | macOS Metal 不支持 |
| GLSL position 上色 | 用法线 N 代替位置，Box SOP 非共享顶点保证面内颜色一致 |
| audioenvelopeCHOP | 不能直接 create，用 envelopeCHOP |
| GLSL 最小 shader 格式 | 必须参考 TD 默认模板（TDPos, TDDeform, oFragColor, TDCheckDiscard） |

---

## 关键文件

```
/Users/ruoleyi/Desktop/TD/
├── NewProject.14.toe            # 当前主文件（或更高版本）
├── backup_before_plan1_*.toe    # 计划1前备份
├── rubik_v2.mp4                 # 最新视频（正在录制/已完成）
├── rubik_30s_old.mp4            # 旧版视频
├── td_bridge_server.py
├── td_claude.sh
└── PROGRESS.md
```

## GLSL Shader 当前代码

### rubik_glsl_vertex
```glsl
out vec4 vColor;
void main() 
{
    vec3 n = N;
    float t = 0.7;
    if      (n.y >  t) vColor = vec4(1.0,  0.898, 0.0,  1.0); // 黄
    else if (n.y < -t) vColor = vec4(1.0,  0.176, 0.47, 1.0); // 粉
    else if (n.z >  t) vColor = vec4(0.0,  1.0,   1.0,  1.0); // 青
    else if (n.z < -t) vColor = vec4(1.0,  0.42,  0.21, 1.0); // 橙
    else if (n.x < -t) vColor = vec4(0.224,1.0,   0.08, 1.0); // 绿
    else if (n.x >  t) vColor = vec4(0.0,  0.502, 1.0,  1.0); // 蓝
    else               vColor = vec4(0.04, 0.04,  0.04, 1.0); // 内面黑
    gl_Position = TDWorldToProj(TDDeform(TDPos()));
}
```

### rubik_glsl_pixel
```glsl
in vec4 vColor;
out vec4 oFragColor;
void main()
{
    TDCheckDiscard();
    oFragColor = TDOutputSwizzle(vColor);
}
```
