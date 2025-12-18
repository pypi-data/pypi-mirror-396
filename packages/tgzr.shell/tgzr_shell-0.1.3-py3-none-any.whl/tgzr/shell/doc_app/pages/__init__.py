from nicegui import ui


@ui.page("/", title="TGZR - Manager Panel", dark=True)
async def main():
    ui.label("Yeah YOLO! 😛").classes("text-h5")

    def do_it(e):
        import os

        l = os.listdir("/")
        label.text = ", ".join(l)

    label = ui.label().classes("tracking-widest")
    with ui.column():
        ui.label("go").classes("bg-blue-800 m-5 p-5 rounded-xl")
        ui.label("go")
        ui.label("go")
        ui.label("go")
        ui.label("go adsf a asdfs")
        ui.label("go")
        ui.label("go")
        ui.button("Go", on_click=do_it)
