"""Internationalization manager utility."""


class I18nManager:
    """Manager for internationalization support."""

    def __init__(self, default_lang: str = "en") -> None:
        self.default_lang = default_lang
        self.current_lang = default_lang
        self.translations: dict[str, dict[str, str]] = {}
        self._load_default_translations()

    def _load_default_translations(self) -> None:
        """Load default translations."""
        # Default translations for initenv module
        default_translations = {
            "git_init_start": {
                "en": "Initializing Git repository...",
                "zh": "初始化Git仓库...",
            },
            "git_init_success": {
                "en": "✓ Git repository initialized",
                "zh": "✓ Git仓库初始化完成",
            },
            "git_init_skip": {
                "en": "Git repository already exists, skipping initialization",
                "zh": "Git仓库已存在，跳过初始化",
            },
            "git_init_fail": {
                "en": "Warning: Failed to initialize Git repository",
                "zh": "警告: 初始化Git仓库失败",
            },
            "project_structure_start": {
                "en": "Setting up project structure...",
                "zh": "设置项目结构...",
            },
            "project_structure_success": {
                "en": "✓ Project structure created successfully",
                "zh": "✓ 项目结构创建成功",
            },
            "project_structure_fail": {
                "en": "Warning: Failed to setup project structure",
                "zh": "警告: 设置项目结构失败",
            },
            "rust_init_start": {
                "en": "Initializing Rust environment...",
                "zh": "初始化Rust环境...",
            },
            "rust_init_success": {
                "en": "✓ Rust project initialized successfully",
                "zh": "✓ Rust项目初始化成功",
            },
            "rust_init_fail": {
                "en": "Warning: Failed to initialize Rust environment",
                "zh": "警告: 初始化Rust环境失败",
            },
            "venv_create_start": {
                "en": "Creating virtual environment...",
                "zh": "创建虚拟环境...",
            },
            "venv_create_success": {
                "en": "✓ Virtual environment created successfully",
                "zh": "✓ 虚拟环境创建成功",
            },
            "venv_create_fail": {
                "en": "Warning: Failed to create virtual environment",
                "zh": "警告: 创建虚拟环境失败",
            },
            "init_complete": {
                "en": "Project environment initialization completed!",
                "zh": "项目环境初始化完成!",
            },
        }

        for key, translations in default_translations.items():
            self.add_translation(key, translations)

    def add_translation(self, key: str, translations: dict[str, str]) -> None:
        """Add translation for a key."""
        self.translations[key] = translations

    def set_language(self, lang: str) -> None:
        """Set current language."""
        self.current_lang = lang

    def get_text(self, key: str, lang: str | None = None) -> str:
        """Get translated text by key."""
        if key not in self.translations:
            return key

        target_lang = lang or self.current_lang
        translations = self.translations[key]

        if target_lang in translations:
            return translations[target_lang]

        if self.default_lang in translations:
            return translations[self.default_lang]

        # Return first available translation
        if translations:
            return next(iter(translations.values()))

        return key

    def t(self, key: str, lang: str | None = None) -> str:
        """Shortcut for get_text."""
        return self.get_text(key, lang)
