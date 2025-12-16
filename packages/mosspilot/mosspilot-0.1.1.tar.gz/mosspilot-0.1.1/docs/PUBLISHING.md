# PyPI 发布指南

本文档介绍如何将 Moss 自动化测试框架发布到 PyPI。

## 前置要求

### 1. 安装构建工具

```bash
pip install build twine
```

### 2. 配置 PyPI 账户

- 注册 [PyPI](https://pypi.org/account/register/) 账户
- 注册 [TestPyPI](https://test.pypi.org/account/register/) 账户（用于测试）
- 生成 API Token：
  - PyPI: https://pypi.org/manage/account/token/
  - TestPyPI: https://test.pypi.org/manage/account/token/

### 3. 配置认证

创建 `~/.pypirc` 文件：

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = <your-pypi-api-token>

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = <your-testpypi-api-token>
```

## 发布流程

### 方法一：使用自动化脚本（推荐）

```bash
# 测试发布到 TestPyPI
python scripts/build_and_publish.py --test

# 正式发布到 PyPI
python scripts/build_and_publish.py
```

### 方法二：手动发布

#### 1. 清理构建目录

```bash
rm -rf build/ dist/ *.egg-info/
```

#### 2. 运行测试

```bash
python -m pytest tests/ -v
```

#### 3. 构建包

```bash
python -m build
```

#### 4. 检查包

```bash
python -m twine check dist/*
```

#### 5. 上传到 TestPyPI（测试）

```bash
python -m twine upload --repository testpypi dist/*
```

#### 6. 测试安装

```bash
pip install -i https://test.pypi.org/simple/ mosspilot-test-framework
```

#### 7. 上传到正式 PyPI

```bash
python -m twine upload dist/*
```

## 版本管理

### 更新版本号

在 [`pyproject.toml`](../pyproject.toml) 中更新版本号：

```toml
[project]
version = "0.1.1"  # 更新版本号
```

### 版本规范

遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范：

- `MAJOR.MINOR.PATCH`
- `0.1.0` - 初始版本
- `0.1.1` - 补丁版本（bug修复）
- `0.2.0` - 次要版本（新功能）
- `1.0.0` - 主要版本（重大变更）

## 发布检查清单

发布前请确认：

- [ ] 所有测试通过
- [ ] 文档已更新
- [ ] [`CHANGELOG.md`](../CHANGELOG.md) 已更新
- [ ] 版本号已更新
- [ ] 依赖包版本已确认
- [ ] 在 TestPyPI 上测试成功

## 常见问题

### 1. 包名冲突

如果包名已存在，需要修改 [`pyproject.toml`](../pyproject.toml) 中的 `name` 字段。

### 2. 认证失败

检查 `~/.pypirc` 配置文件和 API Token 是否正确。

### 3. 构建失败

确保所有依赖都在 [`pyproject.toml`](../pyproject.toml) 中正确声明。

### 4. 上传失败

检查网络连接和 PyPI 服务状态。

## 自动化发布

可以通过 GitHub Actions 实现自动化发布：

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
```

## 发布后验证

发布成功后，验证包是否可以正常安装和使用：

```bash
# 创建新的虚拟环境
python -m venv test_env
source test_env/bin/activate  # Linux/Mac
# 或 test_env\Scripts\activate  # Windows

# 安装包
pip install mosspilot-test-framework

# 验证安装
mosspilot --version

# 创建测试项目
mosspilot init test-project --template basic

# 运行测试
cd test-project
mosspilot run all
```

## 支持

如果在发布过程中遇到问题，请：

1. 检查 [PyPI 文档](https://packaging.python.org/)
2. 查看 [Twine 文档](https://twine.readthedocs.io/)
3. 提交 Issue 到项目仓库