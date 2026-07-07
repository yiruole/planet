---
name: creative-intelligence-system
description: "用户的长期创作智能系统(数字艺术/实验影像/电影),架构、已建 Skills、实施阶段与原则"
metadata: 
  node_type: memory
  type: project
  originSessionId: 7663ac50-e167-4172-b5f4-270b59d5a3dc
---

用户(数字艺术家/实验影像创作者)委托建立长期 Creative Intelligence System,我担任首席工程师/技术导演。架构四层:Skills(分析/推理/规划)→ Local Tools(媒体处理)→ MCP/Bridge(操作 DCC)→ Creative Memory(远期素材记忆)。

截至 2026-07-07 已完成:
- PHASE 0 审计:fxhoudini/blender/touchdesigner/playwright 四个 MCP 全通;Houdini 20.5.487 + Blender 5.1.2 + TD 2025.31550 + AE 2025(AE 无自动化通道);ffmpeg 8.1.1(**无 drawtext 滤镜**)、yt-dlp;anaconda python 是 x86_64 Rosetta(装 ML 库需另建 arm64 环境);无 opencv/torch
- PHASE 1:`~/.claude/skills/creative-rules/`(evidence/iteration/media 三个规则文件)
- PHASE 2:`~/.claude/skills/reference-reverse-engineer/`(SKILL.md + scripts/media_inspect.py + examples/),已用真实视频端到端验证并 git commit

- PHASE 3(2026-07-07 完成):houdini/blender/touchdesigner effect-builder + footage-transform-lab 四个 skill,全部案例驱动并实测(水环无头冒烟、TD 桥检查、motion_trace 242帧端到端)。TD 失败记录从 git 历史恢复(`git show eef4e80:Desktop/TD/PROGRESS.md` 有 10 条踩坑表)。

- PHASE 4(2026-07-07):压力测试(雪夜闪光状态切换)完整闭环,案例文档 `examples/snow-flash-state-flip.md`
- PHASE 5(2026-07-07):**fidelity loop v1**——复盘发现系统只有机制关没有保真关、迭代被最便宜修正路径俘获。落地:`creative-rules/fidelity-rules.md`(双关卡验收、每轮最大3差距+来源分类A–I、修正路由约束、豁免台账)+ `creative-rules/scripts/compare_fidelity.py`(证据面板,不打分:图像=直方图/边缘/分块密度,视频=时序亮度曲线+事件时刻)。回归验证:暴露了人工三轮都没抓到的闪光时机偏晚0.3s、暗态过暗3倍。

- PHASE 6 / 校准测试1(2026-07-07 完成):backrooms audio-relight 全链盲测闭环(小红书参考,页面文案当隐藏答案)。机制逆向四步全中;真实管线 Blender 光层→TD 分频混合(hybrid)。暴露并已反写:①面板盲区(资产语义/拓扑/尺度分布/接触/遮挡/材质谱系→人工checklist+盲区配额+proxy升级票据,进 fidelity-rules)②route_to_skill 单值缺陷→有序数组+stage_gates(进 reference-reverse-engineer)③TD 工程五坑:乱序scrub采样不可信/lag release 延迟/project.save 回调死锁/惰性求值/录制走图像序列(进 touchdesigner-effect-builder)。案例私参在 `~/Desktop/Digital Art/reverse/xhs_test1/CASE.md`。**测试2(fidelity 盲区:色彩/运动为魂)待用户给素材;场景升级轮(settle+bevel+材质方差)待用户决定**。

- PHASE 7-总测试(2026-07-08 完成,一次连跑 8 阶段):AE 双测试(video2 living-painting 位移场静/动两版+稳像曝光锁;video1 人脸手风琴 2.5D 面片)→ 空间重建(画室 blocking;判读:space.mov 是 IG 屏录非空间素材、bottle mp4 是 app 成品非原始扫描)→ 声驱空间(Komet glitch→光呼吸/瓶敲击/相机凑近,52% 静默保留)→ previs《最后一格阳光》(街角照片+照片态 animatic)→ Blender→AI→合成街角镜头(control passes 材质覆盖法、AI handoff package 未假装执行)→ 黑水幼鱼 sonification。新建 7 个 skill:spatial-capture-reconstruction / sound-image-system / film-development-previs / hybrid-cg-ai-cinematography / image-to-video-director / after-effects-compositor / physical-phenomena-sonification。**系统六文档在 `~/Desktop/Digital Art/SYSTEM/`**(SYSTEM_MAP/SKILL_REGISTRY/VERIFIED_CAPABILITIES/KNOWN_LIMITATIONS/MATERIAL_CAPTURE_GUIDE/NEXT_PROJECTS)。三大能力缺口:ML segmentation(无 arm64 torch)、COLMAP/GS(无 CUDA)、AE 自动化桥。

推送:home 仓库 push 到 github.com/yiruole/planet 需走 ClashX 代理,**实测可靠形式是环境变量** `https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890 git push`(`git -c http.proxy=...` 2026-07-07 实测失效,症状 SSL_ERROR_SYSCALL 像直连被重置);代理节点对 GitHub 偶发抽风,先 `curl -x http://127.0.0.1:7890 -sI https://github.com` 探通再推。直连超时。

后续:AE compositor 待 ExtendScript 通道;ML 视觉工具(flow/depth)按需引入;snow_flash 保真升级(树资产/曝光/时序修正)待用户决定。

核心原则(用户明确要求):审计优先、复用已有 MCP/Bridge、最小端到端闭环、真实素材测试、OBSERVED/INFERred/UNKNOWN 证据分级、字幕≠看视频、不过度工程化、不建空架构、关键节点 git commit、设想不合理要直说。远期黑洞警告:素材记忆系统和 ML 视觉工具链按需引入,勿早做。

相关:[[peony-bloom-v5-project]](首个完整案例)、[[liquid-chrome-project]]
