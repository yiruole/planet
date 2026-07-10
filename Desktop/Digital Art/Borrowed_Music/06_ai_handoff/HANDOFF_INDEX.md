# Borrowed Music — AI 视频生成输入包索引(2026-07-11)

来源:v02 生产时间轴(`02_blender/borrowed_music_production.blend`,708 帧 @24fps,640x360)。**所有分镜/机位/构图/角色位置/动作时序即最终答案,AI 只做视觉替换。**

## 每镜头内容(shot01–shot06 同构)

| 文件 | 说明 |
|---|---|
| `shotXX_proxy.mp4` | 灰盒预演动画,原始镜头时长,24fps——**Seedance 的运动参考** |
| `shotXX_first / _mid / _last.png` | 首/核心动作/末有效帧——风格化关键帧的底图(GPT/Nano Banana),Seedance 首尾帧引导 |
| `shotXX_q1 / _q3.png` | 仅 S03/S04(动作复杂):1/4 与 3/4 帧 |
| `shotXX_depth.png` | 深度图,**近亮远暗**,sqrt 非线性(近/远都可辨);量程:S01 45m / S02 8m / S03 5m / S04 6m / S05 40m / S06 35m;渲染于 first 帧,与 first.png 逐像素对齐 |
| `shotXX_masks/` | character / environment / music_garment / rover_props 四类硬遮罩(白=该类),first 帧,与 first.png 对齐 |
| `shotXX_notes.md` | 起止帧/时长/焦段/机位运动/动作时序/**不可改清单**/待替换清单/Seedance 运动指示 |

## 镜头总表

| Shot | 帧 | 时长 | 一句话 |
|---|---|---|---|
| 01 | 1–96 | 4.0s | 星球外景缓推居住舱(MOV 星壁参考) |
| 02 | 97–192 | 4.0s | 背影开衣柜,10 件音乐挂着 |
| 03 | 193–312 | 5.0s | 手臂五次触碰,停在深纱(触碰帧=声画锁定) |
| 04 | 313–504 | 8.0s | 两句对白;取纱→漂移→裹附侧翼 |
| 05 | 505–648 | 6.0s | 出舱走入黑暗,音乐轻起,漫游车振动一次 |
| 06 | 649–708 | 2.5s | 停下;异常剪影;f682 缺音暗沉 |

## 建议工作流
1. GPT/Nano Banana:以 `first.png` 为构图底 + notes 的"不可改清单"做约束,生成风格化关键帧(参考 `../reports/AI_HANDOFF.md` 的 prompt/negative;整体气质:冷/克制/低饱和/大量黑暗)
2. Seedance:风格化 first(+last)帧作首尾引导,`proxy.mp4` 作运动/时长参考,notes 的"中间运动"段落作运动 prompt
3. 回填:生成片段交回本管线做统一分级(老电影幻梦版配方 `02_blender/comp_v03.py`)与声画同步验收(触碰/振动/缺音帧号见 notes)

## 素材授权
- `01_assets/eso_milkyway_clean.jpg`:ESO/S. Brunier,CC BY 4.0(星空底图)
- `01_assets/moonless_golf_4k.hdr`:Poly Haven,CC0(备用夜空)
- 外太空 MOV:IG 屏录,**仅作 look/速度参考,不得直接进成片**

## 全片交叉参照
`contact_sheet_all_shots.png`(6 镜头 × 首/中/末);声画同步帧总表见 `../reports/SHOT_ASSET_MAP.md`;temp 声轨 `../04_sound/temp_mix.wav`(对白/触碰/缺音时刻可听)。
