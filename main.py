from app import App
from process_manager import ProcessManager
from profile_manager import ProfileManager
from tray_icon import TrayIcon


def main():
    pm = ProfileManager()
    proc = ProcessManager()
    app = App(pm, proc)
    tray = TrayIcon(on_show=app.show, on_quit=app.quit_app)
    tray.start()
    app.mainloop()


if __name__ == "__main__":
    main()
