"""Shared BeautyTime design tokens and component styles."""

import reflex as rx

COLORS = {
    "background": "#F6F1EA",
    "linen": "#FCFAF6",
    "surface": "#FFFEFC",
    "text": "#2E2620",
    "muted": "#75675C",
    "accent": "#4A3A2E",
    "accent_hover": "#382B22",
    "accent_text": "#4A3A2E",
    "primary_foreground": "#FAF6F0",
    "secondary": "#EBE1D5",
    "sand": "#DDCDB9",
    "detail": "#BF9C72",
    "border": "#E6DCD0",
    "input": "#DED3C6",
    "success": "#2F6648",
    "success_soft": "#E6F2EA",
    "warning": "#8A6224",
    "warning_soft": "#F7EEDA",
    "error": "#9A3B42",
    "error_soft": "#FAE9EA",
    "muted_brand": "#75675C",
}

SHADOWS = {
    "soft": (
        "0 1px 2px rgba(46, 38, 32, 0.04), "
        "0 4px 14px -6px rgba(46, 38, 32, 0.08)"
    ),
    "card": (
        "0 1px 2px rgba(46, 38, 32, 0.04), "
        "0 18px 40px -18px rgba(46, 38, 32, 0.16)"
    ),
    "lift": (
        "0 2px 4px rgba(46, 38, 32, 0.05), "
        "0 26px 50px -20px rgba(46, 38, 32, 0.24)"
    ),
    "button": (
        "inset 0 1px 0 rgba(255, 255, 255, 0.12), "
        "0 8px 18px -8px rgba(46, 38, 32, 0.45)"
    ),
    "focus_input": "0 0 0 4px rgba(191, 156, 114, 0.25)",
    "tile": (
        "0 1px 2px rgba(46, 38, 32, 0.04), "
        "0 4px 14px -6px rgba(46, 38, 32, 0.08)"
    ),
}

FONT_FAMILY = '"Manrope", ui-sans-serif, system-ui, sans-serif'
HEADING_FONT_FAMILY = '"Cormorant Garamond", Georgia, serif'
RADIX_ACCENT = "brown"
FONT_STYLESHEET = (
    "https://fonts.googleapis.com/css2?"
    "family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500&"
    "family=Manrope:wght@400;500;600;700&display=swap"
)

MAX_WIDTHS = {
    "auth": "520px",
    "platform_login": "480px",
    "client": "720px",
    "admin": "820px",
    "home": "900px",
    "platform": "1100px",
}

PAGE_SECTION_GAP = rx.breakpoints(initial="6", md="8")
CARD_DEFAULT_PADDING = rx.breakpoints(initial="24px", sm="32px")
PAGE_STYLE = {
    "min_height": "100vh",
    "background_color": COLORS["background"],
    "background_image": (
        "radial-gradient(ellipse at top, rgba(191, 156, 114, 0.10), "
        "transparent 48%)"
    ),
    "font_family": FONT_FAMILY,
    "padding": rx.breakpoints(initial="32px 20px 64px", md="56px 32px 64px"),
    "overflow_x": "hidden",
}

CARD_STYLE = {
    "width": "100%",
    "max_width": MAX_WIDTHS["auth"],
    "padding": CARD_DEFAULT_PADDING,
    "border": f"1px solid {COLORS['border']}",
    "border_radius": "28px",
    "background_color": COLORS["surface"],
    "box_shadow": SHADOWS["card"],
}

HERO_CARD_STYLE = {
    **CARD_STYLE,
    "max_width": MAX_WIDTHS["home"],
}

PANEL_STYLE = {
    "width": "100%",
    "padding": CARD_DEFAULT_PADDING,
    "border": f"1px solid {COLORS['border']}",
    "border_radius": "28px",
    "background_color": COLORS["surface"],
    "box_shadow": SHADOWS["soft"],
}

MENU_STYLE = {
    "padding": rx.breakpoints(initial="16px", sm="16px 20px"),
    "border": f"1px solid {COLORS['border']}",
    "border_radius": "28px",
    "background_color": "rgba(255, 254, 252, 0.8)",
    "box_shadow": SHADOWS["soft"],
}

