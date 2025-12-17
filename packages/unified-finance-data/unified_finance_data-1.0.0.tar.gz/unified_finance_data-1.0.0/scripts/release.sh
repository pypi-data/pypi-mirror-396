#!/bin/bash
# 发布脚本 - 用于自动化发布流程

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查Python版本
check_python() {
    print_info "检查Python版本..."

    if ! command -v python3 &> /dev/null; then
        print_error "Python3未安装"
        exit 1
    fi

    python_version=$(python3 --version | cut -d' ' -f2)
    print_success "Python版本: $python_version"
}

# 检查Git状态
check_git() {
    print_info "检查Git状态..."

    if ! command -v git &> /dev/null; then
        print_error "Git未安装"
        exit 1
    fi

    # 检查是否有未提交的更改
    if [[ -n $(git status --porcelain) ]]; then
        print_warning "有未提交的更改:"
        git status --short
        read -p "是否继续? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "操作取消"
            exit 0
        fi
    fi

    print_success "Git状态检查完成"
}

# 更新版本号
update_version() {
    if [ -z "$1" ]; then
        print_error "请提供版本号"
        echo "用法: $0 <version> [options]"
        exit 1
    fi

    local new_version="$1"
    print_info "更新版本号到: $new_version"

    # 更新pyproject.toml中的版本
    sed -i.bak "s/^version = .*/version = \"$new_version\"/" pyproject.toml
    rm pyproject.toml.bak

    # 更新__init__.py中的版本
    sed -i.bak "s/__version__ = .*/__version__ = \"$new_version\"/" src/unified_finance_data/__init__.py
    rm src/unified_finance_data/__init__.py.bak

    print_success "版本号更新完成"

    # 提交版本更新
    git add pyproject.toml src/unified_finance_data/__init__.py
    git commit -m "bump version to $new_version"
    git tag -a "v$new_version" -m "Release version $new_version"

    print_success "版本更新已提交并打标签"
}

# 运行测试
run_tests() {
    print_info "运行测试..."

    # 激活虚拟环境（如果存在）
    if [ -d "venv" ]; then
        source venv/bin/activate
        print_info "激活虚拟环境"
    elif [ -d ".venv" ]; then
        source .venv/bin/activate
        print_info "激活虚拟环境"
    fi

    # 安装依赖
    print_info "安装依赖..."
    pip install -e ".[dev]"

    # 运行单元测试
    print_info "运行单元测试..."
    if ! python -m pytest unit/ -v; then
        print_error "单元测试失败"
        exit 1
    fi

    print_success "测试通过"
}

# 构建包
build_package() {
    print_info "构建包..."

    # 清理旧的构建
    rm -rf build/ dist/ *.egg-info/

    # 构建包
    if ! python -m build; then
        print_error "构建失败"
        exit 1
    fi

    print_success "包构建完成"
}

# 检查包
check_package() {
    print_info "检查包..."

    if ! python -m twine check dist/*; then
        print_error "包检查失败"
        exit 1
    fi

    print_success "包检查通过"
}

# 发布到TestPyPI
release_test() {
    print_info "发布到TestPyPI..."

    if ! python -m twine upload --repository testpypi dist/*; then
        print_error "发布到TestPyPI失败"
        exit 1
    fi

    print_success "成功发布到TestPyPI"
    print_info "测试安装: pip install --index-url https://test.pypi.org/simple/ unified-finance-data"
}

# 发布到PyPI
release_production() {
    print_info "发布到PyPI..."

    # 推送标签到远程仓库
    git push origin --tags

    if ! python -m twine upload dist/*; then
        print_error "发布到PyPI失败"
        exit 1
    fi

    print_success "成功发布到PyPI"
    print_info "安装: pip install unified-finance-data"
}

# 主函数
main() {
    print_info "开始发布流程..."

    # 检查参数
    if [ $# -eq 0 ]; then
        echo "用法: $0 <version> [options]"
        echo "选项:"
        echo "  --test-only     仅发布到TestPyPI"
        echo "  --skip-tests    跳过测试"
        echo "  --dry-run       仅构建，不发布"
        exit 1
    fi

    local version="$1"
    local test_only=false
    local skip_tests=false
    local dry_run=false

    # 解析选项
    shift
    while [[ $# -gt 0 ]]; do
        case $1 in
            --test-only)
                test_only=true
                shift
                ;;
            --skip-tests)
                skip_tests=true
                shift
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            *)
                print_error "未知选项: $1"
                exit 1
                ;;
        esac
    done

    # 检查环境和Git
    check_python
    check_git

    # 更新版本
    update_version "$version"

    # 运行测试
    if [ "$skip_tests" = false ]; then
        run_tests
    else
        print_warning "跳过测试"
    fi

    # 构建和检查包
    build_package
    check_package

    # 发布
    if [ "$dry_run" = true ]; then
        print_success "构建完成（干运行）"
        print_info "要发布，请运行: $0 $version"
        exit 0
    fi

    if [ "$test_only" = true ]; then
        release_test
        print_success "TestPyPI发布完成!"
    else
        # 先发布到TestPyPI进行测试
        print_info "先发布到TestPyPI进行测试..."
        release_test

        read -p "TestPyPI发布成功，是否继续发布到正式PyPI? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            release_production
            print_success "🎉 发布完成!"
        else
            print_info "已取消发布到正式PyPI"
        fi
    fi
}

# 运行主函数
main "$@"