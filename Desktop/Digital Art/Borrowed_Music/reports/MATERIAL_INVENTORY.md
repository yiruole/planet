# Borrowed Music — 素材清单(STAGE 1,2026-07-08)

## 可直接使用

| 素材 | 路径 | 用途 | 状态 |
|---|---|---|---|
| 火星夜景参考(IG 屏录,Curiosity+银河) | `test/space.mov` | **SHOT 01 的 look 目标**:黑暗地表+漫游车+巨大星空,气质完全吻合 | 参考用(UI 污染,不能当 footage);中央裁切可做 lookboard |
| Komet《plus》音轨 | `test/results/phase4/sound.wav` | 临时"借来的音乐"备选(52% 静默、冷、克制,气质符合);特征曲线已有(features.npz) | 版权曲——**只做 temp**,成片需原创/授权 |
| 幼鱼 sonification 合成音 | `test/results/phase7/creature_sonified.wav` | 触碰声/环境声的颗粒来源备选 | 自有,可自由用 |
| 声音特征提取器 | `phase4/analyze_sound.py` | 对白/音乐时序对齐分析 | 复用 |
| 成像链合成器 | `phase6/comp_grade.py` | STAGE 3+ 合成端(暗部层次/grain/黑位) | 复用 |
| passes 材质覆盖法 | `phase6/build_corner_shot.py` | STAGE 3+ control passes | 复用 |
| 街角照片 | `test/2.imagetovideo.JPG` | 无关本片 | — |

## 本地 3D 资产盘点
- `blender/snow_flash_test/snow_scene.blend` — 雪夜场景(暗调地表+天空结构可参考,资产不直接复用)
- `blender/waterring/*.blend` — 无关
- **无** 宇航员/漫游车/居住舱/衣柜模型;**无** 星空 HDRI(仅一张海滩 exr,气质不符)
- → animatic 全部走 proxy(允许);hero 阶段资产缺口见 ASSET_GAPS.md

## 声音资产盘点
- 对白:无录音 → temp 用 macOS `say`(Tingting 中文语音,明确标记 TEMP)
- 环境声/触碰声:无库 → numpy 合成(temp),幼鱼 wav 可采颗粒
- 借来的音乐:temp 用 numpy 稀疏旋律(缺音可精确控制)或 Komet 片段

## 原素材保护
test/ 全部只读;所有产物进 `Borrowed_Music/`。
