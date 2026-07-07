---
name: film-development-previs
description: 把概念/梦/剧情/一张照片/一段声音发展成电影镜头设计:motif→visual grammar→temporal grammar→camera logic→sound-image plan→shot list→storyboard→animatic/previs。触发词:previs、预演、分镜、把这个概念做成镜头、镜头设计、storyboard、animatic。
---

# Film Development & Previs v0.1

前置:遵守 `~/.claude/skills/creative-rules/`。基于《最后一格阳光》案例(单照片+glitch 曲 → 12s animatic)实测。**不写三幕剧模板**——从素材真相出发长出结构。

## 1. 开发链(顺序固定,每步一句话就够)

1. **素材真相盘点**:手里真有什么(照片/声音/空间/参考),各自的身份是什么——素材不足时概念必须缩到素材撑得住的尺寸
2. **Motif**(一个,不要三个):画面里反复出现、可被拍摄的具体物(光斑/边界线/封板),不是抽象主题词
3. **Visual grammar**:2–3 条构图/色彩法则(如"光影边界永远是画面最强线""色彩两极不过渡")
4. **Temporal grammar**:时间如何流动(压缩比/匀速 vs 加速/状态翻转点在哪一帧级别)
5. **Camera logic**:运动预算分配——光在动就锁机位,机器动就光不动;插入镜头用焦段裁切还是移机,写明理由
6. **Sound-image plan**:声音的静默段与画面的哪个状态对齐;瞬态归谁(复用 sound-image-system 特征分析)
7. **Shot list 表格**:shot/时长/内容/机位镜头/光照状态,8–15s 控制在 2–4 个镜头
8. **Lighting states**:每个状态给可执行参数(色温/角度/stop 差/光池半径)

## 2. Previs 三条路线(按素材选,不按野心选)

| 素材 | 路线 | 成本 |
|---|---|---|
| 有高质量场景照片 | **照片态 animatic**(实测):同一照片做 N 个光照态分级(numpy:分区增益+色温矩阵),状态间用几何 mask 扫掠/光池渐亮衔接,ffmpeg 混音轨 | 分钟级 |
| 有 Blender blocking 场景(Phase 3 类) | 机位+光照关键帧渲 previs(灰模即可) | 小时内 |
| 都没有 | 纯 shot list + 手绘级站位图,不硬造画面 | — |

**照片态 animatic 配方**(《最后一格阳光》实测):
- 光照态 = 全图增益 × 通道色偏(夜:×0.16 + B×1.45 R×0.72);别用曲线,previs 层面粗分级更快更稳
- 影子爬行 = 对角坐标场 `(x/W + 1-y/H)` 阈值扫掠 + 0.05–0.08 软边,日态/暮态按 mask 混合
- 灯光醒来 = 灯位高斯 glow(exp(-d²/r²))× 暖色 × 渐亮包络;多盏灯错峰(0.8s)有生命感
- 瞬态闪烁 = 冲量×指数衰减核(τ≈2帧),偶发负冲量(掉电)比正冲量更"电流不稳"

## 3. 纪律

- storyboard 帧从 animatic 里抽,不单独画——保证分镜与动态一致
- 每个 shot 的光照状态必须能在 Lighting states 表里找到参数,previs 不许出现"到时候再说"的光
- 概念文档 ≤1 页;交付物:CONCEPT.md + sb_*.jpg + animatic mp4(带声)
- 下游:进 Phase 6 类管线时,shot list 的机位/焦段/光照态直接变成 Blender 相机与灯光设定

## 4. 案例库

- **《最后一格阳光》**(完整闭环):`~/Desktop/Digital Art/test/results/phase5/`(CONCEPT.md + make_animatic.py + animatic_12s.mp4);单张街角照片+Komet glitch 曲 → motif"光的撤离"→ 3 镜头 12s;照片态 previs 配方源于此
