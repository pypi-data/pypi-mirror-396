from nicegui import ui


@ui.page("/", title="TGZR - Manager Panel", dark=True)
async def main():
    ui.label("Hello world! 😛 (TGZR Shell App Template)")
