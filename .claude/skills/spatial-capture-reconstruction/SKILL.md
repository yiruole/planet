---
name: spatial-capture-reconstruction
description: 把现实空间/物体素材(环绕视频、多视角照片、扫描 app 导出)变成可用的 3D 场景:输入质检→路线判断(photogrammetry/GS/NeRF/Blender blocking/不适合)→重建或重拍指南→导入 Blender→观察镜头。触发词:扫描、重建、photogrammetry、splatting、把这个空间做成 3D、scan。
---

# Spatial Capture & Reconstruction v0.1

前置:遵守 `~/.claude/skills/creative-rules/`。基于 Phase 3 画室扫描案例实测。**先判路线再动手,不为完成任务强行选某条路线。**

## 0. 输入质检(任何素材先过这关)

用 `media_inspect.py`(reference-reverse-engineer 自带)出 contact sheet,逐帧看:
1. **它真的是空间素材吗?** 屏录/转发/带 UI 遮罩的视频不是(实测:名为 space.mov 的文件是 Instagram 屏录)。文件名不可信,必看内容
2. **它是原始素材还是重建成品?** 扫描 app(Luma/Scaniverse/Polycam)导出的 reveal 动画是成品渲染——点云渐显开场是标志。成品不能当原始输入重跑管线(视差/曝光已烘焙)
3. 覆盖角度(全 360° 还是正面弧)、高度环数量、运动模糊帧比例、曝光是否锁定
4. **材质红旗**:透明(玻璃/液体)、镜面、弱纹理大平面(白墙/白画布)——特征匹配三大杀手

## 1. 路线判断表

| 条件 | 路线 |
|---|---|
| 有原始多视角照片/视频 + 本机有 COLMAP 等工具链 | photogrammetry(mesh 可编辑,最通用) |
| 需要视点连续渲染、素材充足、有 CUDA/云 | Gaussian Splatting(本机 Apple Silicon 无 CUDA,**当前不可本地执行**) |
| NeRF | 基本被 GS 替代,依赖大,默认不选 |
| 素材是扫描 app 成品 / 素材不足 / 无工具链 | **Blender 手工 blocking**(照片匹配):从 2–3 个清晰帧重建布局/尺度/地标,1 小时内出观察镜头,精度够 previs/打光/机位设计 |
| 素材根本不是空间素材 | 不重建,归档为参考,写明原因 |

**手机扫描 app(Luma/Scaniverse)本身就是合法路线**:用户拍摄→app 出 GS/mesh→导出 PLY/GLB 进 Blender。本机无法重训时,这是真资产的首选通道。

## 2. Blender blocking 重建流程(实测)

1. 从素材抽 2–3 个正交视角清晰帧作 block_ref
2. 无头脚本(`blender -b --python build_x.py -- <outdir> still|anim`):房间壳(地板+墙)→ 家具主体(圆柱/盒子组合)→ 地标物(让空间可辨识的元素,如百叶暖气板=框+横条阵列)→ 材质纯色 Principled → 大面积 area light + 世界光
3. 先渲 2 个静帧与 block_ref 对位,再渲 5–10s 观察镜头(TRACK_TO empty + 相机位置关键帧)
4. 交付:脚本(可重放)+ 对位帧 + turntable + before/after

## 3. 失败修正表(实测)

| 症状 | 原因 | 修法 |
|---|---|---|
| 墙/地之间灰色漏光带 | `primitive_cube_add(size=1)` 后按半尺寸 scale,所有 box 减半 | cube 用 size=2,scale=size/2 才等于目标尺寸;或建后量 bbox 验证 |
| 透明瓶渲成灰渐变团 | EEVEE 折射需逐版本属性(use_ssr_refraction/use_raytracing + 材质 refraction 开关) | hasattr 探测循环设置;blocking 层接受灰代理,成片层换 Cycles 或加环境反射体 |
| 粉色/彩色被洗白 | 强光 + 低饱和 base color | 饱和度加倍再看图,AgX 会再压一档 |
| GS 成品视频喂 photogrammetry | 视差烘焙+运动模糊 → 特征匹配崩 | 不做;要原始素材或重拍 |

## 4. 重拍协议(capture protocol,给用户的拍摄指南)

- 60–120 张 / 60fps 慢环绕,3 个高度环(低/平视/俯),相邻重叠 ≥70%,覆盖全 360°
- AE/AF 锁定,快门 ≥1/120,漫射均匀光,避免硬阴影
- 透明/镜面物:喷哑光显像剂或换替身;弱纹理平面:临时铺报纸/纹理胶带造特征
- 扫描 app 用户:除 reveal 视频外,**务必导出 PLY/GLB 原始资产**——成品动画不可二次加工

## 5. 下游路由

- blocking/mesh → blender-effect-builder(打光/材质/镜头)
- 声音驱动空间 → sound-image-system
- previs/镜头设计 → film-development-previs
- 实时点云美学 → TouchDesigner(GS PLY 可进 TD Point File In)

## 6. 案例库

- **画室一角 blocking**(Phase 3 完整闭环):`~/Desktop/Digital Art/test/results/phase3/`(ROUTE_JUDGMENT.md + build_space_block.py + turntable);素材真相判读(屏录≠空间素材、app 成品≠原始扫描)是本案例核心教训
