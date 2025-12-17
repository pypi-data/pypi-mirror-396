{
  pkgs ? import <nixpkgs> { },
}:

pkgs.mkShell {
  buildInputs = with pkgs; [
    # Python 3.13
    python313
    python313Packages.pip
    python313Packages.venvShellHook # For automatic virtual environment
    python313Packages.hatchling # Build system requirement

    # Development tools
    black # Code formatter
    python313Packages.flake8 # Linter
    python313Packages.mypy # Type checker
    python313Packages.pytest # Testing framework

    mkdocs
    gum
  ];

  # Set environment variables
  VIRTUAL_ENV = "./.venv";
  PYTHONPATH = "${placeholder "out"}/lib/python3.13/site-packages";

  # Create shell hook to initialize virtual environment if needed
  shellHook = ''
    gum style --foreground="#ebba34" "█████▄ ▄▄ ▄▄  ▄▄ ▄▄▄▄▄▄ ▄▄▄▄▄  ▄▄▄▄ ";
    gum style --foreground="#ebba34" "██▄▄█▀ ██ ███▄██   ██   ██▄▄  ███▄▄ ";
    gum style --foreground="#ebba34" "██     ██ ██ ▀██   ██   ██▄▄▄ ▄▄██▀ ";
    gum style --foreground="#f0c348" "▄▄▄▄▄▄                     ▄▄                            ▄▄▄▄▄▄▄ ▄▄          ▄▄ ▄▄ ";
    gum style --foreground="#f0c348" "███▀▀██▄                   ██                           █████▀▀▀ ██          ██ ██ ";
    gum style --foreground="#f0c348" "███  ███ ▄█▀█▄ ██ ██ ▄█▀█▄ ██ ▄███▄ ████▄ ▄█▀█▄ ████▄    ▀████▄  ████▄ ▄█▀█▄ ██ ██ ";
    gum style --foreground="#f0c348" "███  ███ ██▄█▀ ██▄██ ██▄█▀ ██ ██ ██ ██ ██ ██▄█▀ ██ ▀▀      ▀████ ██ ██ ██▄█▀ ██ ██ ";
    gum style --foreground="#f0c348" "██████▀  ▀█▄▄▄  ▀█▀  ▀█▄▄▄ ██ ▀███▀ ████▀ ▀█▄▄▄ ██      ███████▀ ██ ██ ▀█▄▄▄ ██ ██ ";
    echo ""
    gum style --foreground="#00ffcc" "All packages have been downloaded."
    gum style --foreground="#00ffcc" "Python version: $(gum style --foreground="#ccff00" $(python --version))"
    gum style --foreground="#00deb1" "(if it isn't 3.13 something went wrong, but as long as it's above 3.11 it should be fine.)"
    echo ""

    # Detect shell type and activate the right venv script
    if [ -n "$FISH_VERSION" ]; then
        # Fish shell
        VENV_ACTIVATE=".venv/bin/activate.fish"
    else
        # Default to POSIX shell
        VENV_ACTIVATE=".venv/bin/activate"
    fi

    # Check if virtual environment exists, create it if it doesn't
    if [ ! -d ".venv" ]; then
        echo "Creating a venv since one doesn't exist"
        python -m venv .venv
        source $VENV_ACTIVATE
        pip install --upgrade pip
        echo "Everything looks alright"
    else
        echo "venv already exists, activating that"
        source $VENV_ACTIVATE
    fi

    # Install the package in development mode if not already installed
    if ! python -c "import pintes" &> /dev/null; then
        echo "Installing Pintes in development mode (changes are applied instantly)"
        pip install -e .
    fi

    echo "venv activated: $VIRTUAL_ENV"
    echo ""
    echo "to run the demo, use:"
    echo "cd demo && python demo.py"
    echo ""
    echo "current packages installed:"
    pip list
  '';
}
