---
name: sound-image-system
description: 把声音变成画面/空间的驱动系统:声音特征提取(envelope/transient/频段/质心/重复结构/静默)→概念性映射设计(≤3 条主映射)→离线渲染或 TD 实时执行。触发词:声音驱动、audio reactive、声画、音乐可视化、sonic space、用这段声音驱动。
---

# Sound-Image System v0.1

前置:遵守 `~/.claude/skills/creative-rules/`。基于 Phase 4(Komet glitch 曲驱动画室空间)+ backrooms audio-relight 两案例实测。

## 0. 核心立场

**不是 beat-reactive 玩具**。映射必须有概念理由(声音变量为什么"应该"控制这个视觉变量),最多 3 条主映射,静默/延迟/不响应是设计的一部分——一首曲子 52% 是留白时,休止态就是作品的一半。

## 1. 声音特征提取(先分析再设计)

模板 `~/Desktop/Digital Art/test/results/phase4/analyze_sound.py`(numpy FFT,无重依赖):
- 特征帧率 = 目标视频 fps(30),hop=sr/fps,win 2048 hann
- **提取**:RMS 包络 / 低中高频段能量(20-200/200-2k/2k-10k)/ 谱通量→瞬态(自适应阈值:flux > 15帧滑动均值×1.8 且 >0.12)/ 频谱质心 / 静默比(RMS < max×0.06)/ 重复周期(通量包络自相关峰)
- 输出 features.npz(逐帧曲线)+ features.json(画像摘要)+ feature_panel.png(四联证据图)
- **先读画像再设计映射**:能量分布决定哪些频段值得映射(中频空就不映射中频);静默比决定休止态的分量;重复周期给时间结构

素材注意:屏录/视频里的音乐先 `ffmpeg -vn -ac 1 -ar 22050` 抽干净音轨;文件名与视觉内容不可信,音轨才是素材本体。

## 2. 映射设计纪律

- 每条映射写成"声音变量 → 视觉变量 + 概念理由"三元组,理由说不出口的映射砍掉
- 变量类型分工:**连续量**(频段能量/质心)→ 连续视觉参数(光强/色温/位置插值,要平滑窗);**离散事件**(瞬态)→ 冲量型响应(冲量×指数衰减核卷积,τ 3–8 帧,交替符号避免单向漂移)
- 响应曲线先在 numpy 里算好逐帧数值,再进 DCC 打关键帧——不要在 DCC 里实时算特征
- 静默段所有映射归零回休止态;休止态本身要能看(=静态版本)

## 3. 执行路线

| 场景 | 路线 |
|---|---|
| 离线高质量(3D 空间/材质/DOF) | **Blender**:features.npz → 逐帧 keyframe_insert → 渲染 → ffmpeg mux 原曲(实测 450 帧 EEVEE ≈15min) |
| 实时/演出/长时间生成 | **TD**:audiofilein→audiofilter 分频→analyze(rmspower)→lag(response lag2≤0.1s)→ opacity/参数表达式;阈值+闩锁做"保持"效果(见 touchdesigner-effect-builder) |
| 已有 footage 上加声驱效果 | footage-transform-lab(位移场幅度/换场率吃声音特征) |

## 4. 场景复用模式(Blender)

前置阶段的场景脚本按段执行复用:`exec(src.split("# --- camera")[0])` 取建场景部分,驱动层另写——场景与驱动解耦,同一空间可换任意曲目重驱动。驱动对象打包到 pivot empty(matrix_parent_inverse 保持世界位置)再对 pivot 打关键帧。

## 5. 验收(fidelity gate)

- **静态 vs 驱动对比**:同机位同帧号渲静态版(映射全零)与驱动版并排——差异必须一眼可读且发生在映射说好的变量上
- **声画对齐抽查**:挑 3 个瞬态时刻,视觉响应与音频事件差 ≤2 帧
- 休止段抽帧:必须真的静

## 6. 案例库

- **画室听音乐**(Phase 4 完整闭环):`~/Desktop/Digital Art/test/results/phase4/`(MAPPING.md 映射表 + analyze_sound.py + build_sound_space.py + 15s 成片)
- **backrooms audio-relight**(TD 实时路线):三段分频驱动光照层 opacity,`~/Desktop/Digital Art/reverse/xhs_test1/CASE.md`
