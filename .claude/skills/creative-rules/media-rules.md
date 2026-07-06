# Non-Destructive Media Rules — 媒体处理纪律

## 绝不修改原件

- 所有处理(转码/抽帧/代理/分析)输出到独立目录,原始素材只读。
- 分析产物统一放在素材旁的 `<name>_analysis/` 或用户指定目录,命名可追溯来源。
- 删除/覆盖/移动用户现有文件必须先问。分析缓存(自己生成的)可以自由管理。

## 本地优先

- 素材不上传外部服务。参考链接抓取(网页/视频平台)只下行,不上传用户内容。
- 未经允许不调用付费 API。

## 工具选择顺序

1. ffprobe/ffmpeg(零依赖,永远第一选择)
2. 已装的 Python 库(numpy/PIL/scikit-image)
3. 需要新装的重依赖(opencv/torch/whisper 等)——装之前评估:是否本任务真的需要、arm64 兼容性(注意本机 anaconda 是 x86_64 Rosetta,ML 库应装原生 arm64 环境)

## 常用产物规范

- **代理**:720p h264 crf 23,足够分析用
- **contact sheet**:覆盖全片时长的均匀采样网格,文件名含帧时间码
- **shot detection**:ffmpeg scene filter(阈值 0.3 起调),输出 JSON 时间码列表
- **代表帧**:每 shot 至少 1 帧,PNG 原分辨率
