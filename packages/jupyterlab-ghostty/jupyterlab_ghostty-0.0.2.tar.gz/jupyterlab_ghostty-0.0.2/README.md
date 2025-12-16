# jupyterlab-ghostty

A JupyterLab extension that provides a terminal emulator powered by [ghostty-web](https://github.com/coder/ghostty-web) (`libghostty` WASM).

## Requirements

- JupyterLab >= 4.0.0

## Installation

```bash
pip install jupyterlab-ghostty
```

## Uninstall

```bash
pip uninstall jupyterlab-ghostty
```

## Development Installation

For a development installation:

```bash
# Clone the repository
git clone https://github.com/eexwhyzee/jupyterlab-ghostty.git
cd jupyterlab-ghostty

# Install dependencies
jlpm install

# Build the extension
jlpm build

# Install the extension in development mode
pip install -e "."

# Link the extension for development
jupyter labextension develop . --overwrite
```

## Usage

Once installed, you'll see a "Ghostty Terminal" option in:

1. **Launcher**: Click the "Ghostty Terminal" icon in the "Other" section
2. **Command Palette**: Search for "New Ghostty Terminal"
3. **File Menu**: File > New > Ghostty Terminal

Both the standard existing xterm.js terminal and Ghostty terminal can be used side-by-side.

## Configuration

Configure the Ghostty terminal in JupyterLab Settings:

| Setting | Description | Default |
|---------|-------------|---------|
| `fontFamily` | Font family for terminal text | `Menlo, Consolas, "DejaVu Sans Mono", monospace` |
| `fontSize` | Font size (9-72) | `13` |
| `lineHeight` | Line height multiplier | `1.0` |
| `theme` | Terminal theme (`inherit`, `light`, `dark`) | `inherit` |
| `scrollback` | Scrollback buffer lines | `10000` |
| `cursorBlink` | Whether the cursor blinks | `false` |
| `shutdownOnClose` | Shut down session when closing | `false` |
| `closeOnExit` | Close widget when session ends | `true` |

