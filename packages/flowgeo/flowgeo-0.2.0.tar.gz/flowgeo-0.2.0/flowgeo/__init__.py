"""
FlowGeo - 3D 几何可视化库
"""

# 版本信息
__version__ = "0.2.0"
__author__ = "Bin"

# 核心类导入
from .core.scene import Scene
from .core.slide import Slide
from .core.config import get_config, set_config, get_theme_config

# 几何对象导入
from .geometry.base import Point, Vector
from .geometry.primitives import Line, Polygon
from .geometry.axes import Axes
from .geometry.solids.cube import Cube
from .geometry.solids.sphere import Sphere
from .geometry.solids.pyramid import Pyramid

# 渲染系统导入（新增）
from .rendering import Renderer, RenderResult, Style
from .rendering.backends import PlotlyRenderer
from .rendering.camera import SmartCamera

# 导出系统导入（新增）
from .export import (
    Exporter,
    HtmlExporter,
    download_offline_resources,
    check_offline_resources
)

# 主题导入
from .themes import cozy_light, manim_dark

# 便捷函数
def get_available_themes():
    """获取可用主题列表"""
    return get_config('themes.available', ['cozy_light', 'manim_dark'])

# 公开的 API
__all__ = [
    # 核心类
    'Scene', 'Slide',

    # 几何对象
    'Point', 'Vector', 'Line', 'Polygon', 'Axes',
    'Cube', 'Sphere', 'Pyramid',

    # 渲染系统（新增）
    'Renderer', 'RenderResult', 'Style', 'PlotlyRenderer', 'SmartCamera',
    
    # 导出系统（新增）
    'Exporter', 'HtmlExporter',
    'download_offline_resources', 'check_offline_resources',

    # 配置函数
    'get_config', 'set_config', 'get_theme_config',

    # 便捷函数
    'get_available_themes',

    # 主题
    'cozy_light', 'manim_dark'
]