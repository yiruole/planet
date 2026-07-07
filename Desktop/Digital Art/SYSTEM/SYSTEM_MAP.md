# Creative Intelligence System — SYSTEM MAP(2026-07-08)

## 四层架构
```
Skills(分析/路由/配方)→ Local Tools(ffmpeg/numpy/scipy 脚本)→ MCP/Bridge(操作 DCC)→ Creative Memory(~/.claude memory + 案例文档)
```

## 创作流(四条主链,全部实测)
```
参考 → 复刻   reference-reverse-engineer → [houdini|blender|touchdesigner]-effect-builder / footage-transform-lab → fidelity-rules 双关卡
现实 → 重建   spatial-capture-reconstruction → blender-effect-builder → (下游任意链)
声音 → 画面   sound-image-system → Blender 离线 / TD 实时;物理现象反向:physical-phenomena-sonification(画面→声音)
剧情 → 镜头   film-development-previs → hybrid-cg-ai-cinematography(Blender 真值→AI 表面→合成)→ after-effects-compositor
```

## Skills 目录(~/.claude/skills/)
- `creative-rules/` — 共享规则:evidence / iteration / media / **fidelity-rules**(双关卡+盲区配额+镜头形成链)+ `scripts/compare_fidelity.py`
- `reference-reverse-engineer/` — 逆向总入口 + `scripts/media_inspect.py`
- `houdini-effect-builder/` `blender-effect-builder/` `touchdesigner-effect-builder/` — DCC 执行
- `footage-transform-lab/` — 素材变换(motion trace / 位移场 / 2.5D 面片 / 稳像跟踪)
- `spatial-capture-reconstruction/` — 扫描质检/路线判断/blocking 重建/重拍协议
- `sound-image-system/` — 声音特征→概念映射→驱动
- `film-development-previs/` — 概念→shot list→照片态 animatic
- `hybrid-cg-ai-cinematography/` — Blender→AI→合成分工 + control passes + handoff
- `image-to-video-director/` — 单图承载力分析→运动设计
- `after-effects-compositor/` — 合成职能路由 + 成像链配方
- `physical-phenomena-sonification/` — 现象→结构变量→声音

## 工作区
- `~/Desktop/Digital Art/AE/video1|video2/results/` — footage 双测试成果
- `~/Desktop/Digital Art/test/results/phase3–7/` — 总测试成果(每阶段自含:脚本+文档+可看成品)
- `~/Desktop/Digital Art/reverse/xhs_test1/` — backrooms 案例(用户已移动,git 历史有全量)
- `~/Desktop/Digital Art/blender|Houdini|TD/` — 各 DCC 工程
- 本目录 `SYSTEM/` — 系统级六文档

## 通道状态
Houdini(fxhoudini MCP)✅ / Blender(MCP+socket 9876+无头脚本)✅ / TD(MCP+HTTP 9980,注意空闲挂死)✅ / AE ⛔ 无自动化 / AI 生成服务 ⛔ 未接入
