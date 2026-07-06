---
name: reference-reverse-engineer
description: 逆向分析视觉参考(图片/截图/视频/YouTube/小红书链接/网页/教程/节点图),判断技术结构,输出 OBSERVED/INFERRED/UNKNOWN 三级分析、候选 pipeline 对比和最小复现实验,并路由到专项软件 Skill。触发词:复刻、逆向、这个效果怎么做、分析这个视频/图/参考、reverse engineer。
---

# Reference Reverse Engineer

跨软件视觉逆向总入口。**只负责分析和路由,不负责执行**——执行交给专项 skill 或对应 MCP。

必读规则:`~/.claude/skills/creative-rules/`(evidence-rules / iteration-rules / media-rules)。

## 工作流

### 1. 素材获取(按输入类型)

| 输入 | 方法 |
|---|---|
| 本地图片/视频 | 直接用;视频进入第 2 步 |
| YouTube | `yt-dlp -f "bv*[height<=720]+ba/b" <url>` 下载到分析目录 |
| 小红书/微博等 | 先 curl 抓 og:video / og:image meta(带浏览器 UA);登录墙时用 playwright MCP;都失败则请用户提供截图/录屏 |
| 网页/教程 | WebFetch 抓文字 + playwright 截图 |
| 当前工程截图/节点图 | 直接读图 |

### 2. 视频结构化分析(不许只看字幕)

用本 skill 自带工具(纯 ffmpeg,无重依赖):

```bash
python3 ~/.claude/skills/reference-reverse-engineer/scripts/media_inspect.py <video> [--outdir DIR] [--scene-threshold 0.3] [--grid 4x4]
```

产物(默认写到 `<video>_analysis/`):
- `metadata.json` — ffprobe 全量(时长/fps/分辨率/编码/码率)
- `shots.json` — 场景切换时间码(ffmpeg scene filter)
- `contact_sheet.jpg` — 覆盖全片的均匀采样网格(看时间演变)
- `frames/` — 每个 shot 的代表帧 PNG(逐帧细看)

然后**逐张读图观察**,记录到分析笔记。短视频(<30s)至少看 contact sheet + 全部代表帧;长视频先看 contact sheet 定位关键段,再对关键段加密抽帧。

### 3. 分析维度

逐项过(无信息就标 UNKNOWN):composition / camera(机位、运动、焦距感)/ lens & perspective / motion(什么在动、驱动方式)/ geometry(建模 vs 程序化 vs 实拍)/ material(BRDF 特征、SSS、透明)/ lighting(光源数、方向、软硬、色温)/ simulation clues(物理正确性、噪波特征、循环)/ temporal structure(节奏、循环、剪辑)/ compositing(层、遮罩、混合痕迹)/ post(调色、颗粒、bloom、暗角)/ sound-image relation(若有声)/ likely pipeline。

### 4. 判别启发(积累中,遇新模式就补充)

- **3D 渲染 vs 实拍**:高光滚动是否符合物理、边缘是否过于干净、景深虚化形状、噪点类型(渲染噪 vs 传感器噪)
- **程序化 vs 手工**:重复元素是否有统计一致性(程序化=同分布随机,手工=刻意变化)
- **实时 vs 离线**:GI 质量、SSS、运动模糊、分辨率下的细节密度;TD/Unreal 风格 bloom 是实时特征
- **模拟 vs 关键帧**:次级运动(overshoot、波传播)、碰撞响应自然度
- **合成痕迹**:边缘 halo、颗粒不连续、透视不一致、光照方向矛盾

### 5. 输出(按 evidence-rules)

Markdown 报告 + 同目录 `analysis.json`:

```json
{
  "source": "path或url",
  "media": {"duration": 0, "fps": 0, "resolution": ""},
  "observed": [{"fact": "", "evidence": "帧号/时间码"}],
  "inferred": [{"claim": "", "basis": "", "confidence": "high|medium|low"}],
  "unknown": [""],
  "pipelines": [{"route": "", "tools": [""], "pros": [""], "cons": [""], "est_effort": ""}],
  "recommended": {"route": "", "reason": ""},
  "mvp": {"goal": "", "steps": [""], "success_criteria": ""},
  "route_to_skill": "houdini-effect-builder|blender-effect-builder|touchdesigner-effect-builder|footage-transform-lab|none"
}
```

### 6. 路由判断

- 程序化几何/模拟/生长/破碎 → Houdini(fxhoudini MCP 已通)
- 场景/摄像机/材质渲染/实拍+CG → Blender(blender MCP 已通,socket 9876)
- 实时/audio-reactive/feedback/glitch → TouchDesigner(touchdesigner MCP 已通)
- 处理已有 footage → footage-transform-lab(未建;先用 ffmpeg 手工)
- 合成/追踪/时间操作 → AE(暂无自动化通道,给手工步骤)
- 不确定 → 给 2–3 条路线让用户选

**不要因为某软件已装就强行用它。** 判断依据是效果的技术本质。

## 已验证案例(可参照)

- 液体水环(NeXus 风格)→ Blender GN:采样曲线+点转体积,`~/Desktop/Digital Art/water_ring_nexus_style.blend`
- 重瓣牡丹开花(RAWICE Digital Flower #013)→ Houdini Python SOP:分层花瓣+bloom_ease 时序,`~/Desktop/Digital Art/Houdini/bloom/`(详见其 PROGRESS.md)
