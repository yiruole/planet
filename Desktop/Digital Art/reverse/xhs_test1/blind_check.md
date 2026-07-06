# Blind-check:独立逆向 vs 页面公布的工作流

**日期**:2026-07-07 · 压力测试1(模糊路由+TD全闭环)
**协议**:analysis.json 先锁定,后读页面文案。

## 隐藏答案(页面 description,作者 @by__nils 作品的转发说明)

> ① #blender 搭场景,建好灯光分组
> ② 渲染成多层图像,每组灯光单独一层
> ③ 导入 #touchdesigner,用音频分析节点分离高频/中频/低频
> ④ 把不同频段的音频信号映射到灯光强度,随机闪烁天花板的灯

## 逐条比对

| # | 真实工作流 | 我的独立判断 | 判定 |
|---|---|---|---|
| ① | Blender 搭场景+灯光分组 | INFERRED high:"底板在 Blender 渲染为按光源拆分的 render layers" | ✅ 对 |
| ② | 每组灯光单独渲染一层(静帧) | INFERRED medium:"底板是静帧(非序列)" | ✅ 对 |
| ③ | TD 音频分析分离高/中/低频 | INFERRED high:"audiofilein→分频/包络";但频段划分细节我放进了 UNKNOWN | ✅ 对(粒度略保守) |
| ④ | 频段信号→灯光强度 + 随机闪烁 | INFERRED high:"math 映射各层 opacity + noise CHOP 随机分量" | ✅ 对 |
| 路由 | Blender→TD 混合管线 | recommended A + route_note 指明混合;route_to_skill 填 touchdesigner-effect-builder | ✅ 对 |

## 路由哪里对、哪里错、为什么

**对的**:
- 机制四步全部命中,无一条 INFERRED 被证伪。关键一步是把节点图当第一证据源(TD 节点名、"Blender render layers" 框标题、noise→math→switch 拓扑),而不是猜。
- 声画相关性检验(corr 0.51, lag≤3帧)独立于文案证实了"音频驱动"。

**必须诚实记录的局限**:
1. **本案路由其实不模糊**——视频自带 breakdown(下半屏就是节点图)。测试想压的"两难路由"没有真正发生;命中率高部分归功于作者把答案画在了画面里。选材教训:纯效果视频(无 breakdown)才能真正压路由。
2. **route_to_skill 单值字段表达不了混合管线**——真实答案是 blender(底板)→TD(机制核心),我只能塞进 route_note 文字说明。这是 schema 级缺陷,属于可反写的普遍性问题。
3. 频段划分(高/中/低三段)这个粒度我标了 UNKNOWN,答案里有——判断正确但偏保守;三段分频是 audio-reactive 的行业默认,可作为 INFERRED medium 而非 UNKNOWN。

## 对执行阶段的指导

按答案确认的管线执行:Blender 灯光分组渲染静帧层 → TD 三段分频驱动层混合 + noise 随机闪烁 → TD 后期(LENS_DIRT/GRAIN/HSV_ADJUST 参照视频节点名)。
