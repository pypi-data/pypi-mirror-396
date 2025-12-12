# kevin_dl

一个面向深度学习的工具库



环境要求

```shell
numpy>=1.19
pytorch>=1.2
kevin-toolbox>=1.4.10
```

安装方法：

```shell
pip install kevin-dl  --no-dependencies
```



[项目地址 Repo](https://github.com/cantbeblank96/kevin_dl_release)

[免责声明 Disclaimer](./notes/Disclaimer.md)

[版本更新记录](./notes/Release_Record.md)：

- v 0.1.1 （2025-12-09）【bug fix】
  - fix bug in models.api.run_kevin_sdk_face_detect()，支持自动从外部文件 `~/.kv_dl_cfg/.run_kevin_sdk_face_detect.json` 读取默认配置。
