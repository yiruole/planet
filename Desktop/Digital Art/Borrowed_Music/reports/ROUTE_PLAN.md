# Borrowed Music — 制作路线(2026-07-08)

## 总链(全部走已验证 skill,不新建)
```
film-development-previs(本阶段:结构/节奏/灰盒)
→ blender-effect-builder(场景/薄膜原型/机位/光照/无头渲染循环)
→ hybrid-cg-ai-cinematography(hero 阶段:passes 材质覆盖法 + AI handoff)
→ after-effects-compositor(成像链:HALO→SOFT→CHROMA→TONE→GRAIN;暗部层次;缺音帧画面响应)
→ sound-image-system(声音设计:泄漏/触碰/借来的音乐与画面事件对齐;漫游车振动=瞬态→物体冲量,直接复用 Phase 4 映射代码)
```
辅助:image-to-video-director(space.mov 参考的承载力分析思路用于 SHOT 01 构图)、footage-transform-lab(薄膜"轻微起伏"可用位移场思路在合成端补,若 3D 布料太贵)。

## 关键技术决策
1. **薄膜三原型全部 Blender 材质+简单几何**,不做布料模拟(性能纪律+资产策略):起伏=顶点级 wave/noise 位移或合成端位移场
2. **室内外一个 .blend 两个 set**(相距 100m),6 机位分镜头渲染,ffmpeg 拼装——空间连续性由同工程保证
3. 星空:animatic 用世界着色器 Voronoi 星点;成片换 HDRI(缺口表)
4. 声音:先 numpy 全 temp(缺音精确可控),成片阶段逐轨替换;**声画同步点**(触碰×5、漫游车振动×1、缺音×1)从 animatic 起就锁帧号
5. 对白空间感:第二句走"radio/门后"滤波(diff 高通+衰减),不拍对方(constraint)
6. 缺音的画面响应(合成端):该帧微小曝光/薄膜亮度下沉一次,不做夸张效果

## 阶段计划
- STAGE 2(本次):30s 灰盒 animatic + 全 temp 声轨 → 验证叙事 6 项
- STAGE 3:hero frame(ANIMATIC_REVIEW 选定镜头)+ 深色薄纱材质升级 + AI handoff 包
- STAGE 4:分镜头成片渲染(Cycles 夜景按需)+ 成像链 + 真声轨替换
- STAGE 5:终剪/调色/字幕/交付
