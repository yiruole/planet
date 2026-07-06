---
name: houdini-effect-builder
description: 在 Houdini 中搭建视觉效果(程序化几何/生长开花/粒子/模拟/VDB/程序化动画)。接收 reference-reverse-engineer 的路由或直接的 Houdini 制作需求,通过 fxhoudini MCP 执行:规划节点网络→原子化搭建→参数调优→渲染验证→迭代。触发词:用 Houdini 做/复刻、Houdini 效果、程序化生成、SOP/VEX/VDB/模拟。
---

# Houdini Effect Builder

前置:遵守 `~/.claude/skills/creative-rules/`(证据分级/迭代验证/媒体纪律)。分析参考交给 reference-reverse-engineer;本 skill 只负责**在 Houdini 里把效果做出来**。

## 0. 连接检查

先 `get_houdini_connection_status`。失败时按序排查:① Houdini 是否运行 ② 端口 8100 是否监听(`lsof -nP -iTCP:8100`)③ 桥接插件 package 是否加载——路径配置在 `~/Library/Preferences/houdini/20.5/packages/fxhoudinimcp.json`,指向 `Digital Art old/.../fxhoudinimcp/houdini`(**该文件夹不可移动**)。不重启的临时启动法:Houdini Python Shell 里 `sys.path.insert` 后 `fxhoudinimcp_server.startup.ensure_running()`。

## 1. 视觉特征 → 技术路线(实测案例支撑)

| 视觉特征 | 路线 | 依据案例 |
|---|---|---|
| 有机分层结构、逐层时序动画(花开/生长/展开) | **Python SOP 程序化生成**,形态逻辑写成代码,时序用缓动函数驱动 | 牡丹 bloom |
| 形态规则可参数化但节点表达繁琐(嵌套循环、逐元素个性化) | Python SOP > 纯节点;节点只做后处理(细分/法线/材质) | 牡丹:8 层×百余花瓣逐瓣抖动,节点网络不可维护 |
| 液体沿路径/粒子流动+融合表面 | POP + curve force → VDB from particles → convert;**若要实时预览且逻辑简单,考虑让路给 Blender GN**(水环案例:采样曲线+Points to Volume 在 GN 里 20 个节点解决) | 水环 |
| 实时反馈/audio-reactive/材质流动 | 让路给 TouchDesigner | liquid chrome |
| 烟/云/爆炸/大规模模拟、破碎、复杂物理 | Houdini 独占:pyro/RBD/vellum/FLIP(用 setup_*_sim 工具起步) | — |

**判断原则**:Houdini 赢在"逻辑复杂度"和"模拟规模",不赢在"快速出一个简单效果"。简单效果先想 Blender/TD。

## 2. 搭建纪律(fxhoudini MCP)

1. **整图规划后一次提交**:3+ 节点用 `build_network`;新节点类型先 `dry_run=True` 验证(自带 did-you-mean 纠错)
2. **不猜参数名**:不熟的节点先 `get_node_card(node_type)`;概念查 `search_help`。猜参数名是静默坏网络的头号原因
3. **搭完必验**:`verify_network(parent)` 看 error_nodes 和几何计数;视觉里程碑 `render_viewport` 或渲一帧,**看图再下结论**
4. Python SOP 源码**放 .py 文件**(与 hip 同目录),用 `execute_python` 读文件写入 `python` parm——改代码后重载即生效,且可 git 管理
5. `execute_python` 只用于无专用工具的场景(文件→parm 装载、look-at 矩阵、ROP 参数探测),justification 写清楚
6. 可调参数集中暴露(CTRL null + 通道引用),别埋硬编码
7. 阶段成果落 filecache / save_scene;**save_scene 可能 60s 超时,超时后先查文件 mtime 再重试**

## 3. 参数启发式(全部实测)

**几何**
- 位移细节(叶脉/棱)要扛住 1 次 Catmull-Clark 细分:深度 ≥ 0.055–0.09 × 元素 scale;subdivide 1 次为上限,2 次会磨平
- 程序化随机:时序抖动 ±0.06、倾角 ±8°、半径 ±12% 是"自然而不乱"的量级起点
- 缓动:生物性展开用"先快弹后慢展"(前 18% 时间完成 42% 行程,尾段 2.8 次幂缓出)
- ⚠️ Python 里 `(1-s)**小数幂` 的 s 必须 clamp [0,1]:浮点误差令 s 微超 1 → 负底数小数幂 → 复数 → cook 崩溃

**材质/灯光(Karma + principledshader)**
- SSS ≤ 0.35,否则点色 Cd 被冲灰;透光感靠背面轮廓光而非加大 SSS
- 点色驱动:`basecolor_usePointColor=1`;颜色对比写进 Cd 比调材质快
- 三灯起步:暖主光(强,单侧)+ 冷补光(≤主光 5%)+ 轮廓光;黑背景下透明/SSS 材质必须有亮环境或强轮廓光才能被看见
- 摄像机先查 `get_bounding_box`,放在 2–3× bbox 半径处再 look-at,否则容易钻进几何内部

**渲染(本机 M3 参考)**
- 960×540/16smp ≈ 7min/帧;9smp ≈ 3–4min;640×360/9smp ≈ 1–2.5min。草稿一律 9smp 以下
- Karma ROP 的 `rop.render()` **立即返回**,husk 后台跑:`pgrep husk` 轮询,文件出现且 husk 退出才算完成;无错误+无文件 = 还在渲,不是失败
- 序列渲染用独立 hython(不冻结 GUI、不受会话超时限制):`nohup hython render_script.py > log 2>&1 &`;脚本模板见案例库
- ROP 参数名随版本变,用 hasattr/parm() 探测再设(camera/picture/resolutionx/samplesperpixel)

## 4. MVP 与迭代

- 首版:低细分、少元素、9smp 单帧,先验证形态和构图
- 动画:只渲 **首/中/末 3 帧**验证时序,不渲整段
- 每轮迭代改动 ≤3 个变量,渲同机位对比帧,与参考并排逐项检查(构图/颜色/材质/运动/层次)
- 完整序列渲染是**最后一步**且必须用户确认成本(给出档位×时长估算)

## 5. 失败模式速查

| 症状 | 原因 | 修法 |
|---|---|---|
| Python SOP cook 崩溃 `new_Vector3 double` | 坐标里混进复数(负底数小数幂) | clamp 幂运算底数;setPosition 包 float() 定位 |
| 渲染图漆黑/材质像塑料 | 透明/SSS 材质 + 环境太暗 | 提亮 world/加轮廓光,再调材质 |
| 位移细节渲染后消失 | 细分磨平 | 加深位移或减细分次数 |
| 渲染无输出无报错 | husk 仍在后台 | pgrep husk 轮询;等进程退出 |
| 镜头里全是网格大块 | 相机在几何内部 | 查 bbox,拉到 2–3× 半径 |
| save_scene 超时 | 保存时重 cook | 查 mtime,重试一次 |

## 6. 案例库

- **牡丹开花**(完整闭环):`~/Desktop/Digital Art/Houdini/bloom/`,进度文档 PROGRESS.md,逆向分析见 `../reference-reverse-engineer/examples/rawice-digital-flower-013.md`
- 对照反例:水环选择 Blender GN 的理由(工程文件 `~/Desktop/Digital Art/blender/waterring/`)