TILE_STYLE = {
    "width": "100%",
    "padding": rx.breakpoints(initial="20px", sm="24px"),
    "border": f"1px solid {COLORS['border']}",
    "border_radius": "20px",
    "background_color": COLORS["linen"],
    "box_shadow": SHADOWS["soft"],
}

INTERACTIVE_CARD_STYLE = {
    **TILE_STYLE,
    "transition": "transform 200ms ease, box-shadow 200ms ease, border-color 200ms ease",
    "_hover": {
        "transform": "translateY(-2px)",
        "box_shadow": SHADOWS["lift"],
        "border_color": COLORS["detail"],
    },
    "_focus_visible": {
        "outline": f"3px solid {COLORS['detail']}",
        "outline_offset": "2px",
    },
}

METRIC_CARD_STYLE = {
    "width": "100%",
    "min_height": "132px",
    "padding": CARD_DEFAULT_PADDING,
    "border": f"1px solid {COLORS['border']}",
    "border_radius": "20px",
    "background_color": COLORS["surface"],
    "box_shadow": SHADOWS["soft"],
}

EMPTY_STATE_STYLE = {
    "width": "100%",
    "padding": "40px 24px",
    "border": f"1px dashed {COLORS['sand']}",
    "border_radius": "20px",
    "background_color": "rgba(252, 250, 246, 0.6)",
    "text_align": "center",
}

CALLOUT_STYLES = {
    "info": {
        "padding": "16px",
        "border_radius": "14px",
        "background_color": COLORS["secondary"],
        "color": COLORS["accent"],
    },
    "success": {
        "padding": "16px",
        "border_radius": "14px",
        "background_color": COLORS["success_soft"],
        "color": COLORS["success"],
    },
    "warning": {
        "padding": "16px",
        "border_radius": "14px",
        "background_color": COLORS["warning_soft"],
        "color": COLORS["warning"],
    },
    "error": {
        "padding": "16px",
        "border_radius": "14px",
        "background_color": COLORS["error_soft"],
        "color": COLORS["error"],
    },
}


def empty_state(
    message: str | rx.Var[str],
    next_step: str | None = None,
    action: rx.Component | None = None,
) -> rx.Component:
    children = [
        rx.box(
            rx.icon("calendar-days", color=COLORS["accent"], size=20),
            display="flex",
            align_items="center",
            justify_content="center",
            width="48px",
            height="48px",
            border_radius="999px",
            background_color=COLORS["secondary"],
        ),
        rx.text(
            message,
            color=COLORS["text"],
            font_size="15px",
            font_weight="600",
            line_height="1.5",
        ),
    ]
    if next_step:
        children.append(
            rx.text(
                next_step,
                color=COLORS["muted"],
                font_size="14px",
                line_height="1.5",
            )
        )
    if action:
        children.append(action)
    return rx.box(
        rx.vstack(*children, align="center", spacing="3"),
        role="status",
        aria_live="polite",
        style=EMPTY_STATE_STYLE,
    )


def loading_state(message: str | rx.Var[str]) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.box(
                width="8px",
                height="8px",
                border_radius="999px",
                background_color=COLORS["detail"],
                animation="btPulse 1.4s ease-in-out infinite",
            ),
            rx.text(message, color=COLORS["muted"], font_size="14px"),
            align="center",
            spacing="2",
        ),
        rx.box(
            width="80px",
            height="8px",
            border_radius="20px",
            background_image=(
                "linear-gradient(90deg, #EBE1D5 25%, #FCFAF6 50%, #EBE1D5 75%)"
            ),
            background_size="200% 100%",
            animation="btShimmer 1.5s ease-in-out infinite",
        ),
        align="start",
        spacing="3",
        role="status",
        aria_live="polite",
        aria_busy="true",
    )


def error_callout(message: str | rx.Var[str]) -> rx.Component:
    callout = rx.callout(
        message,
        icon="info",
        role="alert",
        style=CALLOUT_STYLES["error"],
    )
    if isinstance(message, str):
        return callout
    return rx.cond(message != "", callout, rx.fragment())


