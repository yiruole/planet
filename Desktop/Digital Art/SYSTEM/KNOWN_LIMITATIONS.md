# KNOWN LIMITATIONS(诚实台账,2026-07-08)

## 需要外部 API/服务(当前只出 handoff,不假装)
- AI 图像/视频生成(Runway/Kling/Luma/ComfyUI 云):hero frame 增强、i2v、表面丰富度
- Tripo/image-to-3D:hero asset 缺失时的升级路径(backrooms 复盘结论)

## 本机工具链缺口
- **无 CUDA**(Apple Silicon):Gaussian Splatting/NeRF 重训、Meshroom 不可本地执行
- **无 COLMAP**:photogrammetry 不可执行(装机需确认)
- **无 ML 视觉库**(opencv/torch;anaconda 是 x86 Rosetta):人物/物体 segmentation、光流、深度估计全缺 → 人脸抠像等需求走 AE 手工或不做
- **AE 无自动化通道**:ExtendScript/UXP 桥未建;roto/planar tracking 只能手工清单
- ffmpeg 8.1.1 **无 drawtext**(字幕用 PIL 画或 TD Text TOP)

## 方法级已知天花板
- 位移场遮罩跟踪只有平移;推进镜头的尺度变化未实现(需相似变换跟踪或 AE)
- 程序化资产到"需真资产"级参考会撞墙(asset ceiling 分级见 reference-reverse-engineer)
- headless Bullet 刚体堆叠=工程黑洞(4 连败,已弃用,用确定性堆叠)
- EEVEE 玻璃/折射在 blocking 层是灰渐变代理;成片级透明材质需 Cycles+环境反射
- TD 桥空闲挂死(App Nap 疑);`project.save()` 桥内死锁——幂等重放为准
- moviefileout 无头不可靠——jpg 序列+ffmpeg 为准

## 素材级教训(反复出现)
- 屏录素材:文件名不可信、UI 污染、转场帧毁统计——一律先逐帧质检
- 扫描 app 只导 reveal 视频=丢了原始资产(PLY/GLB 才可二次加工)
- 手机实拍默认自动曝光,后期锁定有成本——拍摄时 AE/AF 锁
