import re
from pathlib import Path

import polib

import po_translator.api as t_api


class POFileTranslator:
    def __init__(
        self,
        path: Path,
        # The default exclude patterns are for Sphinx directives and
        # bold, italic, double backtick, single backtick, and link markup.
        exclude_patterns: list
        | None = [
            r":\w+(?::\w+)?:`[^`]+`",
            r"\*\*[^\*]+\*\*",
            r"\*[^\*]+\*(?![\*])",
            r"\`\`[^\`]+\`\`",
            r"\`[^\`]+\`(?![\`])",
            r".*?[^\w]_(?![_])",
            r".*?[^\w]__",
        ],
        api: str = "deepl",
        source_lang: str = "auto",
        target_lang: str = "en",
        proxies: dict[str, str] | None = None,
    ):
        self._pofile = polib.pofile(Path(path).as_posix())
        self._patterns = (
            None
            if not exclude_patterns
            else [re.compile(pattern) for pattern in exclude_patterns]
        )
        self._api = t_api.Translator(api, source_lang, target_lang, proxies)

    def __protect_sphinx_directives(self, source_text: str) -> tuple[dict | None, str]:
        if self._patterns is None or not any(
            [char in source_text for char in ["`", "*", "_"]]
        ):
            return None, source_text

        directive_placeholders: dict[str, str] = {}
        temp_text = source_text
        for index, exp in enumerate(self._patterns):
            matches = exp.findall(temp_text)
            for match in matches:
                placeholder = f"XASDF{str(index).zfill(2)}"
                temp_text = temp_text.replace(match, placeholder)
                directive_placeholders[placeholder] = match
        return directive_placeholders, temp_text

    def __undo_sphinx_directives(
        self, directive_placeholders: dict[str, str], translated_text: str
    ) -> str:
        if directive_placeholders is None:
            return translated_text

        for placeholder, match in directive_placeholders.items():
            index = translated_text.find(placeholder)
            try:
                if translated_text[index + len(placeholder)].isalnum() and index != -1:
                    translated_text = translated_text.replace(placeholder, match + " ")
                    continue
            except IndexError:
                pass
            translated_text = translated_text.replace(placeholder, match)
        return translated_text

    def __translate_func(self, entry: polib.POEntry) -> None:
        directive_placeholders, temp_text = self.__protect_sphinx_directives(
            entry.msgid
        )
        translated_text = self._api.translate(temp_text)
        entry.msgstr = self.__undo_sphinx_directives(
            directive_placeholders, translated_text
        )

    def translate(
        self, skip_translated: bool = False, retranslate_fuzzy: bool = False
    ) -> None:
        for entry in self._pofile:
            if not skip_translated or not entry.translated():
                if retranslate_fuzzy or not entry.fuzzy:
                    self.__translate_func(entry)
                    entry.fuzzy = False
            elif retranslate_fuzzy and entry.fuzzy:
                self.__translate_func(entry)
                entry.fuzzy = False

    def save(self) -> None:
        self._pofile.save()