FORM_FIELD_STYLE = {
    "width": "100%",
    "min_width": "0",
    "min_height": "48px",
    "padding_x": "16px",
    "border": f"1px solid {COLORS['input']}",
    "border_radius": "14px",
    "background_color": COLORS["linen"],
    "box_sizing": "border-box",
    "color": COLORS["text"],
    "font_family": FONT_FAMILY,
    "font_size": "16px",
    "box_shadow": "none",
    "_placeholder": {"color": "rgba(117, 103, 92, 0.7)"},
    "_focus": {
        "border_color": COLORS["accent"],
        "background_color": COLORS["linen"],
        "box_shadow": SHADOWS["focus_input"],
    },
}

FORM_LABEL_STYLE = {
    "font_size": "14px",
    "font_weight": "600",
    "color": COLORS["text"],
    "line_height": "1.4",
}


def field_label(label: str) -> rx.Component:
    return rx.text(label, style=FORM_LABEL_STYLE)


def status_badge(
    label: str | rx.Var[str],
    active: bool | rx.Var[bool],
    *,
    neutral_when_inactive: bool = False,
) -> rx.Component:
    inactive_background = (
        COLORS["secondary"] if neutral_when_inactive else COLORS["error_soft"]
    )
    inactive_color = COLORS["muted"] if neutral_when_inactive else COLORS["error"]
    background = rx.cond(active, COLORS["success_soft"], inactive_background)
    color = rx.cond(active, COLORS["success"], inactive_color)
    return rx.badge(
        rx.hstack(
            rx.box(
                width="6px",
                height="6px",
                border_radius="999px",
                background_color=color,
            ),
            rx.text(label),
            align="center",
            spacing="2",
        ),
        height="28px",
        padding_x="12px",
        background_color=background,
        color=color,
        border_radius="999px",
        font_size="12px",
        font_weight="700",
    )


BUTTON_STYLE = {
    "min_height": "48px",
    "padding_x": "24px",
    "border_radius": "999px",
    "font_family": FONT_FAMILY,
    "font_size": "15px",
    "font_weight": "600",
    "gap": "8px",
    "box_shadow": SHADOWS["button"],
    "transition": "all 200ms ease",
    "_active": {"transform": "scale(0.98)"},
    "_focus_visible": {
        "outline": f"3px solid {COLORS['detail']}",
        "outline_offset": "2px",
    },
    "_disabled": {"opacity": "0.45", "cursor": "not-allowed"},
}

BUTTON_STYLES = {
    "primary": {
        **BUTTON_STYLE,
        "background_color": COLORS["accent"],
        "color": COLORS["primary_foreground"],
        "box_shadow": SHADOWS["button"],
        "width": rx.breakpoints(initial="100%", sm="auto"),
        "_hover": {"background_color": COLORS["accent_hover"]},
    },
    "secondary": {
        **BUTTON_STYLE,
        "background_color": COLORS["surface"],
        "color": COLORS["accent"],
        "border": f"1px solid {COLORS['input']}",
        "box_shadow": "none",
        "_hover": {
            "background_color": COLORS["linen"],
            "border_color": COLORS["detail"],
        },
    },
    "soft": {
        **BUTTON_STYLE,
        "background_color": COLORS["secondary"],
        "color": COLORS["accent"],
        "box_shadow": "none",
        "_hover": {"background_color": COLORS["sand"]},
    },
    "ghost": {
        **BUTTON_STYLE,
        "background_color": "transparent",
        "color": COLORS["accent"],
        "box_shadow": "none",
        "_hover": {"background_color": COLORS["secondary"]},
    },
    "danger": {
        **BUTTON_STYLE,
        "background_color": COLORS["error"],
        "color": COLORS["primary_foreground"],
    },
    "danger_outline": {
        **BUTTON_STYLE,
        "background_color": COLORS["surface"],
        "color": COLORS["error"],
        "border": "1px solid rgba(154, 59, 66, 0.3)",
        "box_shadow": "none",
        "_hover": {"background_color": COLORS["error_soft"]},
    },
    "link": {
        **BUTTON_STYLE,
        "background_color": "transparent",
        "color": COLORS["accent"],
        "text_decoration": "underline",
        "text_decoration_color": "rgba(191, 156, 114, 0.6)",
        "text_underline_offset": "4px",
        "box_shadow": "none",
    },
}

