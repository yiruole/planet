# VERIFIED CAPABILITIES(全部有可看成品与脚本,2026-07-08)

## 参考→复刻
- 视频结构化逆向(shot 检测/contact sheet/逐帧观察/音频 RMS 声画对齐):media_inspect.py,多案例
- 盲测协议(页面文案当隐藏答案,机制逆向 4/4):backrooms
- hybrid 管线(Blender 光层 → TD 分频驱动):backrooms audio-relight v9
- 状态切换合成判别(同底板多状态,省一个数量级):snow-flash、light-leak 启发

## footage 变换(全 numpy/ffmpeg 本地)
- motion trace / temporal echo(运动遮罩衰减累积)
- living-painting 区域位移场(key-field 换场;静照+视频两版)
- 2.5D 面片投影(homography,人脸手风琴,视频保活)
- 相位相关稳像 + 遮罩跟踪(平移)+ 手机自动曝光锁定
- 运动量量化(tblend 帧差 YAVG)与区域占比归一对标

## 空间
- 扫描素材质检(屏录≠空间素材;app reveal 成品≠原始扫描)
- Blender 照片匹配 blocking(画室、街角两案例)+ 观察镜头/turntable
- 重拍协议(角度环/曝光锁/透明与弱纹理对策)

## 声画
- 声音特征提取(RMS/分频/瞬态/质心/静默比/重复周期,numpy FFT)
- 概念映射设计(≤3 条+静默保留)→ Blender 逐帧关键帧驱动 → 带声成片
- 现象→声音反向链(分割→4 结构变量→加法合成+颗粒,声画 mux)

## 电影
- 概念开发链(motif→grammar→shot list→lighting states)
- 照片态 animatic(分级态+mask 扫掠+灯池渐亮)
- Blender blocking 镜头(三光照态时间轴/推近机位/DOF/影子施主几何)
- Control passes 材质覆盖法(depth/normal/object masks,Blender 5.1 无头安全)
- AI handoff package 标准(时间结构表+passes+prompt+禁动清单)
- 离线成像链合成(HALO→SOFT→CHROMA→TONE→GRAIN,两案例)

## 工程基础设施
- 无头 Blender 脚本循环(建场景+渲染一条命令);EEVEE 折射/枚举/合成器 5.1 陷阱表
- TD 桥纪律(幂等编号脚本重放/单行 exec/逐帧 save 导出)
- Houdini Python SOP 程序化(牡丹 v5)
- git 全程留档;GitHub 推送走环境变量代理
