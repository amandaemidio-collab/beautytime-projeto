import reflex as rx

from frontend.theme import RADIX_ACCENT

config = rx.Config(
    app_name="frontend",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(
                appearance="light",
                has_background=True,
                radius="large",
                accent_color=RADIX_ACCENT,
            )
        ),
    ]
)