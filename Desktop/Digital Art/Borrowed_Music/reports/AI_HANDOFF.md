# Borrowed Music — AI handoff package(STAGE 4,2026-07-08)

本机无 AI 生成通道,不假装执行。以下交接包可直接用于 ComfyUI(img2img + depth/normal ControlNet)或商用服务的 look enrichment。**AI 只做表面丰富,不得改变构图/位置/光向/动作/空间。**

## 任务 1:S02 hero frame 旧物感增强
- 底图:`04_lookdev/S02/S02_hero_comp.png`(构图与光即最终答案)
- 目标:膜类挂件加轻微污渍/储存痕迹(去"灯箱感");纤维件织物微结构;衣柜内壁轻微使用磨损;整体保持近黑
- Prompt 建议:"dark wardrobe interior at night, translucent aged film sheets hanging on a rail, worn plastic membranes with dust and storage marks, faint cold backlight leaking through, deep blacks, restrained, analog photography, no color, desaturated"
- Negative:"neon, colorful, glowing runes, particles, magic, sci-fi hologram, bright, clean, new fabric, clothes, hangers with shirts"
- 约束:挂件数量/位置/明暗关系不可变;人物剪影轮廓不可变;背光方向(柜内向外)不可变

## 任务 2:深色薄纱织物微观(hero 材质参考)
- 底图:`04_lookdev/S02/hero_veil.png`
- 目标:近黑薄纱的织物结构(细网/纱线),星点保持稀疏(≤6 个),边缘极弱冷光
- Negative:"stars everywhere, galaxy print, sparkle, glitter, sequins"

## 任务 3:S01 外景大气(可选)
- 底图:production `prod/f0048.jpg`;look 目标 `test/space.mov`(火星车星空段,注意它是屏录仅作气质参考)
- 目标:地表岩土质感、地平线薄尘、星空密度分层(银河带);居住舱/漫游车剪影形状不可变
- Negative:"city lights, aurora, colorful nebula, lens flare, daylight"

## 控制素材
`02_blender/borrowed_music_production.blend` 可重渲任意帧任意 pass(depth/normal/mask 走 hybrid-cg-ai-cinematography §2 材质覆盖法,已有现成代码模式)。回填方式:AI 结果作为贴图/参考重制材质,或 img2img 逐帧(仅静帧镜头可行,动镜头需 temporal 一致性方案——当前不做)。
