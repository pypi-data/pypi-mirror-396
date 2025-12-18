if __name__ in {"__main__", "__mp_main__"}:
    from .app import app

    app.run_app(native=False, reload=True)
