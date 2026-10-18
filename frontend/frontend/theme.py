"""Shared BeautyTime palette and typography."""

import reflex as rx

COLORS = {
    "accent": "#B4235A",
    "accent_hover": "#941C49",
    "background": "#F8F7F5",
    "border": "#E7E2DD",
    "error": "#B4233C",
    "muted": "#68615E",
    "surface": "#FFFFFF",
    "text": "#373230",
}

SHADOWS = {
    "card": "0 16px 48px rgba(55, 50, 48, 0.09)",
    "tile": "0 8px 24px rgba(55, 50, 48, 0.05)",
}

FONT_FAMILY = '"Inter", sans-serif'
RADIX_ACCENT = "ruby"
FONT_STYLESHEET = (
    "https://fonts.googleapis.com/css2?"
    "family=Inter:wght@400;500;600;700;800&display=swap"
)

GLOBAL_STYLES = {
    "font_family": FONT_FAMILY,
    "color": COLORS["text"],
    rx.input: {
        "min_height": "52px",
        "border": f"1px solid {COLORS['border']}",
        "border_radius": "12px",
        "font_family": FONT_FAMILY,
    },
    rx.button: {"font_family": FONT_FAMILY},
    rx.link: {"color": COLORS["accent"]},
}

FORM_FIELD_STYLE = {
    "height": "52px",
    "border": f"1px solid {COLORS['border']}",
    "border_radius": "12px",
    "font_family": FONT_FAMILY,
}
