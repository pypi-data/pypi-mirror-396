# FlowGeo 静态资源目录

本目录用于存放离线模式所需的JavaScript库。

## 📖 使用说明

### 默认行为（在线模式）

```python
from flowgeo import Scene

scene = Scene()
# ... 添加内容 ...
scene.export_html("output.html")  # 默认使用CDN
```

**特点**：
- ✅ 生成的HTML文件很小（几KB）
- ✅ 无需下载任何资源
- ⚠️ 需要网络连接才能查看HTML

### 离线模式（手动开启）

```python
scene.export_html("output.html", use_local_resources=True)  # 启用离线模式
```

**特点**：
- ✅ 首次使用时自动下载资源（优先国内源）
- ✅ 生成的HTML包含所有JS代码，无需网络即可查看
- ⚠️ 生成的HTML文件较大（4-5MB）
- ⚠️ 首次使用需要网络连接下载资源

## 🚀 自动下载机制

FlowGeo 会在首次使用离线模式时**自动下载**所需的资源文件，无需手动操作！

**下载策略**：
1. 优先尝试国内CDN源（BootCDN、jsDelivr中国）
2. 如果国内源失败，自动切换到国外源
3. 下载的资源会缓存在本地，后续使用无需重新下载

```python
from flowgeo import Scene

scene = Scene()
# ... 添加内容 ...

# 首次使用时会自动下载资源（需要网络连接）
scene.export_html("output.html", use_local_resources=True)
```

### 手动下载资源

如果需要提前下载资源，可以使用：

```python
from flowgeo import download_offline_resources, check_offline_resources

# 检查资源状态
status = check_offline_resources()
print(status)  # {'plotly': True, 'mathjax': True, 'polyfill': True}

# 手动下载所有资源
download_offline_resources()
```

或使用命令行：

```bash
python -m flowgeo.export.resource_manager
```

## 📦 资源文件列表

自动下载的资源包括：

1. **Plotly.js** (必需) - 约 3.5 MB
   - 国内源: BootCDN, jsDelivr
   - 国外源: cdn.plot.ly
   
2. **MathJax** (必需) - 约 800 KB
   - 国内源: BootCDN, jsDelivr
   - 国外源: cdn.jsdelivr.net
   
3. **Polyfill** (可选) - 约 50 KB
   - 国内源: BootCDN
   - 国外源: polyfill.io

## 📁 目录结构

```
flowgeo/static/
├── README.md
└── js/
    ├── plotly-2.26.0.min.js    (自动下载)
    ├── tex-mml-chtml.js        (自动下载)
    └── polyfill.min.js         (自动下载)
```

## 💡 高级用法

### 提前下载资源

如果想在使用前提前下载资源：

```python
from flowgeo import download_offline_resources, check_offline_resources

# 检查资源状态
status = check_offline_resources()
print(status)  # {'plotly': True, 'mathjax': True, 'polyfill': True}

# 手动下载所有资源
download_offline_resources()
```

### 命令行下载

```bash
python -m flowgeo.export.resource_manager
```

### 强制重新下载

```python
download_offline_resources(force=True)  # 强制重新下载所有资源
```

## ⚠️ 注意事项

1. **默认使用在线模式**：不会自动下载资源，生成的HTML需要网络才能查看
2. **离线模式需手动开启**：使用 `use_local_resources=True` 参数
3. **首次下载需要网络**：首次使用离线模式时会自动下载资源（优先国内源）
4. **资源会被缓存**：下载后的资源保存在本地，后续使用无需重新下载
5. **自动回退机制**：如果所有源都下载失败，会自动回退到CDN模式
6. **文件体积较大**：离线HTML文件约4-5MB（包含所有JavaScript库）

## 🌐 镜像源列表

### Plotly.js
- 🇨🇳 BootCDN: `https://cdn.bootcdn.net/ajax/libs/plotly.js/2.26.0/plotly.min.js`
- 🇨🇳 jsDelivr: `https://cdn.jsdelivr.net/npm/plotly.js@2.26.0/dist/plotly.min.js`
- 🌍 官方CDN: `https://cdn.plot.ly/plotly-2.26.0.min.js`

### MathJax
- 🇨🇳 BootCDN: `https://cdn.bootcdn.net/ajax/libs/mathjax/3.2.2/es5/tex-mml-chtml.js`
- 🇨🇳 jsDelivr: `https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js`

### Polyfill
- 🇨🇳 BootCDN: `https://cdn.bootcdn.net/ajax/libs/babel-polyfill/7.12.1/polyfill.min.js`
- 🌍 Polyfill.io: `https://polyfill.io/v3/polyfill.min.js?features=es6`