# Phase 6 — AI image/video handoff package(2026-07-08)

本机无可用 AI 视频生成通道(不调用付费 API,不假装完成)。以下为可直接交给 Runway/Kling/Luma/ComfyUI(depth/normal ControlNet)等服务的完整交接包。

## 镜头意图
《最后一格阳光》主镜头,10s @30fps,960x640(可上采样)。新奥尔良法语区街角(参考 `../../2.imagetovideo.JPG` 为最终质感目标):赤陶红灰泥双立面、白色腰线/檐口、封板拱门(胶合板+WAR 涂鸦)、悬挂地产招牌、黑色铸铁灯柱、两盏煤气壁灯。

## 时间结构(AI 侧必须保持)
- f001–150 GOLD:低角度暖阳(3200K 感),对角硬影盖住画面左下(影界=画面最强线)
- f150–200 DUSK:直射光撤走,-2.5 stop,影界消失
- f200–212 静场
- f212(左灯)/ f236(右灯)NIGHT:煤气壁灯先后亮起,暖橙光池半径 ~1.5m,靛蓝夜环境
- 全程相机匀速推近(10.5,-10.5)→(6.8,-6.8)m,朝向街角,无摇移

## 控制素材(本目录)
- `still_f001.jpg` first frame / `anim/f0300.jpg` last frame / `anim/f0270.jpg` hero frame(夜态)
- `passes/depth_f*.jpg`(camera view-Z,MapRange 0–30m)
- `passes/normal_f*.jpg`(world normal ×0.5+0.5)
- `passes/mask_building/lamps/street/sign_f*.jpg`(object-index 硬遮罩)
- `corner_shot.blend`(完整工程,可重渲任意帧/任意 pass)
- 运动信息:相机线性推近 3.7m/10s,视差纯平移;场景零物体运动;光照状态时间轴见上

## Prompt(建议)
"New Orleans French Quarter corner building at golden hour transitioning to night, terracotta red stucco facade, white cornice bands, arched doorways boarded with plywood, graffiti, hanging realty sign, black cast-iron lamp post, two gas wall lanterns turning on one after another, hard diagonal shadow sweeping across the facade, slow dolly-in, photorealistic, 35mm film, deep warm-to-blue color transition"

## Negative constraints
no people, no cars, no text change on signs, no camera shake, no new light sources, keep architecture static, no sky replacement flicker, preserve shadow edge as straight line

## Continuity notes
- 影界必须是直线(建筑投影),不是渐晕
- 壁灯亮起顺序:左(f212)先、右(f236)后,间隔 0.8s
- 招牌在夜态是暗的(无内打光)
- AI 只负责表面丰富度(灰泥剥落/木纹/涂鸦/街道污渍/大气),**空间结构/机位/光照方向以 control passes 为准**
