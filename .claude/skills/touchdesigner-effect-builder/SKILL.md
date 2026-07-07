---
name: touchdesigner-effect-builder
description: 在 TouchDesigner 中搭建实时视觉效果(feedback/displace/glitch/audio-reactive/GLSL/生成式动画/实时交互)。接收 reference-reverse-engineer 路由或直接的 TD 需求,通过 touchdesigner MCP 执行:规划 OP 网络→构建→调参→截图验证→迭代。触发词:用 TD/TouchDesigner 做、实时效果、audio reactive、feedback、glitch。
---

# TouchDesigner Effect Builder v0.1

前置:遵守 `~/.claude/skills/creative-rules/`。基于魔方全息项目(NewProject.19)与 liquid chrome 案例实测提炼。本机 TD 2025.31550。

## 0. 连接方式

1. **touchdesigner MCP**(已注册,`mcp__touchdesigner__td_*`:td_health/td_connect/td_create_op/td_set_par/td_eval/td_exec 等)——先 `td_health` 检查
2. **HTTP 后备**(MCP 连不上时,已实测):`POST localhost:9980/mcp`,payload `{"action":"exec|eval|health|...","args":{...}}`,**JSON 里不能有裸换行**(代码要 `\n` 转义)
3. TD 端需要 bridge 组件在工程里运行;bridge 实体在 `Digital Art old/universe drive/touchdesigner-mcp/`(**不可移动**);带桥工程可 `open -a TouchDesigner <toe>` 启动,~15-45s 后 9980 起

**成像管线配方(backrooms 实测,复刻"拍出来的"质感)**:mix → HALO(level blacklevel 0.72→blur 34→level 0.5→add)→ SOFT(blur 2.0,吃掉 CG 锐边)→ CHROMA(彩色 noise add 0.035,色度噪声)→ TONE(level outlow 0.03–0.045 抬黑位 + inhigh 0.96 高光滚降)→ GRAIN(mono noise add 0.06)→ HSV(hueoffset 微调色偏)。顺序重要:halation 在软化前,grain 在最后。

**桥使用纪律(backrooms audio-relight 实测)**:
- 桥会**空闲挂死**(idle 数十分钟后 health 超时,TD 进程还活着;疑 App Nap)。长流程每步前查 health;挂死即走恢复流程,别调试
- 恢复流程标准化的前提:**所有构建/修正脚本编号存盘(c1…fixN),全部幂等**,恢复 = 重启 TD + 顺序重放,30 秒内回到现场
- 多行代码经桥易碎:脚本写盘,桥内只执行单行 `exec(open('/abs/path.py').read())`;结果写 JSON 文件落盘再从外部读,不依赖桥返回值
- 桥的 exec 是 `exec(code, globals(), locals())`:**推导式 body 看不到 exec 局部变量**(Python 作用域),`{n: f(c) for n in xs}` 报 `name 'c' is not defined`——一律用普通 for 循环
- **`project.save()` 在桥回调内死锁**(主循环被回调占用)。构建全部写成**幂等可重放脚本**(开头 destroy 再 create),保存交给用户或接受"崩了重放"
- 桥挂死恢复:`pkill -9 -x TouchDesigner` → 重开带桥 .toe → 顺序重放构建脚本

## 1. TOP / CHOP / SOP / COMP 路线判断

| 需求 | 家族 | 依据 |
|---|---|---|
| 像素级效果(调色/glitch/扫描线/晕影/合成) | TOP,复杂逻辑直接写 GLSL TOP | 魔方:背景/扫描栏/全息 grade 全是 GLSL TOP |
| 时间驱动/随机触发/参数动画 | CHOP(Noise CHOP + 表达式引用) | 魔方:相机抽搐/glitch/字幕闪现全靠 sparse Noise CHOP |
| 3D 几何/实例化 | SOP + GLSL MAT(几何逻辑重的考虑让路 Houdini) | 魔方 27 cubie 用 vertex shader 按 `gl_VertexID/顶点数` 识别,别用位置(变换后坐标乱) |
| 网络组织/复用 | COMP;渲染链 Render TOP → 后处理 TOP 串 → 输出 | — |

**GLSL 优先原则**:3 个以上原生 TOP 串联能被 1 个 pixel shader 替代时,写 GLSL(可控、快、参数集中)。CHOP 负责"何时/多少",TOP/GLSL 负责"什么样"。

## 2. 效果使用边界(避免画面脏的核心)

- **bloom**:`maxRadius < 0.1`(实测 1.0 会把任何形状糊成圆);bloom 只点缀高光——先关 bloom 调对光比和对比度,最后再开
- **noise**:每层噪波必须说得出负责的尺度(背景颗粒/几何抖动/时间触发是三件事,别用一个 noise 全包);sparse 型用于"偶发事件",hermite 用于连续漂移
- **feedback**:衰减 <0.97,否则画面积累发白;feedback 内容要有运动才有意义
- **材质单一**→ 用亮度→色相映射(gradient grade)加层次:魔方案例的 hologram_grade 就是亮度分 5 档映射不同色温
- **画面脏**→ 检查:黑位是否压住(背景别用纯灰)、发光元素数量(≤3 个视觉焦点)、glitch 频率(偶发才有效,常驻就是噪音)

