# main.py
import os, json

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock

from jnius import autoclass, PythonJavaClass, java_method

PythonActivity = autoclass("org.kivy.android.PythonActivity")
WebView = autoclass("android.webkit.WebView")
Color = autoclass("android.graphics.Color")
LayoutParams = autoclass("android.view.ViewGroup$LayoutParams")


def read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class Runnable(PythonJavaClass):
    __javainterfaces__ = ["java/lang/Runnable"]

    def __init__(self, fn):
        super().__init__()
        self.fn = fn

    @java_method("()V")
    def run(self):
        self.fn()


class WebViewApp(App):
    def build(self):
        self.root = Widget()
        self.activity = PythonActivity.mActivity

        base = os.path.join(self.activity.getFilesDir().getAbsolutePath(), "app", "www")
        print("[PATH] www base =", base)

        csv_files = {
            "ke_fragepool.csv": os.path.join(base, "ke_fragepool.csv"),
            "ke_fragepool_schule_freizeit.csv": os.path.join(base, "ke_fragepool_schule_freizeit.csv"),
        }

        csv_map = {}
        for key, p in csv_files.items():
            try:
                csv_map[key] = read_text(p)
                print(f"[CSV] OK {key} ({len(csv_map[key])} chars) -> {p}")
            except Exception as e:
                csv_map[key] = ""
                print(f"[CSV] FEHLER {key} -> {p}: {e}")

        self.payload = json.dumps(csv_map, ensure_ascii=False)
        self.debug = f"py-inject keys={sum(1 for v in csv_map.values() if v.strip())}"

        def create_webview_on_ui_thread():
            wv = WebView(self.activity)
            wv.setBackgroundColor(Color.WHITE)

            s = wv.getSettings()
            s.setJavaScriptEnabled(True)
            s.setDomStorageEnabled(True)
            s.setAllowFileAccess(True)
            s.setAllowContentAccess(True)
            try:
                s.setAllowFileAccessFromFileURLs(True)
                s.setAllowUniversalAccessFromFileURLs(True)
            except Exception:
                pass

            index_path = os.path.join(base, "index.html")
            url = "file://" + index_path
            print("[WEB] load", url)
            wv.loadUrl(url)

            self.activity.addContentView(
                wv,
                LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT),
            )

            self._webview = wv  # Referenz halten
            print("[WEB] added")

        # WebView sicher im UI-Thread erzeugen
        self._runnable = Runnable(create_webview_on_ui_thread)
        self.activity.runOnUiThread(self._runnable)

        # Injection: ein paar Versuche nach dem Start (läuft im Kivy-Thread)
        self._inject_tries = 0
        Clock.schedule_once(self.try_inject, 0.6)
        Clock.schedule_once(self.try_inject, 1.2)
        Clock.schedule_once(self.try_inject, 2.0)

        return self.root

    def try_inject(self, *args):
        if not hasattr(self, "_webview"):
            print("[INJECT] webview noch nicht da")
            return

        self._inject_tries += 1
        js = (
            "window.ANDROID_CSVS=" + self.payload + ";"
            "window.ANDROID_DEBUG=" + json.dumps(self.debug) + ";"
            "console.log('ANDROID inject ok');"
        )

        def inject_on_ui_thread():
            try:
                self._webview.evaluateJavascript(js, None)
                print(f"[INJECT] try {self._inject_tries} OK:", self.debug)
            except Exception as e:
                print(f"[INJECT] try {self._inject_tries} FEHLER:", e)

        self.activity.runOnUiThread(Runnable(inject_on_ui_thread))


if __name__ == "__main__":
    WebViewApp().run()

