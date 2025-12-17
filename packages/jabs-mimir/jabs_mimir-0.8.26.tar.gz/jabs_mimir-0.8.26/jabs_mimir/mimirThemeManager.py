# mimirThemeManager.py

class MimirThemeManager:
    def __init__(self, style):
        self._style = style
        self._themeColors = style.colors
        self._allowThemeToggle = False
        self._themeChangeSubscribers = []

    def allowDarkMode(self, enabled=True):
        self._allowThemeToggle = enabled

    @property
    def themeColors(self):
        return self._themeColors

    def toggleTheme(self):
        current = self._style.theme.name
        self._style.theme_use("darkly" if current != "darkly" else "cosmo")
        self.updateThemeColors()

    def updateThemeColors(self):
        self._themeColors = self._style.colors
        for callback in self._themeChangeSubscribers:
            try:
                callback()
            except Exception as e:
                print(f"[MimirTheme] Failed to notify theme subscriber: {e}")

    def subscribeToThemeChange(self, callback):
        if callback not in self._themeChangeSubscribers:
            self._themeChangeSubscribers.append(callback)