## 3. 参数启发式(魔方项目实测)

- 相机轨道:0.3 rad/s 是"缓慢观察"量级;抽搐 ±1.2 单位、sparse noise 驱动
- 偶发事件频率:0.8s 换一次 + 15% 概率 ≈ "病理感";更高频率变成杂乱
- 半透明几何:`srcblend='sa', destblend='omsa', depthwriting=False` 三件套,缺一渲染错
- 穿入几何内部:`near clip 0.02` + MAT `cullface='neither'`
- Text TOP:必须 `outputresolution='custom'` 显式设分辨率 + `fontsizexunit='pixels'`(points 单位小到不可见);叠字幕用 Composite **add** 模式(不依赖 alpha)
- Composite 'over':**Input 0 = 前景,Input 1 = 背景**(反了就是黑屏或只见背景)

## 4. MVP 与迭代

首版:静态网络 + 单一运动源,截图确认构图;逐个开启效果层(每次 1 层),每层截图对比;audio-reactive 最后接(先用 LFO/Noise 模拟驱动信号调好视觉,再换真音频)。

## 5. 失败修正表(全部实测)

| 症状 | 原因 | 修法 |
|---|---|---|
| 形状全部变圆/糊 | bloom maxRadius 过大 | 降到 <0.1 |
| 录制的 mov 是空的/1帧/不出文件 | `record=True` toggle 不写帧;批量场景下 addframe.pulse()+强制 cook 也不可靠(backrooms 实测) | **首选逐帧 `op('OUT').save('f%05d.jpg' % f)` + ffmpeg 合成**(自带强制 cook;1260 帧实测 15s);moviefileout 只用于实时播放录制 |
| 乱序 scrub 采样 CHOP 值不可信 | lag/analyze 等 timesliced CHOP **有状态**,值依赖 cook 历史,同一帧三次读出三个值 | 校准/统计采样必须从帧 1 顺序步进;乱序 scrub 得到的统计直接作废 |
| 声画响应慢半拍(约 5-10 帧系统延迟) | lag CHOP 的 release(lag2)把响应质心整体后移 | 响应型信号 lag2 ≤0.1s;要"亮灯保持"效果用阈值后闩锁(threshold→hold),别靠大 release 硬拖 |
| 批量导出全是同一帧/画面不动 | TD 惰性求值,无 viewer 拉动就不 cook | 逐帧导出用 TOP.save(强制 cook);读 CHOP 值本身也会触发 cook |
| GLSL TOP 里时间不动 | GLSL TOP 无 TDTime uniform | 自建 uniform,`me.time.seconds` 经 vec 传入 |
| 文字看不见 | Text TOP 默认分辨率/points 字号 | custom 分辨率 + pixels 单位字号;add 模式合成 |
| 透明物体渲染成实心/黑块 | blend/depth 设置不全 | sa/omsa/depthwriting=False 三件套 |
| 逐元素识别错乱 | 用位置判断元素 | 用 `gl_VertexID / 每元素顶点数` |
| render 背景参数无效 | 参数名记错 | 是 `par.bgcolora`(不是 bgcoloralpha) |
| bridge JSON 报错 | 代码含裸换行 | 全部 `\n` 转义后再发 |

## 6. 边界:什么时候不用 TD

- 高质量离线渲染(SSS/GI/微距 DOF)→ **Houdini/Blender**(TD 是实时管线,画质天花板低)
- 重几何程序化(生长/破碎/大量个性化元素)→ **Houdini**
- 场景/摄像机/实拍混合的"电影帧" → **Blender**
- 精细合成/roto/tracking → **AE**
- TD 赢面:实时反馈回路、音频驱动、交互输入、长时间运行的生成系统、现场演出

## 7. 案例库

- **魔方全息**(完整闭环,含 30s 录制):工程与 GLSL 源码记录在 git 历史 `Desktop/TD/PROGRESS.md`(文件已删但 `git show eef4e80:Desktop/TD/PROGRESS.md` 可取);录制成品 rubik_hologram_30s.mov
- **liquid chrome**:`~/Desktop/Digital Art/TD/transball/liquid_chrome.toe`(REGEN.Prod 复刻)
- **backrooms audio-relight**(hybrid:Blender 光层底板 × TD 分频混合,测试1完整闭环):工程 `~/Desktop/Digital Art/reverse/xhs_test1/audio_relight.toe`,幂等构建脚本 td_c1/c2/c3.py,全程与私有参数见同目录 CASE.md
