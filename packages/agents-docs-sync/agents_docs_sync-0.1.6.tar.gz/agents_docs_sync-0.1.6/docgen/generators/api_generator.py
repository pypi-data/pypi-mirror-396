"""
APIドキュメント生成モジュール
"""

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ..detectors.detector_patterns import DetectorPatterns
from ..models.api import APIInfo
from ..models.project import ProjectInfo
from ..utils.cache import CacheManager
from ..utils.markdown_utils import (
    GENERATION_TIMESTAMP_LABEL,
    SECTION_SEPARATOR,
    get_current_timestamp,
)
from .base_generator import BaseGenerator
from .parsers.generic_parser import GenericParser
from .parsers.js_parser import JSParser
from .parsers.python_parser import PythonParser

if TYPE_CHECKING:
    from .parsers.base_parser import BaseParser


class APIGenerator(BaseGenerator):
    """APIドキュメント生成クラス"""

    def __init__(
        self,
        project_root: Path,
        languages: list[str],
        config: dict[str, Any],
        package_managers: dict[str, str] | None = None,
    ):
        """
        初期化

        Args:
            project_root: プロジェクトのルートディレクトリ
            languages: 検出された言語のリスト
            config: 設定辞書
            package_managers: 検出されたパッケージマネージャの辞書
        """
        super().__init__(project_root, languages, config, package_managers)

        # キャッシュマネージャーの初期化
        cache_enabled = self.config.get("cache", {}).get("enabled", True)
        self.cache_manager = (
            CacheManager(project_root=self.project_root, enabled=cache_enabled)
            if cache_enabled
            else None
        )

    def _get_mode_key(self) -> str:
        return "api_mode"

    def _get_output_key(self) -> str:
        return "api_doc"

    def _get_document_type(self) -> str:
        return "APIドキュメント"

    def _get_structured_model(self) -> Any:
        # 現在は構造化出力を使用していないためNoneを返す
        return None

    def _create_llm_prompt(self, project_info: ProjectInfo) -> str:
        # 現在はLLM生成を使用していないため空文字を返す
        return ""

    def _generate_template(self, project_info: ProjectInfo) -> str:
        # テンプレート生成の代わりにパーサーベースの生成を行う
        # BaseGeneratorのgenerateフローから呼ばれる場合、ここが実質的な生成ロジックの一部になる
        # ただし、API生成は特殊なので、_generate_markdownで処理する
        return ""

    def _get_project_overview_section(self, content: str) -> str:
        return ""

    def _convert_structured_data_to_markdown(
        self, structured_data: Any, project_info: ProjectInfo
    ) -> str:
        return ""

    def _generate_markdown(self, project_info: ProjectInfo) -> str:
        """
        API情報からマークダウンを生成

        Args:
            project_info: プロジェクト情報（このクラスでは主に使用しないが、インターフェースとして必要）

        Returns:
            マークダウンの文字列
        """
        # 各言語のパーサーでAPI情報を収集
        all_apis = []
        parsers = self._get_parsers()

        # 除外ディレクトリとファイルパターンを設定
        exclude_dirs = self.config.get("exclude", {}).get(
            "directories",
            list(DetectorPatterns.EXCLUDE_DIRS) + ["venv"],
        )

        # キャッシュの使用設定
        use_cache = self.config.get("cache", {}).get("enabled", True)

        # 一度だけファイルスキャンを行い、結果を各パーサーに共有（重複スキャンを避ける）
        # すべてのパーサーの拡張子を集めて一度だけスキャン
        all_extensions = set()
        for parser in parsers:
            all_extensions.update(parser.get_supported_extensions())

        shared_files_to_parse = self._scan_project_files(
            exclude_dirs=exclude_dirs,
            extensions=all_extensions,
        )

        # 各パーサーで解析（ファイルスキャン結果を共有）
        for i, parser in enumerate(parsers):
            # 最後のパーサー以外はキャッシュ保存をスキップ（最後に一度だけ保存）
            skip_cache_save = i < len(parsers) - 1

            apis = parser.parse_project(
                exclude_dirs=exclude_dirs,
                use_cache=use_cache,
                cache_manager=self.cache_manager,
                files_to_parse=shared_files_to_parse,
                skip_cache_save=skip_cache_save,
            )
            all_apis.extend(apis)

        # すべてのパーサー実行後に一度だけキャッシュを保存
        if use_cache and self.cache_manager:
            self.cache_manager.save()

        # API情報をソート（ファイル名、行番号順）
        all_apis.sort(key=lambda x: (x["file"], x["line"]))

        return self._render_api_markdown(all_apis)

    def _render_api_markdown(self, apis: list[APIInfo]) -> str:
        """
        API情報のリストからマークダウンをレンダリング

        Args:
            apis: API情報のリスト

        Returns:
            マークダウン文字列
        """
        lines = []

        # ヘッダー
        lines.append("# API ドキュメント")
        lines.append("")
        lines.append(f"{GENERATION_TIMESTAMP_LABEL} {get_current_timestamp()}")
        lines.append("")
        lines.append(SECTION_SEPARATOR)
        lines.append("")

        if not apis:
            lines.append("APIが見つかりませんでした。")
            return "\n".join(lines)

        # ファイルごとにグループ化
        current_file = None
        for api in apis:
            file_path = api["file"]

            # 新しいファイルセクション
            if file_path != current_file:
                if current_file is not None:
                    lines.append("")
                current_file = file_path
                lines.append(f"## {file_path}")
                lines.append("")

            # API情報を出力
            lines.append(f"### {api['name']}")
            lines.append("")
            lines.append(f"**型**: `{api['type']}`")
            lines.append("")
            lines.append("**シグネチャ**:")
            lines.append("```")
            lines.append(api["signature"])
            lines.append("```")
            lines.append("")

            if api["docstring"]:
                lines.append("**説明**:")
                lines.append("")
                # docstringを整形（インデントを調整）
                docstring_lines = api["docstring"].split("\n")
                for doc_line in docstring_lines:
                    lines.append(doc_line)
                lines.append("")
            else:
                lines.append("*説明なし*")
                lines.append("")

            lines.append(f"*定義場所: {file_path}:{api['line']}*")
            lines.append("")
            lines.append(SECTION_SEPARATOR)
            lines.append("")

        return "\n".join(lines)

    def _get_parsers(self) -> list["BaseParser"]:
        """
        言語に応じたパーサーのリストを取得

        Returns:
            パーサーのリスト
        """
        parsers = []

        for lang in self.languages:
            if lang == "python":
                parsers.append(PythonParser(self.project_root))
            elif lang in ["javascript", "typescript"]:
                parsers.append(JSParser(self.project_root))
            else:
                parsers.append(GenericParser(self.project_root, language=lang))

        return parsers

    def _scan_project_files(
        self, exclude_dirs: list[str], extensions: set[str]
    ) -> list[tuple[Path, Path]]:
        """
        プロジェクトファイルを一度だけスキャン（複数パーサー間で共有）

        Args:
            exclude_dirs: 除外するディレクトリ
            extensions: スキャン対象の拡張子セット

        Returns:
            (絶対パス, 相対パス)のタプルのリスト
        """
        files_to_parse = []
        project_root_resolved = self.project_root.resolve()
        extensions_set = {ext.lower() for ext in extensions}

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

                # パスベースの除外チェック
                try:
                    rel_path = root_path.relative_to(project_root_resolved)
                    if any(excluded in rel_path.parts for excluded in exclude_dirs):
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
                            continue

                        # シンボリックリンクのチェック
                        if file_path.is_symlink():
                            continue

                        files_to_parse.append((file_path, file_path_relative))
                    except (OSError, PermissionError):
                        # ファイルアクセスエラーは無視して続行
                        continue
        except (OSError, PermissionError) as e:
            from ..utils.logger import get_logger

            logger = get_logger("api_generator")
            logger.warning(f"プロジェクトの走査中にエラーが発生しました: {e}")

        return files_to_parse
