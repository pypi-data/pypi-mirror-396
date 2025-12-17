#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建脚本 - 用于构建和发布PyPI包
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def run_command(cmd, cwd=None, check=True):
    """运行命令并处理输出"""
    print(f"运行命令: {' '.join(cmd) if isinstance(cmd, list) else cmd}")

    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=check,
            capture_output=True,
            text=True
        )

        if result.stdout:
            print(f"输出: {result.stdout}")
        if result.stderr:
            print(f"错误: {result.stderr}")

        return result.returncode == 0

    except subprocess.CalledProcessError as e:
        print(f"命令失败: {e}")
        if e.stdout:
            print(f"输出: {e.stdout}")
        if e.stderr:
            print(f"错误: {e.stderr}")
        return False


def clean_build_artifacts():
    """清理构建产物"""
    print("清理构建产物...")

    # 要清理的目录和文件
    cleanup_items = [
        'build/',
        'dist/',
        '*.egg-info/',
        '**/__pycache__/',
        '**/*.pyc',
        '**/*.pyo',
    ]

    project_root = Path(__file__).parent.parent

    for pattern in cleanup_items:
        if pattern.endswith('/'):
            # 目录
            for path in project_root.glob(pattern):
                if path.is_dir():
                    print(f"删除目录: {path}")
                    shutil.rmtree(path)
        else:
            # 文件模式
            for path in project_root.glob(pattern):
                if path.is_file():
                    print(f"删除文件: {path}")
                    path.unlink()

    print("清理完成")


def install_build_deps():
    """安装构建依赖"""
    print("安装构建依赖...")

    deps = [
        'build',
        'twine',
        'wheel',
        'setuptools>=61.0',
    ]

    for dep in deps:
        if not run_command([sys.executable, '-m', 'pip', 'install', dep]):
            print(f"安装 {dep} 失败")
            return False

    print("构建依赖安装完成")
    return True


def run_tests():
    """运行测试"""
    print("运行测试...")

    project_root = Path(__file__).parent.parent

    # 运行单元测试
    if not run_command([sys.executable, '-m', 'pytest', 'unit/', '-v'], cwd=project_root):
        print("单元测试失败")
        return False

    # 运行代码格式检查
    if not run_command([sys.executable, '-m', 'flake8', 'src/'], cwd=project_root):
        print("代码格式检查失败，但继续构建")

    print("测试通过")
    return True


def build_package():
    """构建包"""
    print("构建包...")

    project_root = Path(__file__).parent.parent

    if not run_command([sys.executable, '-m', 'build'], cwd=project_root):
        print("构建失败")
        return False

    print("包构建完成")
    return True


def check_package():
    """检查包"""
    print("检查包...")

    project_root = Path(__file__).parent.parent
    dist_dir = project_root / 'dist'

    if not dist_dir.exists():
        print("dist目录不存在")
        return False

    # 检查构建的文件
    files = list(dist_dir.glob('*'))
    if not files:
        print("没有找到构建的文件")
        return False

    print(f"找到构建文件: {[f.name for f in files]}")

    # 使用twine检查
    for file_path in files:
        if not run_command([sys.executable, '-m', 'twine', 'check', str(file_path)]):
            print(f"检查文件失败: {file_path}")
            return False

    print("包检查通过")
    return True


def upload_to_testpypi():
    """上传到TestPyPI"""
    print("上传到TestPyPI...")

    project_root = Path(__file__).parent.parent

    if not run_command([
        sys.executable, '-m', 'twine', 'upload',
        '--repository', 'testpypi',
        'dist/*'
    ], cwd=project_root):
        print("上传到TestPyPI失败")
        return False

    print("上传到TestPyPI成功")
    return True


def upload_to_pypi():
    """上传到正式PyPI"""
    print("上传到PyPI...")

    project_root = Path(__file__).parent.parent

    if not run_command([
        sys.executable, '-m', 'twine', 'upload',
        'dist/*'
    ], cwd=project_root):
        print("上传到PyPI失败")
        return False

    print("上传到PyPI成功")
    return True


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='构建和发布unified-finance-data包')
    parser.add_argument('--skip-tests', action='store_true', help='跳过测试')
    parser.add_argument('--skip-clean', action='store_true', help='跳过清理')
    parser.add_argument('--test-only', action='store_true', help='仅上传到TestPyPI')
    parser.add_argument('--build-only', action='store_true', help='仅构建，不上传')

    args = parser.parse_args()

    print("开始构建和发布 unified-finance-data")
    print("=" * 60)

    # 检查项目结构
    project_root = Path(__file__).parent.parent
    pyproject_path = project_root / 'pyproject.toml'

    if not pyproject_path.exists():
        print(f"未找到 pyproject.toml 文件: {pyproject_path}")
        return False

    # 清理构建产物
    if not args.skip_clean:
        if not clean_build_artifacts():
            return False

    # 安装构建依赖
    if not install_build_deps():
        return False

    # 运行测试
    if not args.skip_tests:
        if not run_tests():
            return False

    # 构建包
    if not build_package():
        return False

    # 检查包
    if not check_package():
        return False

    # 如果只是构建，则到此为止
    if args.build_only:
        print("构建完成！")
        return True

    # 确认上传
    if args.test_only:
        print("\n准备上传到TestPyPI")
        response = input("确认继续? (y/N): ")
    else:
        print("\n准备上传到正式PyPI")
        response = input("确认继续? (y/N): ")

    if response.lower() != 'y':
        print("用户取消操作")
        return False

    # 上传到TestPyPI
    if args.test_only:
        if not upload_to_testpypi():
            return False
        print("\n成功上传到TestPyPI!")
        print("安装测试: pip install --index-url https://test.pypi.org/simple/ unified-finance-data")
        return True

    # 上传到TestPyPI（先测试）
    print("\n先上传到TestPyPI进行测试...")
    if not upload_to_testpypi():
        print("TestPyPI上传失败，但继续上传到正式PyPI")

    # 上传到正式PyPI
    if not upload_to_pypi():
        print("上传到正式PyPI失败")
        return False

    print("\n成功发布到PyPI!")
    print("安装: pip install unified-finance-data")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)