"""
Pintes
~~~~~~~~~~~~~~~~
*An amalgamation of horror.*
Pintes is a Python module designed to generate static HTML pages.
"""


class CreatePint:
    """
    Creates a new pint for you to use.
    """

    def __init__(self):
        self.body = []
        self.head = []
        # JS
        self.top_js = []
        self.bottom_js = []

        # Create functions
        self.create = self._CreateMethods(self.head, self.body)

    # Le code
    class _CreateMethods:
        def __init__(self, head: list, body: list):
            self.head = head
            self.body = body

        def title(self, title: str = "A Pintes Page"):
            """
            Creates a title.
            It's recommended to have only 1 per page.
            `title` is the title itself and is a string.
            """
            self.head.append(f"<title>{title}</title>")

        def header(self, text: str = "Powered by Pintes!", level: int = 1):
            """
            Creates a header.
            By default the text gets set to "Powered by Pintes!" and is a `h1` element by default.
            `text` is the actual contents of the element and is a string.
            `level` is the level/importance of the header and is an integer. Setting it to 1 (the default) makes a `h1` element.
            """
            self.body.append(f"<h{level}>{text}</h{level}>")

        def p(self, text: str = ''):
            """
            Creates a paragraph element.
            The text by default is empty.
            `text` is the actual contents of the element is a string.
            """
            self.body.append(f"<p>{text}</p>")

        def a(self, label: str = 'Link', url: str = 'https://formuna.qzz.io/'):
            """
            Creates an anchor element.
            By default the label is "Link" and the URL links to my website.
            `label` is the text the user sees, with a blue color and underline, and is a string. Defaults to "Link".
            `url` is the URL the user goes to upon clicking the anchor and is a string. Defaults to "https://formuna.qzz.io/".
            """
            self.body.append(f'<a href="{url}">{label}</a>')

    def create_custom(
        self,
        text: str = "UNNAMED",
        className: str = "",
        tag: str = "p",
        selfClosing: bool = False,
    ):
        """
        Creates a new customizable tag.
        `text` is the text inside the tag. Defaults to 'UNNAMED' if none specified.
        `className` is the class of the tag. Optional.
        `tag` is the tag type. Defaults to 'p' (paragraph) if none specified.
        `selfClosing` is a boolean that determines if the tag is self-closing. Defaults to False. (e.g. <br/> is self-closing.) Will raise a ValueError if text is specified while this is true.
        """
        if selfClosing:
            if text == "UNNAMED":
                self.body.append(f'<{tag} class="{className}"/>')
            else:
                raise ValueError("selfClosing tags cannot have text.")
        else:
            self.body.append(f'<{tag} class="{className}">{text}</{tag}>')

    def create_anchor(
        self, text: str = "UNNAMED", href: str = "#", className: str = ""
    ):
        """
        Creates an anchor tag.
        `text` is the text inside the anchor tag. Defaults to 'UNNAMED' if none specified.
        `href` is the href of the anchor tag. Defaults to '#' if none specified. (does nothing)
        `className` is the class of the anchor tag. Optional.
        """
        self.body.append(f'<a href="{href}" class="{className}">{text}</a>')

    def create_image(
        self,
        src: str,
        alt: str = "Image",
        className: str = "",
        height: str = "100%",
        width: str = "100%",
    ):
        """
        Creates an image tag.
        `src` is the source of the image. Required.
        `alt` is the alt text of the image. Defaults to 'Image' but recommended to change.
        `className` is the class of the image tag. Optional.
        """
        self.body.append(
            f'<img src="{src}" alt="{alt}" class="{className}" style="width:{width}; height:{height};"/>'
        )

    # Export functions
    def export_to_html(self):
        """
        Exports the body to an HTML string. Useful for debugging or PyWebview.
        """
        # return "".join(self.body)
        body = "".join(self.body)
        head = "".join(self.head)
        top_js = "".join(self.top_js)
        bottom_js = "".join(self.bottom_js)
        html = f"<!DOCTYPE html><html><head>{head}</head><body>{top_js} {body} {bottom_js}</body></html>"
        return html

    def export_to_html_file(
        self, filename: str = "index.html", printResult: bool = True
    ):
        """
        Exports the body to an HTML file.
        `filename` is the filename of the exported HTML file. Defaults to 'index.html' if none specified.
        `printResult` controls whether the function will print the result of the export. Defaults to True.
        """
        html = self.export_to_html()
        with open(filename, "w", encoding="utf-8") as file:
            file.write(html)
        if printResult:
            print(f"Exported to {filename} successfully.")

    # Pint merger
    def pint_merge(self, pint, tag: str = "div"):
        """
        Merges two Pints together.
        `pint` is the Pint object to merge with.
        `tag` is the tag to wrap the merged Pint in. Defaults to 'div'. Can be set to any tag that supports children elements.
        """
        if not isinstance(pint, CreatePint):
            raise TypeError("pint must be an instance of CreatePint")
        divhtml = f'<{tag}>{"".join(pint.body)}</{tag}>'
        self.body.append(divhtml)

    # Head functions
    def retitle_page(self, title: str = ""):
        """
        Retitles the page.
        `title` is the new title of the page. Defaults to ''.
        """
        self.head.append(f"<title>{title}</title>")

    def add_favicon(self, href: str = "favicon.ico"):
        """
        Adds a favicon to the page.
        `href` is the href of the favicon. Defaults to 'favicon.ico'.
        """
        self.head.append(f'<link rel="icon" href="{href}">')

    def add_metadata(self, name: str = "", content: str = ""):
        """
        Adds metadata to the page. Useful for search engines such as Google.
        `name` is the name of the metadata. (e.g. 'author' or 'description')
        `content` is the content of the metadata. (e.g. 'Formuna' or 'A Pintes demo')
        """
        self.head.append(f'<meta name="{name}" content="{content}">')

    def add_css(self, css: str = ""):
        """
        Adds raw CSS data to the page.
        `css` is the string of CSS. Defaults to Nothing.
        """
        self.head.append(f"<style>{css}</style>")

    # JavaScript-related functions
    def add_js(
        self, js: str = 'console.log("Powered by Pintes!")', position: str = "bottom"
    ):
        """
        Adds raw JavaScript code to the page.
        `js` is the string of JavaScript. Defaults to a one-liner that prints "Powered by Pintes!" in the console.
        `position` is the position of where the JavaScript tag is placed. Defaults to 'bottom' (just on top `</body>`).
        """
        if position == "top":
            self.top_js.append(f"<script>{js}</script>")
        elif position == "bottom":
            self.bottom_js.append(f"<script>{js}</script>")
        else:
            raise ValueError("position must be either 'top' or 'bottom'")


# Global create instance for module-level access
# Create a global instance that can be used for module-level calls
_global_pint_instance = CreatePint()


# Need to create a custom module-level create interface that wraps the global instance
class ModuleCreateInterface:
    def header(self, text: str = "Powered by Pintes!", level: int = 1):
        """
        Creates a header.
        By default the text gets set to "Powered by Pintes!" and is a `h1` element by default.
        `text` is the actual contents of the element and is a string.
        `level` is the level/importance of the header and is an integer. Setting it to 1 (the default) makes a `h1` element.
        """
        _global_pint_instance.body.append(f"<h{level}>{text}</h{level}>")

    def title(self, title: str = "A Pintes Page"):
        """
        Creates a title.
        It's recommended to have only 1 per page.
        `title` is the title itself and is a string.
        """
        _global_pint_instance.head.append(f"<title>{title}</title>")


create = ModuleCreateInterface()


if __name__ == "__main__":
    print("What are you doing? Run demo.py instead.")