BADGE_STYLES = {
    "confirmed": {
        "height": "28px",
        "padding_x": "12px",
        "background_color": COLORS["success_soft"],
        "color": COLORS["success"],
        "border_radius": "999px",
        "font_size": "12px",
        "font_weight": "700",
    },
    "cancelled": {
        "height": "28px",
        "padding_x": "12px",
        "background_color": COLORS["error_soft"],
        "color": COLORS["error"],
        "border_radius": "999px",
        "font_size": "12px",
        "font_weight": "700",
    },
    "inactive": {
        "height": "28px",
        "padding_x": "12px",
        "background_color": COLORS["secondary"],
        "color": COLORS["muted"],
        "border_radius": "999px",
        "font_size": "12px",
        "font_weight": "700",
    },
    "outline": {
        "height": "28px",
        "padding_x": "12px",
        "background_color": COLORS["surface"],
        "color": COLORS["muted"],
        "border": f"1px solid {COLORS['border']}",
        "border_radius": "999px",
        "font_size": "12px",
        "font_weight": "700",
    },
}


def brand() -> rx.Component:
    return rx.hstack(
        rx.text("Beauty", color=COLORS["accent"]),
        rx.text("Time", color=COLORS["detail"], font_style="italic"),
        align="baseline",
        spacing="0",
        font_family=HEADING_FONT_FAMILY,
        font_size="30px",
        font_weight="600",
        letter_spacing="-0.02em",
        line_height="1",
    )


GLOBAL_STYLES = {
    "font_family": FONT_FAMILY,
    "font_size": "15px",
    "line_height": "1.6",
    "color": COLORS["text"],
    "background_color": COLORS["background"],
    rx.heading: {
        "font_family": HEADING_FONT_FAMILY,
        "font_weight": "600",
        "color": COLORS["text"],
        "line_height": "1.15",
    },
    rx.text: {"font_family": FONT_FAMILY},
    rx.input: FORM_FIELD_STYLE,
    rx.text_area: {
        **FORM_FIELD_STYLE,
        "min_height": "112px",
        "padding_y": "12px",
        "resize": "vertical",
    },
    rx.select: {
        "font_family": FONT_FAMILY,
        "font_size": "16px",
    },
    rx.checkbox: {
        "min_height": "48px",
        "padding_x": "16px",
        "border_radius": "14px",
        "background_color": COLORS["linen"],
        "color": COLORS["text"],
        "font_family": FONT_FAMILY,
        "_checked": {
            "background_color": COLORS["secondary"],
            "border_color": COLORS["accent"],
        },
    },
    rx.badge: {
        "height": "28px",
        "padding_x": "12px",
        "border_radius": "999px",
        "font_family": FONT_FAMILY,
        "font_size": "12px",
        "font_weight": "700",
    },
    rx.button: BUTTON_STYLE,
    rx.link: {
        "color": COLORS["accent"],
        "_focus_visible": {
            "outline": f"3px solid {COLORS['detail']}",
            "outline_offset": "2px",
        },
        "[aria-invalid='true']": {
            "border_color": COLORS["error"],
        },
        "[aria-invalid='true']:focus": {
            "border_color": COLORS["error"],
            "box_shadow": "0 0 0 4px rgba(154, 59, 66, 0.16)",
        },
    },
    rx.callout: {
        "padding": "16px",
        "border_radius": "14px",
        "font_family": FONT_FAMILY,
    },
    "[role='alert']:not(:empty)": {
        "display": "flex",
        "align_items": "flex-start",
        "gap": "8px",
        "padding": "8px 12px",
        "border": "1px solid rgba(154, 59, 66, 0.18)",
        "border_left": f"3px solid {COLORS['error']}",
        "border_radius": "14px",
        "background_color": COLORS["error_soft"],
        "color": COLORS["error"],
    },
    "[role='alert']:not(:empty)::before": {
        "content": "'!'",
        "display": "inline-flex",
        "align_items": "center",
        "justify_content": "center",
        "flex": "0 0 18px",
        "width": "18px",
        "height": "18px",
        "border_radius": "999px",
        "background_color": COLORS["error"],
        "color": COLORS["primary_foreground"],
        "font_size": "12px",
        "font_weight": "700",
    },
    "@keyframes btPulse": {
        "0%": {"opacity": "1"},
        "50%": {"opacity": "0.35"},
        "100%": {"opacity": "1"},
    },
    "@keyframes btShimmer": {
        "0%": {"background_position": "100% 0"},
        "100%": {"background_position": "-100% 0"},
    },
}
