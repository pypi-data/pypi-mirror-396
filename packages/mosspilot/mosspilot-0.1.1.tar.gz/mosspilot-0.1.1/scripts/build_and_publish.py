#!/usr/bin/env python3
"""
MossPilot 自动化测试框架 PyPI 发布脚本
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(cmd, check=True):
    """执行命令并打印输出"""
    print(f"执行命令: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    if check and result.returncode != 0:
        print(f"命令执行失败，退出码: {result.returncode}")
        sys.exit(1)
    
    return result


def clean_build():
    """清理构建目录"""
    print("清理构建目录...")
    dirs_to_clean = ["build", "dist", "*.egg-info"]
    
    for pattern in dirs_to_clean:
        if "*" in pattern:
            import glob
            for path in glob.glob(pattern):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                    print(f"删除目录: {path}")
        else:
            if os.path.exists(pattern):
                shutil.rmtree(pattern)
                print(f"删除目录: {pattern}")


def check_dependencies():
    """检查构建依赖"""
    print("检查构建依赖...")
    try:
        import build
        import twine
        print("✓ 构建依赖已安装")
    except ImportError as e:
        print(f"缺少构建依赖: {e}")
        print("请运行: pip install build twine")
        sys.exit(1)


def run_tests():
    """运行测试"""
    print("运行测试...")
    result = run_command("python -m pytest tests/ -v", check=False)
    if result.returncode != 0:
        print("⚠️ 测试失败，但继续构建...")
    else:
        print("✓ 测试通过")


def build_package():
    """构建包"""
    print("构建包...")
    run_command("python -m build")
    print("✓ 包构建完成")


def check_package():
    """检查包"""
    print("检查包...")
    run_command("python -m twine check dist/*")
    print("✓ 包检查通过")


def upload_to_testpypi():
    """上传到 TestPyPI"""
    print("上传到 TestPyPI...")
    run_command("python -m twine upload --repository testpypi dist/*")
    print("✓ 已上传到 TestPyPI")


def upload_to_pypi():
    """上传到 PyPI"""
    print("上传到 PyPI...")
    run_command("python -m twine upload dist/* --repository mosspilot")
    print("✓ 已上传到 PyPI")


def main():
    """主函数"""
    print("MossPilot 自动化测试框架 PyPI 发布脚本")
    print("=" * 50)
    
    # 检查是否在项目根目录
    if not os.path.exists("pyproject.toml"):
        print("错误: 请在项目根目录运行此脚本")
        sys.exit(1)
    
    # 解析命令行参数
    test_only = "--test" in sys.argv
    skip_tests = "--skip-tests" in sys.argv
    
    try:
        # 1. 检查依赖
        check_dependencies()
        
        # 2. 清理构建目录
        clean_build()
        
        # 3. 运行测试（可选）
        if not skip_tests:
            run_tests()
        
        # 4. 构建包
        build_package()
        
        # 5. 检查包
        check_package()
        
        # 6. 上传
        if test_only:
            upload_to_testpypi()
            print("\n🎉 成功发布到 TestPyPI!")
            print("测试安装: pip install -i https://test.pypi.org/simple/mosspilot")
        else:
            # 询问是否确认发布到正式 PyPI
            confirm = input("\n确认发布到正式 PyPI? (y/N): ")
            if confirm.lower() == 'y':
                upload_to_pypi()
                print("\n🎉 成功发布到 PyPI!")
                print("安装命令: pip install mosspilot")
            else:
                print("取消发布")
    
    except KeyboardInterrupt:
        print("\n用户取消操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n发布失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()