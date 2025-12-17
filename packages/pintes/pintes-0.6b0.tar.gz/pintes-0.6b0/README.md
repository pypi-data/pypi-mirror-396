# Pintes
*HTML is too hard, let's write the website in Python!*

Pintes is a tool made in Python that allows users to develop static HTML pages with ease.

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/FormunaGit/Pintes/python-publish.yml?style=flat&logo=githubactions&logoColor=white) ![GitHub License](https://img.shields.io/github/license/FormunaGit/Pintes?logo=gnu) ![GitHub last commit](https://img.shields.io/github/last-commit/formunagit/pintes)

## Why?
- The tool itself can be pretty useful in some cases, such as for a prototype or a simple GUI for something like [pywebview](https://github.com/r0x0r/pywebview).
- At first, the name "Pintes" was a joke but now doubles as a play on the word "pint", a unit of liquid.
  - In Pintes, a pint is what holds your elements.

## How?
Pintes internally uses a list that the tag create functions append to. This list is then joined and written to a file after the necessary tags are added.

## Usage
~~As of 0.1:PRERELEASE, Pintes is not on PyPI. And since I don't understand how to use setup.py, you'll have to clone the repository and use the `pintes.py` file as a module.~~

As of 0.2.alpha.1 (0.2a1), Pintes is now on PyPI. You can install it using `pip install pintes` and use it as a module.

Check out the demo folder for a demo on how to use Pintes.

## What's available?
- [x] Most HTML tags
- [x] Divs support
- [x] Classes support
- [x] CSS support
- [x] Image support
- [x] Anchor/`a` tag support
- [ ] JS support
  - [x] `<script>` tag
  - [ ] Basic JS functionality from within Python
- [x] Custom divs support (e.g. `ul` and `ol`)
- [x] Self-closing tags support (e.g. `br`)

Am I missing something? [Help Pintes and make an issue!](https://github.com/FormunaGit/Pintes/issues)

## License
The license for Pintes is the GNU General Public License v3.0. You can view the license here in the LICENSE file or [here](https://www.gnu.org/licenses/gpl-3.0.html).

Because of the license, Pintes is free to use, modify, and distribute. However, you must provide the source code and the license with the distribution if you modify it.

## Contributing
If you want to contribute to Pintes, you can fork the repository and make a pull request. Don't know where to start? I recommend just reading through the code and adding [features that haven't been added yet](https://github.com/FormunaGit/Pintes/?tab=readme-ov-file#whats-available).

Nix users (and by extent, NixOS users) can take advantage of the `shell.nix` file. Just `cd` into the project and run `nix-shell`. It'll take care of everything; installing the required packages, setting up the venv if needed and activating it, all in a temporary environment that won't affect your system.
