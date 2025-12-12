# PixelArrayLib - PixelArray Python开发工具库

PixelArrayLib是一个功能丰富的Python开发工具库，包含阿里云服务、数据库工具、装饰器、监控等功能，同时提供便捷的命令行工具。

## 安装

### 基础安装

```bash
pip install pixelarraylib
```

### 可选依赖安装

为了避免安装不必要的依赖，你可以按需安装特定模块的依赖：

```bash
# 只安装阿里云服务相关依赖
pip install pixelarraylib[aliyun]

# 只安装MySQL工具相关依赖
pip install pixelarraylib[mysql]

# 只安装Redis工具相关依赖
pip install pixelarraylib[redis]

# 只安装监控工具相关依赖
pip install pixelarraylib[monitor]

# 只安装网络工具相关依赖
pip install pixelarraylib[net]

# 只安装系统工具相关依赖
pip install pixelarraylib[system]

# 只安装GitLab工具相关依赖
pip install pixelarraylib[gitlab]

# 安装所有可选依赖
pip install pixelarraylib[all]

# 组合安装多个模块
pip install pixelarraylib[mysql,redis]
```

**可选依赖说明：**
- `aliyun`: 阿里云服务集成（OSS、SMS、FC、DM、ECS、ECI等）
- `mysql`: MySQL数据库工具（pymysql、aiomysql）
- `redis`: Redis数据库工具
- `monitor`: 监控告警工具（飞书通知等）
- `net`: 网络请求工具
- `system`: 系统工具（加密、SSH等）
- `gitlab`: GitLab工具（PyPI包管理、代码分析等）
- `all`: 所有可选依赖

## 使用方法

### 1. Python程序中使用

```python
# 导入pixelarraylib模块
import pixelarraylib

# 使用各种功能模块
from pixelarraylib.aliyun import some_service
from pixelarraylib.db_utils import database_tools
from pixelarraylib.decorators import useful_decorators
```

### 2. 命令行工具使用

安装后，你可以在命令行中直接使用 `pixelarraylib` 命令：

#### 创建测试用例文件
```bash
# 一键创建所有测试用例文件
pixelarraylib create_test_case_files
```

## 功能特性

- **阿里云服务集成**: 包含CMS、Green、DM、FC、SMS、STS等服务
- **数据库工具**: MySQL、Redis等数据库操作工具
- **Web框架**: FastAPI集成
- **实用工具**: 二维码生成、加密解密、XML处理等
- **命令行工具**: 测试用例生成、代码统计等实用脚本

## 开发

### 本地开发安装

```bash
# 克隆仓库
git clone https://gitlab.com/pixelarrayai/general_pythondevutils_lib.git
cd general_pythondevutils_lib

# 安装开发依赖
pip install -e .

# 测试命令行工具
pixelarraylib --help
```

### 添加新的命令行工具

1. 在 `pixelarraylib/scripts/` 目录下创建新的脚本文件
2. 在 `pixelarraylib/__main__.py` 中添加新的命令选项
3. 更新 `pixelarraylib/scripts/__init__.py` 导出新功能

## 许可证

MIT License

## 作者

Lu qi (qi.lu@pixelarrayai.com) 