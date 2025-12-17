"""
Pintes JavaScript Module.

Made to give the user Python functions that replicate JS functions.
"""


class PJS:
    """
    PintesJS.

    Allows Pintes pages to use JavaScript functions in a more Python-like way.
    """

    def __init__(self, RootPint):
        self.rootclass = RootPint

    def alert(self, message: str = ''):
        """
        PJS.Alert().

        Displays a dialog with an optional message, and waits until the user dismisses the dialog.
        """
        self.rootclass.top_js.append(f'alert("{message}")')

    def log(self, message: str = 'Made in Pintes!'):
        self.rootclass.top_js.append(f'console.log("{message}")')
