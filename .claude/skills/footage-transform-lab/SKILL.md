---
name: footage-transform-lab
description: 对已有实拍/渲染素材(MOV/MP4)做结构性时间变换与运动驱动的画面转化(motion trace/temporal echo/帧差分析),而非简单叠加滤镜。ffmpeg+numpy 本地处理,不修改原件。触发词:处理这段素材、motion trace、temporal echo、时间回声、footage 变换、素材实验。
---

# Footage Transform Lab v0.1

前置:遵守 `~/.claude/skills/creative-rules/`(尤其 media-rules:原件只读,产物入独立目录)。

## 定位

把已有 footage 当作**可被运动/时间结构驱动的场**来变换,不做贴纸式 overlay。v0.1 只包含已实测的最小闭环;depth/optical flow/segmentation 等 ML 能力**按需再引入**,不预装。

## 工作流

1. **检查**:复用 `~/.claude/skills/reference-reverse-engineer/scripts/media_inspect.py`(ffprobe 元数据 + shot 检测 + contact sheet)——不重复造
2. **代理**(素材大于 1080p 或长于 1min 时):`ffmpeg -i in -vf scale=-2:720 -c:v libx264 -crf 23 proxy.mp4`,实验都在代理上做,满意后原素材重跑
3. **变换**:本 skill 工具(见下)
4. **验证**:输出必须真实播放检查——至少抽 3 帧看图 + ffprobe 确认时长帧数一致

## 已实测工具

### motion_trace.py — 运动轨迹 / 时间回声

```bash
python3 ~/.claude/skills/footage-transform-lab/scripts/motion_trace.py <video> \
  [--mode trace|echo] [--decay 0.92] [--threshold 14] [--strength 1.0] [-o out.mp4]
```

原理:逐帧 luma 差分 → 软阈值运动遮罩 → 衰减累积缓冲 → 与当前帧合成。运动区域留下衰减轨迹(trace)或幽灵残影(echo),静止区域不受污染——效果与素材运动结构耦合。

**参数启发式**(实测):
- `decay` 0.90–0.95 常用;0.95+ 轨迹拖很长(仪式感/拖影),<0.88 几乎即逝(紧张感)
- `threshold` 14 起步;素材噪点多(实拍暗部)提到 20+,否则噪点会被当成运动
- 慢速素材(开花/云)运动幅度小,`threshold` 降到 8–10 且 `softness` 降到 12,否则遮罩全黑无效果
- `echo` 模式亮度会累积,`strength` 从 0.6 试起

**性能**:720p 纯 numpy 管线约 15–25 fps 处理速度,10s 素材 <1min。

## 失败修正表

| 症状 | 原因 | 修法 |
|---|---|---|
| 输出和原片没区别 | 运动幅度低于阈值 | threshold↓ softness↓;先跑一遍看 mask(临时把 comp 换成 mask 可视化) |
| 满屏噪点轨迹 | 阈值低于素材噪声 | threshold↑;或先给素材轻度降噪(`hqdn3d`) |
| echo 模式画面发白 | 亮度无界累积 | strength↓ decay↓ |
| 输出打不开 | 分辨率奇数 | 编码端已 yuv420p,若源是奇数宽高先 `scale=ceil(iw/2)*2:ceil(ih/2)*2` |

### 区域遮罩时变位移场 —— "静物活化 / living painting"(AE video2 实测)

单帧(或静止镜头)→ 指定区域内容持续微幅重排,区域外(边框/墙/背景)零位移。适用:让画/照片/织物"活起来",复刻"刚性边界静止、内容呼吸换位"类参考。

配方(numpy+scipy,模板 `~/Desktop/Digital Art/AE/video2/results/mvp/living_painting_mvp.py`):
- 粗网格(约 10x6)随机位移场,**每 K 帧生成新 key field + smoothstep 时域插值**(K=9–12)。离散换场给"重排/stop-motion 感";连续正弦驱动只会得到"果冻晃动",不是同一效果身份
- bicubic `zoom` 上采样到画幅 → `map_coordinates` 双线性重采样(半分辨率迭代,秒级/百帧)
- 位移乘以**软遮罩**(矩形+gaussian feather σ≈7):遮罩必须收到内容区内沿——feather 半径会向外渗出,σ14 时画框仍会波浪形变形
- 幅度先小后校:用 `tblend=difference,signalstats` YAVG 均值对标参考,**按运动区域占画面比例归一再比较**(区域占 42% 时,整幅 2.5 ≈ 参考满幅 6.0)

验收必看**帧差图**(f0 vs f60 difference):应动区域亮、应静区域(边框/背景)全黑——遮罩渗漏在成片里肉眼难察觉,帧差图一眼暴露。

**迁移到视频素材的三个前置条件(Phase 2 实测,静照配方的隐藏假设)**:
1. **底板必须(近)静止**:呼吸位移(运动量 ≈2.5)会被相机运动(13–55)完全淹没——先逐秒扫描运动量选最稳窗口,再相位相关稳像(1/4 降采样灰度 FFT 平移跟踪,累计漂移);**稳像偏移与效果位移合并成单次 map_coordinates**(两次插值会糊)
2. **动镜头需要遮罩跟踪**:静态矩形遮罩只适用锁定机位;平移跟踪已实测可用,推进镜头的尺度变化需相似变换跟踪(未实现)或 AE 真跟踪
3. **手机实拍要锁曝光**:iPhone 自动曝光逐帧泵动全画面亮度(帧差图上墙面出现亮度带);修法:取画面内静止基准区(墙面 patch)逐帧增益归一
模板:`~/Desktop/Digital Art/AE/video2/results/mvp2/living_painting_video.py`

### 2.5D 面片投影 —— footage 贴 3D 几何(AE video1 人脸手风琴实测)

把视频逐帧切条/切块,贴到程序定义的 3D 面片组(手风琴/折页/卡片扇)上做真透视投影——**不需要 Blender**,纯 numpy 在秒级/帧完成,素材保持"活的"(逐帧取源视频,不是静帧贴图)。

配方(模板 `~/Desktop/Digital Art/AE/video1/results/mvp/face_accordion_mvp.py`):
- 几何:面板顶点链显式构造(手风琴 = x 前进 + z 交替 zigzag),折角/整体 yaw 用 t 的正弦驱动
- 投影:每面板 4 点对应 SVD 解 homography → 3x3 逆矩阵 → 目标 bbox 网格逆映射 `map_coordinates`;按相机空间深度**远→近**绘制解决遮挡
- **立体感主要来自明暗交替,不是透视**:光源必须偏侧向(正面光下相邻面板 dot 几乎相同,zigzag 读不出来);shade 底 ≈0.55——再低背光面变剪影,内容不可读(两端都实测踩过)
- 逐帧成本:8 面板 540x960 约 0.5s/帧,120 帧 ≈1min

边界:需要人物抠像(内容与背景分离)时本配方到顶——segmentation 是 ML 缺口,精细 roto 归 AE。

## 探索方向(未实现,逐个由真实创作需求驱动)

footage as field / membrane 形变 / optical-flow displacement / depth 空间重投影 / 不可能的连续性 / 区域属性交换 / 位移场量化+patch 重排(把"流动感"升级为真"跳位重排")。每个方向做成独立小脚本,不做大框架。

## 边界

- 需要 3D 空间重建/重打光 → Blender/Houdini(导出数据用)
- 精细 roto/tracking 合成 → AE
- 实时处理 → TD(本 skill 是离线批处理)
