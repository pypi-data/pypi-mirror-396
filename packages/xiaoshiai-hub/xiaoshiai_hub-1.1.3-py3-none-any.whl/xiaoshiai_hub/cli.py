"""
XiaoShi AI Hub SDK 命令行工具
"""

import argparse
import getpass
import os
import sys


def get_auth_from_env():
    """从环境变量获取认证信息"""
    token = os.environ.get("MOHA_TOKEN")
    username = os.environ.get("MOHA_USERNAME")
    password = os.environ.get("MOHA_PASSWORD")
    return token, username, password


def get_auth_from_file():
    """从文件获取已保存的 token"""
    from xiaoshiai_hub.auth import load_token
    token, base_url, _ = load_token()
    return token, base_url


def get_auth(args):
    """从命令行参数、环境变量和文件获取认证信息"""
    token, username, password = get_auth_from_env()

    # 命令行参数优先级最高
    if args.token:
        token = args.token
    if args.username:
        username = args.username
    if args.password:
        password = args.password

    # 如果没有通过环境变量或命令行提供 token，尝试从文件读取
    if not token and not (username and password):
        saved_token, _ = get_auth_from_file()
        if saved_token:
            token = saved_token

    return token, username, password


def cmd_upload_folder(args):
    """处理 upload-folder 命令"""
    from xiaoshiai_hub.upload import upload_folder

    token, username, password = get_auth(args)

    # 解析忽略模式
    ignore_patterns = args.ignore if args.ignore else None

    # 从环境变量或参数获取加密密码
    encryption_password = None
    if args.encrypt:
        encryption_password = os.environ.get("MOHA_ENCRYPTION_PASSWORD") or args.encryption_password
        if not encryption_password:
            print("错误: --encrypt 需要加密密码。"
                  "请设置 MOHA_ENCRYPTION_PASSWORD 环境变量或使用 --encryption-password 参数", file=sys.stderr)
            return 1

    # 获取加密算法
    algorithm = args.algorithm if encryption_password else None

    try:
        upload_folder(
            folder_path=args.folder,
            repo_id=args.repo_id,
            repo_type=args.repo_type,
            revision=args.revision,
            commit_message=args.message,
            base_url=args.base_url,
            username=username,
            password=password,
            token=token,
            encryption_password=encryption_password,
            ignore_patterns=ignore_patterns,
            temp_dir=args.temp_dir,
            algorithm=algorithm,
        )
        print("上传成功！")
        return 0
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_upload_file(args):
    """处理 upload-file 命令"""
    from xiaoshiai_hub.upload import upload_file

    token, username, password = get_auth(args)

    # 从环境变量或参数获取加密密码
    encryption_password = None
    if args.encrypt:
        encryption_password = os.environ.get("MOHA_ENCRYPTION_PASSWORD") or args.encryption_password
        if not encryption_password:
            print("错误: --encrypt 需要加密密码。"
                  "请设置 MOHA_ENCRYPTION_PASSWORD 环境变量或使用 --encryption-password 参数", file=sys.stderr)
            return 1

    # 确定仓库中的路径
    path_in_repo = args.path_in_repo if args.path_in_repo else os.path.basename(args.file)

    # 获取加密算法
    algorithm = args.algorithm if encryption_password else None

    try:
        upload_file(
            path_file=args.file,
            path_in_repo=path_in_repo,
            repo_id=args.repo_id,
            repo_type=args.repo_type,
            revision=args.revision,
            commit_message=args.message,
            base_url=args.base_url,
            username=username,
            password=password,
            token=token,
            encryption_password=encryption_password,
            algorithm=algorithm,
        )
        print(f"上传成功: {path_in_repo}")
        return 0
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_download_repo(args):
    """处理 download 命令"""
    from xiaoshiai_hub.download import snapshot_download

    token, username, password = get_auth(args)

    # 解析模式
    allow_patterns = args.include if args.include else None
    ignore_patterns = args.ignore if args.ignore else None

    try:
        local_path = snapshot_download(
            repo_id=args.repo_id,
            repo_type=args.repo_type,
            revision=args.revision,
            local_dir=args.local_dir,
            allow_patterns=allow_patterns,
            ignore_patterns=ignore_patterns,
            base_url=args.base_url,
            username=username,
            password=password,
            token=token,
            show_progress=not args.quiet,
        )
        print(f"下载完成: {local_path}")
        return 0
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_download_file(args):
    """处理 download-file 命令"""
    from xiaoshiai_hub.download import moha_hub_download

    token, username, password = get_auth(args)

    # 确定本地目录
    local_dir = args.local_dir if args.local_dir else "."

    try:
        local_path = moha_hub_download(
            repo_id=args.repo_id,
            filename=args.filename,
            repo_type=args.repo_type,
            revision=args.revision,
            local_dir=local_dir,
            base_url=args.base_url,
            username=username,
            password=password,
            token=token,
            show_progress=not args.quiet,
        )
        print(f"下载完成: {local_path}")
        return 0
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_login(args):
    """处理 login 命令"""
    from xiaoshiai_hub.auth import login
    from xiaoshiai_hub.exceptions import AuthenticationError

    # 获取用户名
    username = args.username
    if not username:
        username = input("用户名: ")

    # 获取密码
    password = args.password
    if not password:
        password = getpass.getpass("密码: ")

    if not username or not password:
        print("错误: 用户名和密码不能为空", file=sys.stderr)
        return 1

    try:
        _, token_path = login(
            username=username,
            password=password,
            base_url=args.base_url,
            token_dir=args.token_dir,
        )
        print("登录成功！")
        print(f"Token 已保存到: {token_path}")
        return 0
    except AuthenticationError as e:
        print(f"登录失败: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_logout(args):
    """处理 logout 命令"""
    from xiaoshiai_hub.auth import delete_token, get_token_path

    token_path = get_token_path(args.token_dir)

    if delete_token(args.token_dir):
        print(f"已退出登录，Token 文件已删除: {token_path}")
        return 0
    else:
        print(f"未找到 Token 文件: {token_path}")
        return 0


def cmd_whoami(args):
    """处理 whoami 命令"""
    from xiaoshiai_hub.auth import load_token, get_token_path

    token, base_url, username = load_token(args.token_dir)
    token_path = get_token_path(args.token_dir)

    if token:
        print(f"已登录")
        if username:
            print(f"用户名: {username}")
        if base_url:
            print(f"API 地址: {base_url}")
        print(f"Token 文件: {token_path}")
        return 0
    else:
        print("未登录")
        print(f"请使用 'moha login' 命令登录")
        return 1


def _parse_repo_id(repo_id: str):
    """解析仓库 ID，返回 (organization, repo_name)"""
    parts = repo_id.split("/")
    if len(parts) != 2:
        raise ValueError(f"无效的仓库 ID: {repo_id}，格式应为: 组织/仓库名")
    return parts[0], parts[1]


def _get_client(args):
    """创建 HubClient 实例"""
    from xiaoshiai_hub.client import HubClient
    token, username, password = get_auth(args)
    return HubClient(
        base_url=args.base_url,
        username=username,
        password=password,
        token=token,
    )


def cmd_repo_create(args):
    """处理 repo-create 命令"""
    try:
        org, repo_name = _parse_repo_id(args.repo_id)
        client = _get_client(args)

        # 解析 metadata
        metadata = {}
        if args.license:
            metadata["license"] = args.license
        if args.tasks:
            metadata["tasks"] = args.tasks
        if args.languages:
            metadata["languages"] = args.languages
        if args.tags:
            metadata["tags"] = args.tags
        if args.frameworks:
            metadata["frameworks"] = args.frameworks

        client.create_repository(
            organization=org,
            repo_type=args.repo_type,
            repo_name=repo_name,
            description=args.description,
            visibility=args.visibility,
            metadata=metadata if metadata else None,
            base_model=args.base_model,
            relationship=args.relationship,
        )
        print(f"仓库创建成功: {org}/{repo_name}")
        return 0
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_repo_update(args):
    """处理 repo-update 命令"""
    try:
        org, repo_name = _parse_repo_id(args.repo_id)
        client = _get_client(args)

        # 先获取仓库当前信息
        repo = client.get_repository_info(
            organization=org,
            repo_type=args.repo_type,
            repo_name=repo_name,
        )

        # 使用现有值作为默认值，只更新用户指定的字段
        description = args.description if args.description is not None else repo.description
        visibility = args.visibility if args.visibility is not None else repo.visibility

        # 合并 metadata：用户指定的覆盖现有的
        metadata = dict(repo.metadata) if repo.metadata else {}
        if args.license:
            metadata["license"] = args.license
        if args.tasks:
            metadata["tasks"] = args.tasks
        if args.languages:
            metadata["languages"] = args.languages
        if args.tags:
            metadata["tags"] = args.tags
        if args.frameworks:
            metadata["frameworks"] = args.frameworks

        # 处理 genealogy：用户指定的覆盖现有的
        base_model = args.base_model
        relationship = args.relationship
        if repo.genealogy:
            if base_model is None and 'baseModel' in repo.genealogy:
                base_model = repo.genealogy['baseModel']
            if relationship is None and 'relationship' in repo.genealogy:
                relationship = repo.genealogy['relationship']

        client.update_repository(
            organization=org,
            repo_type=args.repo_type,
            repo_name=repo_name,
            description=description,
            visibility=visibility,
            metadata=metadata if metadata else None,
            annotations=repo.annotations,
            base_model=base_model,
            relationship=relationship,
        )
        print(f"仓库更新成功: {org}/{repo_name}")
        return 0
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_repo_delete(args):
    """处理 repo-delete 命令"""
    try:
        org, repo_name = _parse_repo_id(args.repo_id)
        client = _get_client(args)

        # 确认删除
        if not args.yes:
            confirm = input(f"确定要删除仓库 {org}/{repo_name} 吗？此操作不可恢复！[y/N]: ")
            if confirm.lower() != 'y':
                print("已取消删除")
                return 0

        client.delete_repository(
            organization=org,
            repo_type=args.repo_type,
            repo_name=repo_name,
        )
        print(f"仓库删除成功: {org}/{repo_name}")
        return 0
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_repo_info(args):
    """处理 repo-info 命令"""
    try:
        org, repo_name = _parse_repo_id(args.repo_id)
        client = _get_client(args)

        repo = client.get_repository_info(
            organization=org,
            repo_type=args.repo_type,
            repo_name=repo_name,
        )
        print(f"仓库名称: {repo.name}")
        print(f"组织: {repo.organization}")
        print(f"所有者: {repo.owner}")
        print(f"创建者: {repo.creator}")
        print(f"类型: {repo.type}")
        print(f"可见性: {repo.visibility}")
        if repo.description:
            print(f"描述: {repo.description}")
        if repo.genealogy:
            print(f"模型血缘: {repo.genealogy}")
        if repo.metadata:
            print(f"元数据: {repo.metadata}")
        if repo.annotations:
            print(f"注解: {repo.annotations}")
        return 0
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_branch_create(args):
    """处理 branch-create 命令"""
    try:
        org, repo_name = _parse_repo_id(args.repo_id)
        client = _get_client(args)

        client.create_branch(
            organization=org,
            repo_type=args.repo_type,
            repo_name=repo_name,
            branch_name=args.branch,
            from_branch=args.from_branch,
        )
        print(f"分支创建成功: {args.branch}")
        return 0
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_branch_delete(args):
    """处理 branch-delete 命令"""
    try:
        org, repo_name = _parse_repo_id(args.repo_id)
        client = _get_client(args)

        # 确认删除
        if not args.yes:
            confirm = input(f"确定要删除分支 {args.branch} 吗？[y/N]: ")
            if confirm.lower() != 'y':
                print("已取消删除")
                return 0

        client.delete_branch(
            organization=org,
            repo_type=args.repo_type,
            repo_name=repo_name,
            branch_name=args.branch,
        )
        print(f"分支删除成功: {args.branch}")
        return 0
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_branch_list(args):
    """处理 branch-list 命令"""
    try:
        org, repo_name = _parse_repo_id(args.repo_id)
        client = _get_client(args)

        refs = client.get_repository_refs(
            organization=org,
            repo_type=args.repo_type,
            repo_name=repo_name,
        )

        if not refs:
            print("没有找到分支")
            return 0

        print(f"仓库 {org}/{repo_name} 的分支列表：")
        for ref in refs:
            commit_hash = ref.hash[:8] if ref.hash else 'N/A'
            default_mark = " (默认)" if ref.is_default else ""
            print(f"  - {ref.name} [{ref.type}] (commit: {commit_hash}){default_mark}")
        return 0
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def _add_common_args(parser):
    """添加通用参数"""
    parser.add_argument(
        "--base-url",
        help="Hub API 地址（默认从 MOHA_ENDPOINT 环境变量获取）",
    )
    parser.add_argument(
        "--token",
        help="认证令牌（或设置 MOHA_TOKEN 环境变量）",
    )
    parser.add_argument(
        "--username",
        help="用户名（或设置 MOHA_USERNAME 环境变量）",
    )
    parser.add_argument(
        "--password",
        help="密码（或设置 MOHA_PASSWORD 环境变量）",
    )


def _add_encryption_args(parser):
    """添加加密相关参数"""
    parser.add_argument(
        "--encrypt", "-e",
        action="store_true",
        help="启用模型文件加密",
    )
    parser.add_argument(
        "--encryption-password",
        help="加密密码（或设置 MOHA_ENCRYPTION_PASSWORD 环境变量）",
    )
    parser.add_argument(
        "--algorithm", "-a",
        choices=["AES", "SM4"],
        default="AES",
        help="加密算法（默认: AES）",
    )


def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog="moha",
        description="晓石 AI Hub 命令行工具 - 模型及数据集管理",
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # ========== 上传文件夹命令 ==========
    upload_folder_parser = subparsers.add_parser(
        "upload",
        help="上传文件夹到仓库",
    )
    upload_folder_parser.add_argument("folder", help="要上传的文件夹路径")
    upload_folder_parser.add_argument("repo_id", help="仓库 ID（格式: 组织/仓库名）")
    upload_folder_parser.add_argument(
        "--repo-type", "-t",
        default="models",
        choices=["models", "datasets"],
        help="仓库类型（默认: models）",
    )
    upload_folder_parser.add_argument(
        "--revision", "-r",
        default="main",
        help="上传到的分支（默认: main）",
    )
    upload_folder_parser.add_argument(
        "--message", "-m",
        help="提交信息",
    )
    upload_folder_parser.add_argument(
        "--ignore", "-i",
        action="append",
        help="忽略的文件模式（可多次指定）",
    )
    upload_folder_parser.add_argument(
        "--temp-dir",
        help="加密临时目录",
    )
    _add_common_args(upload_folder_parser)
    _add_encryption_args(upload_folder_parser)
    upload_folder_parser.set_defaults(func=cmd_upload_folder)

    # ========== 上传文件命令 ==========
    upload_file_parser = subparsers.add_parser(
        "upload-file",
        help="上传单个文件到仓库",
    )
    upload_file_parser.add_argument("file", help="要上传的文件路径")
    upload_file_parser.add_argument("repo_id", help="仓库 ID（格式: 组织/仓库名）")
    upload_file_parser.add_argument(
        "--path-in-repo", "-p",
        help="文件在仓库中的路径（默认: 文件名）",
    )
    upload_file_parser.add_argument(
        "--repo-type", "-t",
        default="models",
        choices=["models", "datasets"],
        help="仓库类型（默认: models）",
    )
    upload_file_parser.add_argument(
        "--revision", "-r",
        default="main",
        help="上传到的分支（默认: main）",
    )
    upload_file_parser.add_argument(
        "--message", "-m",
        help="提交信息",
    )
    _add_common_args(upload_file_parser)
    _add_encryption_args(upload_file_parser)
    upload_file_parser.set_defaults(func=cmd_upload_file)

    # ========== 下载仓库命令 ==========
    download_repo_parser = subparsers.add_parser(
        "download",
        help="下载整个仓库",
    )
    download_repo_parser.add_argument("repo_id", help="仓库 ID（格式: 组织/仓库名）")
    download_repo_parser.add_argument(
        "--local-dir", "-o",
        help="保存文件的目录",
    )
    download_repo_parser.add_argument(
        "--repo-type", "-t",
        default="models",
        choices=["models", "datasets"],
        help="仓库类型（默认: models）",
    )
    download_repo_parser.add_argument(
        "--revision", "-r",
        help="要下载的分支/标签/提交（默认: main）",
    )
    download_repo_parser.add_argument(
        "--include",
        action="append",
        help="包含的文件模式（可多次指定）",
    )
    download_repo_parser.add_argument(
        "--ignore", "-i",
        action="append",
        help="忽略的文件模式（可多次指定）",
    )
    download_repo_parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="禁用进度条",
    )
    _add_common_args(download_repo_parser)
    download_repo_parser.set_defaults(func=cmd_download_repo)

    # ========== 下载文件命令 ==========
    download_file_parser = subparsers.add_parser(
        "download-file",
        help="从仓库下载单个文件",
    )
    download_file_parser.add_argument("repo_id", help="仓库 ID（格式: 组织/仓库名）")
    download_file_parser.add_argument("filename", help="仓库中的文件路径")
    download_file_parser.add_argument(
        "--local-dir", "-o",
        help="保存文件的目录（默认: 当前目录）",
    )
    download_file_parser.add_argument(
        "--repo-type", "-t",
        default="models",
        choices=["models", "datasets"],
        help="仓库类型（默认: models）",
    )
    download_file_parser.add_argument(
        "--revision", "-r",
        help="要下载的分支/标签/提交（默认: main）",
    )
    download_file_parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="禁用进度条",
    )
    _add_common_args(download_file_parser)
    download_file_parser.set_defaults(func=cmd_download_file)

    # ========== 登录命令 ==========
    login_parser = subparsers.add_parser(
        "login",
        help="登录并保存 Token",
    )
    login_parser.add_argument(
        "--username", "-u",
        help="用户名（不指定则交互式输入）",
    )
    login_parser.add_argument(
        "--password", "-p",
        help="密码（不指定则交互式输入）",
    )
    login_parser.add_argument(
        "--base-url",
        help="Hub API 地址（默认从 MOHA_ENDPOINT 环境变量获取）",
    )
    login_parser.add_argument(
        "--token-dir",
        help="Token 存储目录（默认: ~/.moha）",
    )
    login_parser.set_defaults(func=cmd_login)

    # ========== 退出登录命令 ==========
    logout_parser = subparsers.add_parser(
        "logout",
        help="退出登录并删除 Token",
    )
    logout_parser.add_argument(
        "--token-dir",
        help="Token 存储目录（默认: ~/.moha）",
    )
    logout_parser.set_defaults(func=cmd_logout)

    # ========== 查看当前登录状态命令 ==========
    whoami_parser = subparsers.add_parser(
        "whoami",
        help="查看当前登录状态",
    )
    whoami_parser.add_argument(
        "--token-dir",
        help="Token 存储目录（默认: ~/.moha）",
    )
    whoami_parser.set_defaults(func=cmd_whoami)

    # ========== 创建仓库命令 ==========
    repo_create_parser = subparsers.add_parser(
        "repo-create",
        help="创建仓库",
    )
    repo_create_parser.add_argument("repo_id", help="仓库 ID（格式: 组织/仓库名）")
    repo_create_parser.add_argument(
        "--repo-type", "-t",
        default="models",
        choices=["models", "datasets"],
        help="仓库类型（默认: models）",
    )
    repo_create_parser.add_argument(
        "--description", "-d",
        help="仓库描述",
    )
    repo_create_parser.add_argument(
        "--visibility", "-v",
        default="internal",
        choices=["public", "internal", "private"],
        help="可见性（默认: internal）",
    )
    repo_create_parser.add_argument(
        "--license",
        action="append",
        help="许可证（可多次指定）",
    )
    repo_create_parser.add_argument(
        "--tasks",
        action="append",
        help="任务类型（可多次指定）",
    )
    repo_create_parser.add_argument(
        "--languages",
        action="append",
        help="语言（可多次指定）",
    )
    repo_create_parser.add_argument(
        "--tags",
        action="append",
        help="标签（可多次指定）",
    )
    repo_create_parser.add_argument(
        "--frameworks",
        action="append",
        help="框架（可多次指定）",
    )
    repo_create_parser.add_argument(
        "--base-model",
        action="append",
        help="基础模型（可多次指定，格式: 组织/模型名）",
    )
    repo_create_parser.add_argument(
        "--relationship",
        choices=["adapter", "finetune", "quantized", "merge", "repackage"],
        help="与基础模型的关系",
    )
    _add_common_args(repo_create_parser)
    repo_create_parser.set_defaults(func=cmd_repo_create)

    # ========== 更新仓库命令 ==========
    repo_update_parser = subparsers.add_parser(
        "repo-update",
        help="更新仓库",
    )
    repo_update_parser.add_argument("repo_id", help="仓库 ID（格式: 组织/仓库名）")
    repo_update_parser.add_argument(
        "--repo-type", "-t",
        default="models",
        choices=["models", "datasets"],
        help="仓库类型（默认: models）",
    )
    repo_update_parser.add_argument(
        "--description", "-d",
        help="仓库描述",
    )
    repo_update_parser.add_argument(
        "--visibility", "-v",
        choices=["public", "internal", "private"],
        help="可见性",
    )
    repo_update_parser.add_argument(
        "--license",
        action="append",
        help="许可证（可多次指定）",
    )
    repo_update_parser.add_argument(
        "--tasks",
        action="append",
        help="任务类型（可多次指定）",
    )
    repo_update_parser.add_argument(
        "--languages",
        action="append",
        help="语言（可多次指定）",
    )
    repo_update_parser.add_argument(
        "--tags",
        action="append",
        help="标签（可多次指定）",
    )
    repo_update_parser.add_argument(
        "--frameworks",
        action="append",
        help="框架（可多次指定）",
    )
    repo_update_parser.add_argument(
        "--base-model",
        action="append",
        help="基础模型（可多次指定，格式: 组织/模型名）",
    )
    repo_update_parser.add_argument(
        "--relationship",
        choices=["adapter", "finetune", "quantized", "merge", "repackage"],
        help="与基础模型的关系",
    )
    _add_common_args(repo_update_parser)
    repo_update_parser.set_defaults(func=cmd_repo_update)

    # ========== 删除仓库命令 ==========
    repo_delete_parser = subparsers.add_parser(
        "repo-delete",
        help="删除仓库",
    )
    repo_delete_parser.add_argument("repo_id", help="仓库 ID（格式: 组织/仓库名）")
    repo_delete_parser.add_argument(
        "--repo-type", "-t",
        default="models",
        choices=["models", "datasets"],
        help="仓库类型（默认: models）",
    )
    repo_delete_parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="跳过确认提示",
    )
    _add_common_args(repo_delete_parser)
    repo_delete_parser.set_defaults(func=cmd_repo_delete)

    # ========== 查看仓库信息命令 ==========
    repo_info_parser = subparsers.add_parser(
        "repo-info",
        help="查看仓库信息",
    )
    repo_info_parser.add_argument("repo_id", help="仓库 ID（格式: 组织/仓库名）")
    repo_info_parser.add_argument(
        "--repo-type", "-t",
        default="models",
        choices=["models", "datasets"],
        help="仓库类型（默认: models）",
    )
    _add_common_args(repo_info_parser)
    repo_info_parser.set_defaults(func=cmd_repo_info)

    # ========== 创建分支命令 ==========
    branch_create_parser = subparsers.add_parser(
        "branch-create",
        help="创建分支",
    )
    branch_create_parser.add_argument("repo_id", help="仓库 ID（格式: 组织/仓库名）")
    branch_create_parser.add_argument("branch", help="要创建的分支名称")
    branch_create_parser.add_argument(
        "--from", "-f",
        dest="from_branch",
        default="main",
        help="基于哪个分支创建（默认: main）",
    )
    branch_create_parser.add_argument(
        "--repo-type", "-t",
        default="models",
        choices=["models", "datasets"],
        help="仓库类型（默认: models）",
    )
    _add_common_args(branch_create_parser)
    branch_create_parser.set_defaults(func=cmd_branch_create)

    # ========== 删除分支命令 ==========
    branch_delete_parser = subparsers.add_parser(
        "branch-delete",
        help="删除分支",
    )
    branch_delete_parser.add_argument("repo_id", help="仓库 ID（格式: 组织/仓库名）")
    branch_delete_parser.add_argument("branch", help="要删除的分支名称")
    branch_delete_parser.add_argument(
        "--repo-type", "-t",
        default="models",
        choices=["models", "datasets"],
        help="仓库类型（默认: models）",
    )
    branch_delete_parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="跳过确认提示",
    )
    _add_common_args(branch_delete_parser)
    branch_delete_parser.set_defaults(func=cmd_branch_delete)

    # ========== 列出分支命令 ==========
    branch_list_parser = subparsers.add_parser(
        "branch-list",
        help="列出仓库的所有分支",
    )
    branch_list_parser.add_argument("repo_id", help="仓库 ID（格式: 组织/仓库名）")
    branch_list_parser.add_argument(
        "--repo-type", "-t",
        default="models",
        choices=["models", "datasets"],
        help="仓库类型（默认: models）",
    )
    _add_common_args(branch_list_parser)
    branch_list_parser.set_defaults(func=cmd_branch_list)

    return parser


def main():
    """主入口"""
    parser = create_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

