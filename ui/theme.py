"""Theme colors, styles, and aesthetic palettes."""

from rich.text import Text

class Theme:
    """Cohesive pastel dark theme colors across the application."""
    PRIMARY = "#27d2ed"       # Cyan
    SECONDARY = "#af91f6"     # Lavender
    ACCENT = "#ed8fba"        # Rose Pink
    SUCCESS = "#4bdd7f"       # Emerald Green
    WARNING = "#facc15"       # Warm Yellow
    DANGER = "#f87070"        # Coral Red
    MUTED = "#8a99a8"         # Muted Slate
    TEXT_DARK = "#121316"     # Dark text on bright badge pills
    TEXT_LIGHT = "#f3f4f6"    # Crisp light text
    BORDER = "#27d2ed"

    @classmethod
    def apply_title_gradient(cls, text: str) -> Text:
        """Applies a smooth linear pastel gradient from lavender (#af91f6) to rose (#ed8fba)."""
        t = Text()
        n = len(text)
        for i, ch in enumerate(text):
            ratio = i / max(1, n - 1)
            r = int(175 + (237 - 175) * ratio)
            g = int(145 + (143 - 145) * ratio)
            b = int(246 + (186 - 246) * ratio)
            t.append(ch, style=f"bold #{r:02x}{g:02x}{b:02x}")
        return t
