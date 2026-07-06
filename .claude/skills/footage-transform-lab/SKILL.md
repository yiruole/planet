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

## 探索方向(未实现,逐个由真实创作需求驱动)

footage as field / membrane 形变 / optical-flow displacement / depth 空间重投影 / 不可能的连续性 / 区域属性交换。每个方向做成独立小脚本,不做大框架。

## 边界

- 需要 3D 空间重建/重打光 → Blender/Houdini(导出数据用)
- 精细 roto/tracking 合成 → AE
- 实时处理 → TD(本 skill 是离线批处理)
