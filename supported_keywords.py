"""
supported_keywords.py
Stores programming language keywords for autocomplete and syntax highlighting.
"""


class SupportedKeywords:
    SUPPORTED_LANGUAGES = [".cpp", ".java"]

    JAVA_KEYWORDS = [
        "abstract", "assert", "boolean", "break", "byte", "case", "catch",
        "char", "class", "const", "continue", "default", "do", "double",
        "else", "extends", "false", "final", "finally", "float", "for",
        "goto", "if", "implements", "import", "instanceof", "int", "System",
        "out", "print()", "println()", "new", "null", "package", "private",
        "protected", "public", "interface", "long", "native", "return",
        "short", "static", "strictfp", "super", "switch", "synchronized",
        "this", "throw", "throws", "transient", "true", "try", "void",
        "volatile", "while", "String"
    ]

    CPP_KEYWORDS = [
        "auto", "const", "double", "float", "int", "short", "struct",
        "unsigned", "break", "continue", "else", "for", "long", "signed",
        "switch", "void", "case", "default", "enum", "goto", "register",
        "sizeof", "typedef", "volatile", "char", "do", "extern", "if",
        "return", "static", "union", "while", "asm", "dynamic_cast",
        "namespace", "reinterpret_cast", "try", "bool", "explicit", "new",
        "static_cast", "typeid", "catch", "false", "operator", "template",
        "typename", "class", "friend", "private", "this", "using",
        "const_cast", "inline", "public", "throw", "virtual", "delete",
        "mutable", "protected", "true", "wchar_t"
    ]

    BRACKETS = ["{", "("]
    BRACKET_COMPLETIONS = ["}", ")"]

    def get_supported_languages(self):
        return self.SUPPORTED_LANGUAGES

    def get_java_keywords(self):
        return self.JAVA_KEYWORDS

    def get_cpp_keywords(self):
        return self.CPP_KEYWORDS

    def get_brackets(self):
        return self.BRACKETS

    def get_bracket_completions(self):
        return self.BRACKET_COMPLETIONS

    def set_keywords(self, keyword_list):
        """Returns a sorted list of keywords (mirrors Java setKeywords)."""
        return sorted(list(keyword_list))
