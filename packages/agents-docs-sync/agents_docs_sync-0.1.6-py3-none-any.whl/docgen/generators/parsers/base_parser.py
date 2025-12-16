"""
パーサーのベースクラス

Template Methodパターンを使用して、コード解析の共通フローを定義します。
サブクラスでは `_parse_to_ast` と `_extract_elements` を実装します。
"""

from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from ...models import APIInfo
from ...utils.exceptions import ParseError
from ...utils.logger import get_logger

if TYPE_CHECKING:
    from ...utils.cache import CacheManager

logger = get_logger("parser")


class BaseParser(ABC):
    """コード解析のベースクラス

    Template Methodパターンにより、解析フローの共通部分を定義します。
    サブクラスでは以下の抽象メソッドを実装します：
    - `_parse_to_ast`: コンテンツをASTにパース
    - `_extract_elements`: ASTからAPI要素を抽出
    - `get_supported_extensions`: サポートする拡張子を返す

    Attributes:
        PARSER_TYPE: パーサーの種類を示すクラス変数
    """

    PARSER_TYPE: ClassVar[str] = "generic"

    def __init__(self, project_root: Path):
        """
        初期化

        Args:
            project_root: プロジェクトのルートディレクトリ
        """
        self.project_root: Path = project_root

    def parse_file(self, file_path: Path) -> list[APIInfo]:
        """
        ファイルを解析してAPI情報を抽出 (Template Method)

        Args:
            file_path: 解析するファイルのパス

        Returns:
            API情報のリスト
        """
        try:
            content = self._read_file(file_path)
            ast = self._parse_to_ast(content, file_path)
            elements = self._extract_elements(ast, file_path)
            return self._post_process(elements)
        except ParseError:
            raise
        except Exception as e:
            raise ParseError(
                message=f"{file_path} の解析に失敗しました",
                file_path=str(file_path),
                language=self.PARSER_TYPE,
                details=str(e),
            ) from e

    def _read_file(self, file_path: Path) -> str:
        """ファイルを読み込む"""
        with open(file_path, encoding="utf-8") as f:
            return f.read()

    @abstractmethod
    def _parse_to_ast(self, content: str, file_path: Path) -> Any:
        """ASTにパース（サブクラスで実装）"""
        pass

    @abstractmethod
    def _extract_elements(self, ast: Any, file_path: Path) -> list[APIInfo]:
        """要素を抽出（サブクラスで実装）"""
        pass

    def _post_process(self, elements: list[APIInfo]) -> list[APIInfo]:
        """後処理（オプション）"""
        return elements

    @abstractmethod
    def get_supported_extensions(self) -> list[str]:
        """
        サポートするファイル拡張子を返す

        Returns:
            拡張子のリスト（例: ['.py', '.pyw']）
        """
        pass

    def get_parser_type(self) -> str:
        """
        パーサーの種類を返す（キャッシュキーの生成に使用）

        Returns:
            パーサーの種類（例: 'python', 'javascript'）
        """
        return self.PARSER_TYPE

    def parse_project(
        self,
        exclude_dirs: list[str] | None = None,
        use_parallel: bool = True,
        max_workers: int | None = None,
        use_cache: bool = True,
        cache_manager: "CacheManager | None" = None,
        files_to_parse: list[tuple[Path, Path]] | None = None,
        skip_cache_save: bool = False,
    ) -> list[APIInfo]:
        """
        プロジェクト全体を解析

        Args:
            exclude_dirs: 除外するディレクトリ（例: ['.git', 'node_modules']）
            use_parallel: 並列処理を使用するかどうか（デフォルト: True）
            max_workers: 並列処理の最大ワーカー数（Noneの場合は自動）
            use_cache: キャッシュを使用するかどうか（デフォルト: True）
            cache_manager: キャッシュマネージャー（Noneの場合はキャッシュを使用しない）
            files_to_parse: 既にスキャン済みのファイルリスト（Noneの場合は新規スキャン）
            skip_cache_save: キャッシュ保存をスキップするか（デフォルト: False）

        Returns:
            全API情報のリスト
        """
        if exclude_dirs is None:
            from ...detectors.detector_patterns import DetectorPatterns

            exclude_dirs = list(DetectorPatterns.EXCLUDE_DIRS) + ["docgen", "venv"]

        # キャッシュの設定
        effective_use_cache = use_cache and cache_manager is not None
        parser_type = self.get_parser_type()

        all_apis = []
        extensions = self.get_supported_extensions()
        # 拡張子をセットに変換して高速な検索を可能にする
        extensions_set = {ext.lower() for ext in extensions}

        # プロジェクトルートを正規化（絶対パスに変換）
        project_root_resolved = self.project_root.resolve()

        # 解析対象ファイルのリストを収集（os.walkで一度だけ走査）
        # files_to_parseが提供されている場合はそれを使用（重複スキャンを避ける）
        if files_to_parse is None:
            files_to_parse = []
            try:
                for root, dirs, files in os.walk(self.project_root, followlinks=False):
                    root_path = Path(root)

                    # 除外ディレクトリを早期にスキップ（dirsをin-placeで変更）
                    dirs[:] = [
                        d
                        for d in dirs
                        if d not in exclude_dirs
                        and not d.startswith(".")
                        and not d.endswith(".egg-info")
                    ]

                    # パスベースの除外チェック（セット検索でO(1)）
                    try:
                        rel_path = root_path.relative_to(project_root_resolved)
                        # セットのintersectionを使用して高速チェック
                        exclude_dirs_set = set(exclude_dirs)
                        if exclude_dirs_set.intersection(rel_path.parts):
                            dirs[:] = []  # このディレクトリ以下をスキップ
                            continue
                        if any(part.endswith(".egg-info") for part in rel_path.parts):
                            dirs[:] = []  # egg-infoディレクトリ以下をスキップ
                            continue
                    except ValueError:
                        # プロジェクトルート外の場合はスキップ
                        continue

                    # ファイルをチェック
                    for file_name in files:
                        file_path = root_path / file_name

                        # 拡張子をチェック
                        ext = file_path.suffix.lower()
                        if ext not in extensions_set:
                            continue

                        try:
                            # パスの正規化（シンボリックリンクを解決）
                            file_path_resolved = file_path.resolve()

                            # プロジェクトルート外へのアクセスを防止
                            try:
                                file_path_relative = file_path_resolved.relative_to(project_root_resolved)
                            except ValueError:
                                # プロジェクトルート外のファイルはスキップ
                                logger.debug(f"プロジェクトルート外のファイルをスキップ: {file_path}")
                                continue

                            # シンボリックリンクのチェック（オプション: シンボリックリンクをスキップする場合）
                            if file_path.is_symlink():
                                logger.debug(f"シンボリックリンクをスキップ: {file_path}")
                                continue

                            files_to_parse.append((file_path, file_path_relative))
                        except (OSError, PermissionError) as e:
                            # ファイルアクセスエラー（権限エラーなど）は無視して続行
                            logger.debug(f"{file_path} へのアクセスに失敗しました: {e}")
                            continue
            except (OSError, PermissionError) as e:
                logger.warning(f"プロジェクトの走査中にエラーが発生しました: {e}")
        else:
            # 提供されたファイルリストから、このパーサーがサポートする拡張子のファイルのみをフィルタリング
            files_to_parse = [
                (file_path, file_path_relative)
                for file_path, file_path_relative in files_to_parse
                if file_path.suffix.lower() in extensions_set
            ]

        # 並列処理または逐次処理で解析
        # 閾値: ファイル数が5を超える場合、またはCPU数が2以上でファイル数が3を超える場合
        import os as os_module

        cpu_count = os_module.cpu_count() or 1
        parallel_threshold = 3 if cpu_count >= 2 else 5
        if use_parallel and len(files_to_parse) > parallel_threshold:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_file = {
                    executor.submit(
                        self._parse_file_safe,
                        file_path,
                        file_path_relative,
                        cache_manager if effective_use_cache else None,
                        parser_type if effective_use_cache else None,
                    ): (file_path, file_path_relative)
                    for file_path, file_path_relative in files_to_parse
                }

                for future in as_completed(future_to_file):
                    file_path, file_path_relative = future_to_file[future]
                    try:
                        apis = future.result()
                        if apis:
                            all_apis.extend(apis)
                    except Exception as e:
                        logger.warning(f"{file_path} の解析に失敗しました: {e}")
        else:
            # 逐次処理
            for file_path, file_path_relative in files_to_parse:
                try:
                    apis = self._parse_file_safe(
                        file_path,
                        file_path_relative,
                        cache_manager if effective_use_cache else None,
                        parser_type if effective_use_cache else None,
                    )
                    if apis:
                        all_apis.extend(apis)
                except Exception as e:
                    logger.warning(f"{file_path} の解析に失敗しました: {e}")
                    continue

        # キャッシュを保存（skip_cache_saveがFalseの場合のみ）
        if effective_use_cache and cache_manager and not skip_cache_save:
            cache_manager.save()

        return all_apis

    def _parse_file_safe(
        self,
        file_path: Path,
        file_path_relative: Path,
        cache_manager: "CacheManager | None" = None,
        parser_type: str | None = None,
    ) -> list[APIInfo]:
        """
        ファイルを安全に解析（内部メソッド）

        Args:
            file_path: ファイルパス
            file_path_relative: 相対パス
            cache_manager: キャッシュマネージャー（オプション）
            parser_type: パーサーの種類（オプション）

        Returns:
            API情報のリスト
        """
        # キャッシュから結果を取得
        if cache_manager is not None and parser_type is not None:
            cached_result = cache_manager.get_cached_result(file_path, parser_type)
            if cached_result is not None:
                # キャッシュされた結果の浅いコピーを作成（キャッシュ内のデータを変更しないため）
                # 各API情報は辞書なので、浅いコピーで十分（ネストされたリストがある場合は個別にコピー）
                result = []
                for api in cached_result:
                    # 辞書の浅いコピーを作成
                    api_copy = api.copy()
                    # 相対パスを設定
                    api_copy["file"] = str(file_path_relative)
                    # ネストされたリスト（parametersなど）がある場合はコピー
                    if "parameters" in api_copy and api_copy["parameters"] is not None:
                        api_copy["parameters"] = api_copy["parameters"].copy()
                    if "decorators" in api_copy and api_copy["decorators"] is not None:
                        api_copy["decorators"] = api_copy["decorators"].copy()
                    result.append(api_copy)
                return result

        try:
            apis = self.parse_file(file_path)
            for api in apis:
                api["file"] = str(file_path_relative)

            # 結果をキャッシュに保存
            if cache_manager is not None and parser_type is not None:
                cache_manager.set_cached_result(file_path, parser_type, apis)

            return apis
        except Exception as e:
            logger.warning(f"{file_path} の解析に失敗しました: {e}")
            return []
