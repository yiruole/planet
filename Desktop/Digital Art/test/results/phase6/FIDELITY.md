# Phase 6 — fidelity report(2026-07-08)

## 交付链完成度
script/概念(Phase 5 previs)→ shot interpretation → Blender blocking(空间真值/机位/三光照态)→ control passes(depth/normal/4 masks × 3 关键帧)→ AI handoff package(完整,未假装执行)→ 合成端成像链 → 10s 成片 final_shot_10s.mp4。

## 分工执行情况
- **Blender(空间真值)**:✅ 双立面街角、拱门节奏、招牌/灯柱/壁灯地标、对角影界(遮挡楼投影)、推近机位、GOLD→DUSK→NIGHT 状态时间轴、DOF
- **AI(表面丰富度)**:⛔ 无通道,交接包完整(HANDOFF.md:prompt/negative/首尾帧/hero/passes/运动与连续性说明)。这是当前系统边界,不是失败
- **合成(整合/光学质感)**:✅ HALO→SOFT→CHROMA→TONE→GRAIN→晕影(numpy 逐帧);夜态黑位从 CG 纯黑抬到胶片蓝灰

## 与质感目标(实拍照片)的差距(triple_blender_ai_final.png)
1. 表面历史:灰泥剥落/涂鸦/污渍全部缺失——正是 handoff 给 AI 的部分
2. 拱门几何:blocking 圆柱拱读作"鼓包",需真拱洞(boolean/建模)
3. 白天状态影界锐度可以,但缺照片里墙面的微反弹光层次
4. 程序化 bump 在 960p 下几乎不可见——控制通道用途足够,美术用途不够

## 构图迭代记录(4 轮看图修正,全部留档)
机位丢街角→对角机位;拱顶白球→胶合板拱;点光烧招牌→灯位归位;太阳方位/遮挡楼三次几何试错(全遮挡→黑屏[相机进了遮挡体]→方位角25°+对街遮挡楼=对角影界)。教训:**影子施主的几何要先算再摆**(仰角×距离=影高,方位角×距离=水平漂移)。

## Blender 5.1 无头陷阱(新增实测)
- `BLENDER_EEVEE_NEXT` 枚举已移除(回归 `BLENDER_EEVEE`)
- `scene.node_tree` 没了 → `scene.compositing_node_group`(需手建 CompositorNodeTree);且 `CompositorNodeOutputFile.base_path` 也变——**无头 passes 最稳路线 = 材质覆盖法**(emission 材质:CameraData 深度/Geometry 法线/pass_index 白黑),引擎无关零 API 风险
