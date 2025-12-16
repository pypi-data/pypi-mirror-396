# JupyterLab Terminal: ghostty-web Integration Plan

## Overview

This document outlines the code changes required to replace xterm.js with [ghostty-web](https://github.com/coder/ghostty-web) in JupyterLab's terminal implementation, as requested in [GitHub Issue #17702](https://github.com/jupyterlab/jupyterlab/issues/17702).

### What is ghostty-web?

ghostty-web is a WebAssembly-based terminal emulator that uses [Ghostty's](https://github.com/ghostty-org/ghostty) VT100 parser. Key benefits include:

- **Proper VT100 implementation**: Uses the same battle-tested code from the native Ghostty application
- **Better Unicode support**: Full grapheme handling for complex scripts (Devanagari, Arabic)
- **XTPUSHSGR/XTPOPSGR support**: Full support for terminal escape sequences
- **xterm.js API compatibility**: Designed as a drop-in replacement
- **~400KB bundle size**: Zero runtime dependencies

---

## Current Architecture

### Package Structure

```
packages/
├── terminal/                    # Core terminal widget
│   ├── src/
│   │   ├── index.ts            # Exports
│   │   ├── tokens.ts           # Interfaces (ITerminal, ITerminalTracker)
│   │   └── widget.ts           # Terminal widget implementation (xterm.js integration)
│   ├── style/
│   │   └── base.css            # Terminal CSS (references .xterm classes)
│   └── package.json            # xterm dependencies
│
├── terminal-extension/          # JupyterLab extension
│   ├── src/
│   │   ├── index.ts            # Plugin, commands, menus
│   │   └── searchprovider.ts   # Search using xterm SearchAddon
│   ├── schema/
│   │   └── plugin.json         # Settings schema
│   └── package.json            # Extension dependencies
│
└── services/src/terminal/       # Backend terminal services (no changes needed)
```

### Current xterm.js Dependencies

**packages/terminal/package.json:**
```json
{
  "dependencies": {
    "@xterm/xterm": "~5.5.0",
    "@xterm/addon-canvas": "~0.7.0",
    "@xterm/addon-fit": "~0.10.0",
    "@xterm/addon-search": "~0.15.0",
    "@xterm/addon-web-links": "~0.11.0",
    "@xterm/addon-webgl": "~0.18.0"
  }
}
```

**packages/terminal-extension/package.json:**
```json
{
  "dependencies": {
    "@xterm/addon-search": "~0.15.0"
  }
}
```

---

## Required Code Changes

### 1. Package Dependencies

#### packages/terminal/package.json

**Remove:**
```json
"@xterm/addon-canvas": "~0.7.0",
"@xterm/addon-fit": "~0.10.0",
"@xterm/addon-search": "~0.15.0",
"@xterm/addon-web-links": "~0.11.0",
"@xterm/addon-webgl": "~0.18.0",
"@xterm/xterm": "~5.5.0"
```

**Add:**
```json
"ghostty-web": "^0.3.0"
```

**Remove from `jupyterlab.extraStyles`:**
```json
"jupyterlab": {
  "extraStyles": {
    "@xterm/xterm": [
      "css/xterm.css"
    ]
  }
}
```

#### packages/terminal-extension/package.json

**Remove:**
```json
"@xterm/addon-search": "~0.15.0"
```

---

### 2. Terminal Widget (packages/terminal/src/widget.ts)

This is the main file requiring changes. The widget wraps the terminal emulator library.

#### 2.1 Import Changes

**Current imports (lines 15-24):**
```typescript
import type {
  ITerminalInitOnlyOptions,
  ITerminalOptions,
  Terminal as Xterm
} from '@xterm/xterm';
import type { CanvasAddon } from '@xterm/addon-canvas';
import type { FitAddon } from '@xterm/addon-fit';
import type { SearchAddon } from '@xterm/addon-search';
import type { WebLinksAddon } from '@xterm/addon-web-links';
import type { WebglAddon } from '@xterm/addon-webgl';
```

**New imports:**
```typescript
import { init as initGhostty, Terminal as GhosttyTerminal } from 'ghostty-web';
```

#### 2.2 Terminal Creation (Private.createTerminal function, lines 644-675)

**Current implementation:**
- Dynamically imports xterm.js and addons
- Detects WebGL support and falls back to Canvas
- Loads FitAddon, SearchAddon, WebLinksAddon

**New implementation:**
```typescript
namespace Private {
  let GhosttyTerminal_: typeof GhosttyTerminal;
  let initialized = false;

  export async function createTerminal(
    options: IGhosttyOptions
  ): Promise<GhosttyTerminal> {
    if (!initialized) {
      await initGhostty();
      const ghostty = await import('ghostty-web');
      GhosttyTerminal_ = ghostty.Terminal;
      initialized = true;
    }

    const term = new GhosttyTerminal_(options);
    return term;
  }
}
```

#### 2.3 Constructor Changes (lines 51-131)

**Key changes needed:**

1. **Options mapping**: Map JupyterLab's `ITerminal.IOptions` to ghostty-web options
2. **Remove SearchAddon handling**: ghostty-web doesn't use the same addon system
3. **Remove FitAddon**: ghostty-web handles fitting differently
4. **Update ready promise**: Simplified initialization

```typescript
constructor(
  session: TerminalNS.ITerminalConnection,
  options: Partial<ITerminal.IOptions> = {},
  translator?: ITranslator
) {
  super();
  // ... existing setup code ...

  const ghosttyOptions = {
    theme: Private.getGhosttyTheme(this._options.theme),
    fontSize: this._options.fontSize,
    fontFamily: this._options.fontFamily,
    scrollback: this._options.scrollback,
    cursorBlink: this._options.cursorBlink,
    // Note: lineHeight, screenReaderMode need mapping or alternatives
  };

  Private.createTerminal(ghosttyOptions)
    .then(term => {
      this._term = term;
      this._initializeTerm();
      // ... rest of initialization ...
    })
    .catch(reason => {
      console.error('Failed to create a terminal.\n', reason);
      this._ready.reject(reason);
    });
}
```

#### 2.4 Option Setters (setOption method, lines 157-203)

**Update option mappings for ghostty-web:**

```typescript
setOption<K extends keyof ITerminal.IOptions>(
  option: K,
  value: ITerminal.IOptions[K]
): void {
  // ... existing checks ...

  switch (option) {
    case 'fontFamily':
      this._term.options.fontFamily = value as string | undefined;
      break;
    case 'fontSize':
      this._term.options.fontSize = value as number | undefined;
      break;
    case 'scrollback':
      this._term.options.scrollback = value as number | undefined;
      break;
    case 'theme':
      this._term.options.theme = Private.getGhosttyTheme(value as ITerminal.Theme);
      this._setThemeAttribute(value as ITerminal.Theme);
      this._themeChanged.emit();
      break;
    // Note: Some options like lineHeight, screenReaderMode, macOptionIsMeta
    // may not have direct equivalents in ghostty-web
    default:
      break;
  }

  this._needsResize = true;
  this.update();
}
```

#### 2.5 Resize Handling (lines 457-469)

**Current (using FitAddon):**
```typescript
private _resizeTerminal() {
  if (this._options.autoFit) {
    this._fitAddon.fit();
  }
  // ...
}
```

**New (ghostty-web native resize):**
```typescript
private _resizeTerminal() {
  if (this._options.autoFit) {
    // ghostty-web handles fitting internally or use resize()
    const { cols, rows } = this._calculateDimensions();
    this._term.resize(cols, rows);
  }
  // ...
}

private _calculateDimensions(): { cols: number; rows: number } {
  // Calculate cols/rows based on container size and font metrics
  // ghostty-web may provide helpers for this
}
```

#### 2.6 Search Addon Removal

**Remove from class:**
```typescript
// Remove these private members
private _searchAddon: SearchAddon;

// Remove this getter
get searchAddon(): SearchAddon {
  return this._searchAddon;
}
```

#### 2.7 Key Event Handling (lines 417-430)

**Current (xterm.js):**
```typescript
term.attachCustomKeyEventHandler(event => {
  if (event.ctrlKey && event.key === 'c' && term.hasSelection()) {
    return false;
  }
  if (event.ctrlKey && event.key === 'v' && this._options.pasteWithCtrlV) {
    return false;
  }
  return true;
});
```

**New (ghostty-web has same API):**
```typescript
// Same API - attachCustomKeyEventHandler exists in ghostty-web
term.attachCustomKeyEventHandler(event => {
  if (event.ctrlKey && event.key === 'c' && term.hasSelection()) {
    return false;
  }
  if (event.ctrlKey && event.key === 'v' && this._options.pasteWithCtrlV) {
    return false;
  }
  return true;
});
```

#### 2.8 Theme Conversion (Private.getXTermTheme, lines 579-591)

**Rename and adapt:**
```typescript
export function getGhosttyTheme(theme: ITerminal.Theme): IGhosttyTheme {
  switch (theme) {
    case 'light':
      return {
        foreground: '#000',
        background: '#fff',
        cursor: '#616161',
        // Map other theme properties
      };
    case 'dark':
      return {
        foreground: '#fff',
        background: '#000',
        cursor: '#fff',
        // Map other theme properties
      };
    case 'inherit':
    default:
      return inheritTheme();
  }
}
```

---

### 3. Search Provider (packages/terminal-extension/src/searchprovider.ts)

The current implementation relies heavily on xterm.js's SearchAddon. This needs significant rework since ghostty-web doesn't have an equivalent addon system.

#### 3.1 Option A: Implement Custom Search (Recommended)

Since ghostty-web provides buffer access via `terminal.buffer`, implement search manually:

```typescript
import { Terminal } from '@jupyterlab/terminal';

export class TerminalSearchProvider extends SearchProvider<TerminalWidget> {
  async startQuery(query: RegExp): Promise<void> {
    this._query = query;
    this._matches = [];

    const terminal = this.widget.content;
    // Access terminal buffer to search
    // ghostty-web provides buffer access similar to xterm.js
    const buffer = terminal.buffer.active;

    for (let i = 0; i < buffer.length; i++) {
      const line = buffer.getLine(i);
      if (line) {
        const text = line.translateToString();
        const matches = text.matchAll(query);
        for (const match of matches) {
          this._matches.push({ line: i, start: match.index, length: match[0].length });
        }
      }
    }

    this._currentMatchIndex = this._matches.length > 0 ? 0 : null;
    this._highlightCurrentMatch();
  }

  private _highlightCurrentMatch(): void {
    // Use terminal.select() to highlight matches
    if (this._currentMatchIndex !== null) {
      const match = this._matches[this._currentMatchIndex];
      // ghostty-web provides select(column, row, length) method
    }
  }

  // ... implement highlightNext, highlightPrevious, etc.
}
```

#### 3.2 Option B: Disable Search Initially

As a simpler initial implementation, disable terminal search:

```typescript
export class TerminalSearchProvider extends SearchProvider<TerminalWidget> {
  // Return empty results, inform users search is not yet available
  async startQuery(query: RegExp): Promise<void> {
    console.warn('Terminal search is not yet supported with ghostty-web');
    return Promise.resolve();
  }

  get matchesCount(): number | null {
    return null;
  }
}
```

#### 3.3 Remove xterm.js Types

**Current imports:**
```typescript
import type {
  ISearchDecorationOptions,
  ISearchOptions
} from '@xterm/addon-search';
```

**Remove these imports and related type usage.**

---

### 4. CSS Styles (packages/terminal/style/base.css)

**Current (references .xterm classes):**
```css
[data-term-theme='inherit'] .xterm .xterm-screen canvas {
  border: 1px solid var(--jp-layout-color0);
}

[data-term-theme='light'] .xterm .xterm-screen canvas {
  border: 1px solid #fff;
}

[data-term-theme='dark'] .xterm .xterm-screen canvas {
  border: 1px solid #000;
}
```

**New (update for ghostty-web DOM structure):**

ghostty-web uses `<canvas>` directly. Update selectors:

```css
[data-term-theme='inherit'] .jp-Terminal-body canvas {
  border: 1px solid var(--jp-layout-color0);
}

[data-term-theme='light'] .jp-Terminal-body canvas {
  border: 1px solid #fff;
}

[data-term-theme='dark'] .jp-Terminal-body canvas {
  border: 1px solid #000;
}
```

---

### 5. Interface Changes (packages/terminal/src/tokens.ts)

#### 5.1 Remove SearchAddon References

The `ITerminal.ITerminal` interface should be updated to remove any SearchAddon-specific types.

#### 5.2 Options Compatibility Review

Review `ITerminal.IOptions` for compatibility with ghostty-web:

| Option | xterm.js | ghostty-web | Notes |
|--------|----------|-------------|-------|
| `fontFamily` | ✅ | ✅ | Direct mapping |
| `fontSize` | ✅ | ✅ | Direct mapping |
| `lineHeight` | ✅ | ❓ | May need custom implementation |
| `theme` | ✅ | ✅ | Format differs |
| `scrollback` | ✅ | ✅ | Direct mapping |
| `cursorBlink` | ✅ | ✅ | Direct mapping |
| `screenReaderMode` | ✅ | ❓ | Check ghostty-web support |
| `macOptionIsMeta` | ✅ | ❓ | Check ghostty-web support |

---

### 6. Extension Plugin (packages/terminal-extension/src/index.ts)

#### 6.1 Remove Search Provider Registration (if disabling search)

**Current (line 286):**
```typescript
if (searchRegistry) {
  searchRegistry.add('terminal', TerminalSearchProvider);
}
```

**If search is disabled:**
```typescript
// Comment out or remove
// if (searchRegistry) {
//   searchRegistry.add('terminal', TerminalSearchProvider);
// }
```

#### 6.2 Import Updates

No changes needed to index.ts itself since it imports from `@jupyterlab/terminal` which wraps the terminal implementation.

---

### 7. Tests (packages/terminal/test/terminal.spec.ts)

#### 7.1 Update Test Infrastructure

Tests may need updates for:
- Mock terminal creation
- Async initialization (ghostty-web requires `init()` call)
- Different DOM structure

#### 7.2 Jest Shim Updates

**packages/testing/src/jest-shim.ts** may need updates for ghostty-web mocking.

---

### 8. Build Configuration

#### 8.1 WASM Bundling

ghostty-web includes a ~400KB WASM file that needs to be bundled correctly:

**webpack.config.js changes (if applicable):**
```javascript
{
  test: /\.wasm$/,
  type: 'asset/resource',
}
```

#### 8.2 JupyterLab Builder Configuration

The WASM file needs to be included in the build output. Check if `@jupyterlab/builder` handles this automatically or requires configuration.

---

## API Compatibility Matrix

| xterm.js Method/Property | ghostty-web Equivalent | Notes |
|--------------------------|------------------------|-------|
| `Terminal` constructor | `Terminal` | Options format differs |
| `open(element)` | `open(element)` | Same API |
| `write(data)` | `write(data)` | Same API |
| `dispose()` | `dispose()` | Same API |
| `focus()` | `focus()` | Same API |
| `hasSelection()` | `hasSelection()` | Same API |
| `getSelection()` | `getSelection()` | Same API |
| `paste(data)` | `paste(data)` | Same API |
| `clear()` | `clear()` | Same API |
| `reset()` | `reset()` | Same API |
| `resize(cols, rows)` | `resize(cols, rows)` | Same API |
| `onData` | `onData` | Same event API |
| `onTitleChange` | `onTitleChange` | Same event API |
| `attachCustomKeyEventHandler` | `attachCustomKeyEventHandler` | Same API |
| `loadAddon(addon)` | `loadAddon(addon)` | Limited addon support |
| `options.*` | `options.*` | Proxy-based, similar API |
| `FitAddon.fit()` | Manual resize | No direct equivalent |
| `SearchAddon.*` | N/A | Must implement manually |
| `WebLinksAddon` | Built-in link detection | Different API |

---

## Implementation Strategy

### Phase 1: Basic Terminal Functionality
1. Replace xterm.js dependencies with ghostty-web
2. Update `widget.ts` for basic terminal rendering
3. Update CSS for new DOM structure
4. Verify basic input/output works

### Phase 2: Feature Parity
1. Implement manual fitting logic
2. Implement custom search provider (or disable)
3. Test all terminal options
4. Update theme handling

### Phase 3: Testing & Polish
1. Update unit tests
2. Run E2E tests (galata)
3. Fix visual regressions
4. Performance testing

---

## Risks and Considerations

### 1. Search Functionality
ghostty-web doesn't have a SearchAddon equivalent. The search provider needs to be reimplemented using buffer access APIs.

### 2. Addon Ecosystem
xterm.js has a rich addon ecosystem. ghostty-web's `loadAddon()` method exists but addon availability is limited.

### 3. API Stability
ghostty-web is relatively new (v0.3.0). API changes may occur in future releases.

### 4. Missing Features
Some xterm.js features may not have direct equivalents:
- `screenReaderMode` - accessibility support
- `macOptionIsMeta` - macOS-specific key handling
- `lineHeight` - text rendering control

### 5. WASM Bundle Size
The ~400KB WASM file adds to initial load time. Consider lazy loading strategies.

### 6. Browser Compatibility
WASM support is generally good, but verify with JupyterLab's browser support matrix.

---

## Files Summary

| File | Change Type | Complexity |
|------|-------------|------------|
| `packages/terminal/package.json` | Dependency swap | Low |
| `packages/terminal/src/widget.ts` | Major rewrite | High |
| `packages/terminal/src/tokens.ts` | Interface review | Low |
| `packages/terminal/style/base.css` | CSS selector updates | Low |
| `packages/terminal-extension/package.json` | Dependency removal | Low |
| `packages/terminal-extension/src/searchprovider.ts` | Rewrite or disable | High |
| `packages/terminal-extension/src/index.ts` | Minor updates | Low |
| `packages/terminal/test/terminal.spec.ts` | Test updates | Medium |

---

# Part 2: Extension-Based Implementation (Experimental)

This section describes how to implement ghostty-web as a **standalone JupyterLab extension** that can be installed alongside the existing terminal without modifying JupyterLab core. This approach allows experimentation without risking stability.

## Why an Extension Approach?

1. **No core modifications**: Install/uninstall without touching JupyterLab source
2. **Side-by-side testing**: Run both xterm.js and ghostty-web terminals simultaneously
3. **Easy rollback**: Simply disable the extension to revert
4. **Community distribution**: Share via PyPI/conda without JupyterLab release cycle
5. **Incremental development**: Build and test features independently

---

## Extension Architecture

### Option A: Separate Terminal Type (Recommended for Experimentation)

Create a new "Ghostty Terminal" alongside the existing terminal, allowing users to choose.

```
┌─────────────────────────────────────────────────────────────────┐
│                    JupyterLab Application                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────┐    ┌──────────────────────┐          │
│  │ @jupyterlab/         │    │ jupyterlab-ghostty   │          │
│  │ terminal-extension   │    │ (new extension)      │          │
│  │                      │    │                      │          │
│  │ provides:            │    │ provides:            │          │
│  │ ITerminalTracker     │    │ IGhosttyTracker      │          │
│  └──────────────────────┘    └──────────────────────┘          │
│           │                           │                         │
│           ▼                           ▼                         │
│  ┌──────────────────┐       ┌──────────────────┐               │
│  │ Terminal Widget  │       │ GhosttyTerminal  │               │
│  │ (xterm.js)       │       │ Widget           │               │
│  └──────────────────┘       │ (ghostty-web)    │               │
│                             └──────────────────┘               │
│                                                                  │
│  Launcher shows both:                                           │
│  ┌─────────────┐  ┌─────────────────┐                          │
│  │ Terminal    │  │ Ghostty Terminal│                          │
│  └─────────────┘  └─────────────────┘                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Option B: Full Replacement (Production Ready)

Disable the default terminal and provide `ITerminalTracker` from the extension.

```
┌─────────────────────────────────────────────────────────────────┐
│                    JupyterLab Application                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────┐                                       │
│  │ @jupyterlab/         │  ← DISABLED                           │
│  │ terminal-extension   │                                       │
│  └──────────────────────┘                                       │
│                                                                  │
│  ┌──────────────────────┐                                       │
│  │ jupyterlab-ghostty   │                                       │
│  │                      │                                       │
│  │ provides:            │                                       │
│  │ ITerminalTracker ────┼──→ All terminal consumers use this    │
│  └──────────────────────┘                                       │
│           │                                                     │
│           ▼                                                     │
│  ┌──────────────────┐                                          │
│  │ GhosttyTerminal  │                                          │
│  │ Widget           │                                          │
│  └──────────────────┘                                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
jupyterlab-ghostty/
├── pyproject.toml              # Python package configuration
├── package.json                # npm package configuration
├── tsconfig.json               # TypeScript configuration
├── webpack.config.js           # Webpack bundler config (WASM handling)
├── install.json                # JupyterLab discovery metadata
├── LICENSE
├── README.md
│
├── src/
│   ├── index.ts                # Main plugin entry point
│   ├── widget.ts               # GhosttyTerminal widget
│   ├── tokens.ts               # IGhosttyTracker token (Option A)
│   └── searchprovider.ts       # Custom search implementation
│
├── style/
│   ├── base.css                # Terminal styling
│   └── index.js                # Style imports
│
├── schema/
│   └── plugin.json             # Settings schema
│
└── jupyterlab_ghostty/         # Python package
    └── __init__.py             # Package initialization
```

---

## Implementation Details

### 1. Package Configuration

#### package.json

```json
{
  "name": "jupyterlab-ghostty",
  "version": "0.1.0",
  "description": "JupyterLab terminal using ghostty-web (libghostty WASM)",
  "keywords": [
    "jupyter",
    "jupyterlab",
    "jupyterlab-extension",
    "terminal",
    "ghostty"
  ],
  "homepage": "https://github.com/your-org/jupyterlab-ghostty",
  "license": "BSD-3-Clause",
  "author": {
    "name": "Your Name"
  },
  "files": [
    "lib/**/*.{d.ts,eot,gif,html,jpg,js,js.map,json,png,svg,woff2,ttf,wasm}",
    "style/**/*.{css,js,eot,gif,html,jpg,json,png,svg,woff2,ttf}",
    "schema/*.json"
  ],
  "main": "lib/index.js",
  "types": "lib/index.d.ts",
  "style": "style/index.css",
  "repository": {
    "type": "git",
    "url": "https://github.com/your-org/jupyterlab-ghostty.git"
  },
  "scripts": {
    "build": "jlpm build:lib && jlpm build:labextension:dev",
    "build:prod": "jlpm clean && jlpm build:lib:prod && jlpm build:labextension",
    "build:labextension": "jupyter labextension build .",
    "build:labextension:dev": "jupyter labextension build --development True .",
    "build:lib": "tsc --sourceMap",
    "build:lib:prod": "tsc",
    "clean": "jlpm clean:lib",
    "clean:lib": "rimraf lib tsconfig.tsbuildinfo",
    "clean:lintcache": "rimraf .eslintcache .stylelintcache",
    "clean:labextension": "rimraf jupyterlab_ghostty/labextension jupyterlab_ghostty/_version.py",
    "clean:all": "jlpm clean:lib && jlpm clean:labextension && jlpm clean:lintcache",
    "install:extension": "jlpm build",
    "watch": "run-p watch:src watch:labextension",
    "watch:src": "tsc -w --sourceMap",
    "watch:labextension": "jupyter labextension watch ."
  },
  "dependencies": {
    "@jupyterlab/application": "^4.0.0",
    "@jupyterlab/apputils": "^4.0.0",
    "@jupyterlab/launcher": "^4.0.0",
    "@jupyterlab/mainmenu": "^4.0.0",
    "@jupyterlab/running": "^4.0.0",
    "@jupyterlab/services": "^7.0.0",
    "@jupyterlab/settingregistry": "^4.0.0",
    "@jupyterlab/terminal": "^4.0.0",
    "@jupyterlab/translation": "^4.0.0",
    "@jupyterlab/ui-components": "^4.0.0",
    "@lumino/coreutils": "^2.0.0",
    "@lumino/messaging": "^2.0.0",
    "@lumino/signaling": "^2.0.0",
    "@lumino/widgets": "^2.0.0",
    "color": "^4.0.0",
    "ghostty-web": "^0.3.0"
  },
  "devDependencies": {
    "@jupyterlab/builder": "^4.0.0",
    "@types/color": "^3.0.0",
    "npm-run-all": "^4.1.5",
    "rimraf": "^5.0.0",
    "typescript": "~5.0.0"
  },
  "sideEffects": [
    "style/**/*.css",
    "style/index.js"
  ],
  "styleModule": "style/index.js",
  "publishConfig": {
    "access": "public"
  },
  "jupyterlab": {
    "extension": true,
    "outputDir": "jupyterlab_ghostty/labextension",
    "schemaDir": "schema",
    "webpackConfig": "./webpack.config.js"
  }
}
```

#### pyproject.toml

```toml
[build-system]
requires = ["hatchling>=1.5.0", "jupyterlab>=4.0.0,<5", "hatch-nodejs-version>=0.3.2"]
build-backend = "hatchling.build"

[project]
name = "jupyterlab-ghostty"
readme = "README.md"
license = { file = "LICENSE" }
requires-python = ">=3.8"
classifiers = [
    "Framework :: Jupyter",
    "Framework :: Jupyter :: JupyterLab",
    "Framework :: Jupyter :: JupyterLab :: 4",
    "Framework :: Jupyter :: JupyterLab :: Extensions",
    "Framework :: Jupyter :: JupyterLab :: Extensions :: Prebuilt",
    "License :: OSI Approved :: BSD License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = []
dynamic = ["version", "description", "authors", "urls", "keywords"]

[tool.hatch.version]
source = "nodejs"

[tool.hatch.metadata.hooks.nodejs]
fields = ["description", "authors", "urls"]

[tool.hatch.build.targets.sdist]
artifacts = ["jupyterlab_ghostty/labextension"]
exclude = [".github", "binder"]

[tool.hatch.build.targets.wheel.shared-data]
"jupyterlab_ghostty/labextension" = "share/jupyter/labextensions/jupyterlab-ghostty"
"install.json" = "share/jupyter/labextensions/jupyterlab-ghostty/install.json"

[tool.hatch.build.hooks.version]
path = "jupyterlab_ghostty/_version.py"

[tool.hatch.build.hooks.jupyter-builder]
dependencies = ["hatch-jupyter-builder>=0.5"]
build-function = "hatch_jupyter_builder.npm_builder"
ensured-targets = [
    "jupyterlab_ghostty/labextension/static/style.js",
    "jupyterlab_ghostty/labextension/package.json",
]
skip-if-exists = ["jupyterlab_ghostty/labextension/static/style.js"]

[tool.hatch.build.hooks.jupyter-builder.build-kwargs]
build_cmd = "build:prod"
npm = ["jlpm"]

[tool.hatch.build.hooks.jupyter-builder.editable-build-kwargs]
build_cmd = "install:extension"
npm = ["jlpm"]
source_dir = "src"
build_dir = "jupyterlab_ghostty/labextension"
```

#### webpack.config.js

```javascript
const path = require('path');

module.exports = {
  module: {
    rules: [
      {
        // Handle WASM files from ghostty-web
        test: /\.wasm$/,
        type: 'asset/resource',
        generator: {
          filename: 'static/wasm/[name][ext]'
        }
      }
    ]
  },
  experiments: {
    asyncWebAssembly: true
  }
};
```

---

### 2. Token Definitions (src/tokens.ts)

For Option A (separate terminal type):

```typescript
// src/tokens.ts
import { IWidgetTracker, MainAreaWidget } from '@jupyterlab/apputils';
import { Token } from '@lumino/coreutils';
import { ISignal } from '@lumino/signaling';
import { Widget } from '@lumino/widgets';
import { Terminal } from '@jupyterlab/services';

/**
 * The Ghostty terminal tracker token.
 */
export const IGhosttyTerminalTracker = new Token<IGhosttyTerminalTracker>(
  'jupyterlab-ghostty:IGhosttyTerminalTracker',
  'A widget tracker for Ghostty terminals.'
);

/**
 * A class that tracks Ghostty terminal widgets.
 */
export interface IGhosttyTerminalTracker
  extends IWidgetTracker<MainAreaWidget<IGhosttyTerminal.ITerminal>> {}

/**
 * Ghostty terminal namespace.
 */
export namespace IGhosttyTerminal {
  /**
   * An interface for a Ghostty terminal widget.
   */
  export interface ITerminal extends Widget {
    /**
     * The terminal session associated with the widget.
     */
    session: Terminal.ITerminalConnection;

    /**
     * Get a config option for the terminal.
     */
    getOption<K extends keyof IOptions>(option: K): IOptions[K];

    /**
     * Set a config option for the terminal.
     */
    setOption<K extends keyof IOptions>(option: K, value: IOptions[K]): void;

    /**
     * Refresh the terminal session.
     */
    refresh(): Promise<void>;

    /**
     * Check if terminal has any text selected.
     */
    hasSelection(): boolean;

    /**
     * Paste text into terminal.
     */
    paste(data: string): void;

    /**
     * Get selected text from terminal.
     */
    getSelection(): string | null;

    /**
     * A signal emitted when the terminal theme changes.
     */
    themeChanged: ISignal<this, void>;
  }

  /**
   * Options for the Ghostty terminal widget.
   */
  export interface IOptions {
    fontFamily?: string;
    fontSize: number;
    lineHeight?: number;
    theme: Theme;
    scrollback?: number;
    shutdownOnClose: boolean;
    closeOnExit: boolean;
    cursorBlink: boolean;
    initialCommand: string;
    autoFit?: boolean;
  }

  /**
   * Default options for Ghostty terminal.
   */
  export const defaultOptions: IOptions = {
    theme: 'inherit',
    fontFamily: 'Menlo, Consolas, "DejaVu Sans Mono", monospace',
    fontSize: 13,
    lineHeight: 1.0,
    scrollback: 10000, // ghostty-web default
    shutdownOnClose: false,
    closeOnExit: true,
    cursorBlink: false, // ghostty-web default
    initialCommand: '',
    autoFit: true
  };

  /**
   * Terminal theme type.
   */
  export type Theme = 'light' | 'dark' | 'inherit';

  /**
   * Theme color configuration.
   */
  export interface IThemeObject {
    foreground: string;
    background: string;
    cursor?: string;
  }
}
```

---

### 3. Terminal Widget (src/widget.ts)

```typescript
// src/widget.ts
import { Terminal as TerminalNS } from '@jupyterlab/services';
import {
  ITranslator,
  nullTranslator,
  TranslationBundle
} from '@jupyterlab/translation';
import { PromiseDelegate } from '@lumino/coreutils';
import { Platform } from '@lumino/domutils';
import { Message, MessageLoop } from '@lumino/messaging';
import { ISignal, Signal } from '@lumino/signaling';
import { Widget } from '@lumino/widgets';
import { init as initGhostty, Terminal as GhosttyTerm } from 'ghostty-web';
import Color from 'color';
import { IGhosttyTerminal } from './tokens';

const TERMINAL_CLASS = 'jp-GhosttyTerminal';
const TERMINAL_BODY_CLASS = 'jp-GhosttyTerminal-body';

/**
 * A widget which manages a terminal session using ghostty-web.
 */
export class GhosttyTerminal extends Widget implements IGhosttyTerminal.ITerminal {
  constructor(
    session: TerminalNS.ITerminalConnection,
    options: Partial<IGhosttyTerminal.IOptions> = {},
    translator?: ITranslator
  ) {
    super();
    translator = translator || nullTranslator;
    this._trans = translator.load('jupyterlab');
    this.session = session;

    this._options = { ...IGhosttyTerminal.defaultOptions, ...options };

    this.addClass(TERMINAL_CLASS);
    this._setThemeAttribute(this._options.theme);

    // Buffer messages while terminal initializes
    let buffer = '';
    const bufferMessage = (
      sender: TerminalNS.ITerminalConnection,
      msg: TerminalNS.IMessage
    ): void => {
      if (msg.type === 'stdout' && msg.content) {
        buffer += msg.content[0] as string;
      }
    };
    session.messageReceived.connect(bufferMessage);
    session.disposed.connect(() => {
      if (this.getOption('closeOnExit')) {
        this.dispose();
      }
    }, this);

    // Initialize ghostty-web
    Private.createTerminal({
      theme: Private.getTheme(this._options.theme),
      fontSize: this._options.fontSize,
      fontFamily: this._options.fontFamily,
      scrollback: this._options.scrollback,
      cursorBlink: this._options.cursorBlink
    })
      .then(term => {
        this._term = term;
        this._initializeTerm();

        this.id = `jp-GhosttyTerminal-${Private.id++}`;
        this.title.label = this._trans.__('Ghostty Terminal');
        this._isReady = true;
        this._ready.resolve();

        if (buffer) {
          this._term.write(buffer);
        }
        session.messageReceived.disconnect(bufferMessage);
        session.messageReceived.connect(this._onMessage, this);

        if (session.connectionStatus === 'connected') {
          this._initialConnection();
        } else {
          session.connectionStatusChanged.connect(this._initialConnection, this);
        }
        this.update();
      })
      .catch(reason => {
        console.error('Failed to create Ghostty terminal.\n', reason);
        this._ready.reject(reason);
      });
  }

  /**
   * A promise that resolves when the terminal is ready.
   */
  get ready(): Promise<void> {
    return this._ready.promise;
  }

  /**
   * The terminal session.
   */
  readonly session: TerminalNS.ITerminalConnection;

  /**
   * Get a config option.
   */
  getOption<K extends keyof IGhosttyTerminal.IOptions>(
    option: K
  ): IGhosttyTerminal.IOptions[K] {
    return this._options[option];
  }

  /**
   * Set a config option.
   */
  setOption<K extends keyof IGhosttyTerminal.IOptions>(
    option: K,
    value: IGhosttyTerminal.IOptions[K]
  ): void {
    if (option !== 'theme' && this._options[option] === value) {
      return;
    }

    this._options[option] = value;

    if (!this._term) {
      return;
    }

    switch (option) {
      case 'fontFamily':
        this._term.options.fontFamily = value as string | undefined;
        break;
      case 'fontSize':
        this._term.options.fontSize = value as number | undefined;
        break;
      case 'scrollback':
        this._term.options.scrollback = value as number | undefined;
        break;
      case 'theme':
        this._term.options.theme = Private.getTheme(value as IGhosttyTerminal.Theme);
        this._setThemeAttribute(value as IGhosttyTerminal.Theme);
        this._themeChanged.emit();
        break;
      default:
        break;
    }

    this._needsResize = true;
    this.update();
  }

  /**
   * Dispose of the terminal widget.
   */
  dispose(): void {
    if (!this.session.isDisposed) {
      if (this.getOption('shutdownOnClose')) {
        this.session.shutdown().catch(reason => {
          console.error(`Terminal not shut down: ${reason}`);
        });
      }
    }
    void this.ready.then(() => {
      this._term?.dispose();
    });
    super.dispose();
  }

  /**
   * Refresh the terminal session.
   */
  async refresh(): Promise<void> {
    if (!this.isDisposed && this._isReady) {
      await this.session.reconnect();
      this._term?.clear();
    }
  }

  /**
   * Check if terminal has selection.
   */
  hasSelection(): boolean {
    return this._isReady ? this._term?.hasSelection() ?? false : false;
  }

  /**
   * Paste text into terminal.
   */
  paste(data: string): void {
    if (this._isReady) {
      this._term?.paste(data);
    }
  }

  /**
   * Get selected text.
   */
  getSelection(): string | null {
    return this._isReady ? this._term?.getSelection() ?? null : null;
  }

  /**
   * Process widget messages.
   */
  processMessage(msg: Message): void {
    super.processMessage(msg);
    if (msg.type === 'fit-request') {
      this.onFitRequest(msg);
    }
  }

  /**
   * Signal emitted when theme changes.
   */
  get themeChanged(): ISignal<this, void> {
    return this._themeChanged;
  }

  protected onAfterAttach(msg: Message): void {
    this.update();
  }

  protected onAfterShow(msg: Message): void {
    this.update();
  }

  protected onResize(msg: Widget.ResizeMessage): void {
    this._offsetWidth = msg.width;
    this._offsetHeight = msg.height;
    this._needsResize = true;
    this.update();
  }

  protected onUpdateRequest(msg: Message): void {
    if (!this.isVisible || !this.isAttached || !this._isReady) {
      return;
    }

    if (!this._termOpened) {
      this._term?.open(this.node);
      this.node.querySelector('.ghostty-terminal')?.classList.add(TERMINAL_BODY_CLASS);
      this._termOpened = true;
    }

    if (this._needsResize) {
      this._resizeTerminal();
    }
  }

  protected onFitRequest(msg: Message): void {
    MessageLoop.sendMessage(this, Widget.ResizeMessage.UnknownSize);
  }

  protected onActivateRequest(msg: Message): void {
    this._term?.focus();
  }

  private _initialConnection(): void {
    if (this.isDisposed || this.session.connectionStatus !== 'connected') {
      return;
    }

    this.title.label = this._trans.__('Ghostty %1', this.session.name);
    this._setSessionSize();

    if (this._options.initialCommand) {
      this.session.send({
        type: 'stdin',
        content: [this._options.initialCommand + '\r']
      });
    }

    this.session.connectionStatusChanged.disconnect(this._initialConnection, this);
  }

  private _initializeTerm(): void {
    const term = this._term!;

    term.onData((data: string) => {
      if (!this.isDisposed) {
        this.session.send({ type: 'stdin', content: [data] });
      }
    });

    term.onTitleChange((title: string) => {
      this.title.label = title;
    });

    // Custom key handling (same as xterm.js version)
    if (!Platform.IS_MAC) {
      term.attachCustomKeyEventHandler(event => {
        if (event.ctrlKey && event.key === 'c' && term.hasSelection()) {
          return false; // Allow OS copy
        }
        return true;
      });
    }
  }

  private _onMessage(
    sender: TerminalNS.ITerminalConnection,
    msg: TerminalNS.IMessage
  ): void {
    switch (msg.type) {
      case 'stdout':
        if (msg.content) {
          this._term?.write(msg.content[0] as string);
        }
        break;
      case 'disconnect':
        this._term?.write('\r\n\r\n[Finished… Term Session]\r\n');
        break;
    }
  }

  private _resizeTerminal(): void {
    if (!this._term) return;

    if (this._options.autoFit) {
      // Calculate dimensions based on container and font size
      const dims = this._calculateDimensions();
      if (dims) {
        this._term.resize(dims.cols, dims.rows);
      }
    }

    if (this._offsetWidth === -1) {
      this._offsetWidth = this.node.offsetWidth;
    }
    if (this._offsetHeight === -1) {
      this._offsetHeight = this.node.offsetHeight;
    }

    this._setSessionSize();
    this._needsResize = false;
  }

  private _calculateDimensions(): { cols: number; rows: number } | null {
    if (!this._term) return null;

    // Get container dimensions
    const width = this.node.clientWidth;
    const height = this.node.clientHeight;

    // Estimate character dimensions (ghostty-web doesn't expose this directly)
    // Use approximate values based on font size
    const fontSize = this._options.fontSize;
    const charWidth = fontSize * 0.6;  // Approximate monospace ratio
    const charHeight = fontSize * (this._options.lineHeight || 1.0) * 1.2;

    const cols = Math.max(2, Math.floor(width / charWidth) - 1);
    const rows = Math.max(1, Math.floor(height / charHeight) - 1);

    return { cols, rows };
  }

  private _setSessionSize(): void {
    if (!this._term || this.isDisposed) return;

    const content = [
      this._term.rows,
      this._term.cols,
      this._offsetHeight,
      this._offsetWidth
    ];
    this.session.send({ type: 'set_size', content });
  }

  private _setThemeAttribute(theme: string | null | undefined): void {
    if (this.isDisposed) return;
    this.node.setAttribute(
      'data-term-theme',
      theme ? theme.toLowerCase() : 'inherit'
    );
  }

  private _needsResize = true;
  private _offsetWidth = -1;
  private _offsetHeight = -1;
  private _options: IGhosttyTerminal.IOptions;
  private _isReady = false;
  private _ready = new PromiseDelegate<void>();
  private _term: GhosttyTerm | null = null;
  private _termOpened = false;
  private _trans: TranslationBundle;
  private _themeChanged = new Signal<this, void>(this);
}

/**
 * Private namespace for helper functions.
 */
namespace Private {
  export let id = 0;
  let initialized = false;

  export const lightTheme: IGhosttyTerminal.IThemeObject = {
    foreground: '#000',
    background: '#fff',
    cursor: '#616161'
  };

  export const darkTheme: IGhosttyTerminal.IThemeObject = {
    foreground: '#fff',
    background: '#000',
    cursor: '#fff'
  };

  export function inheritTheme(): IGhosttyTerminal.IThemeObject {
    const bodyStyle = getComputedStyle(document.body);
    return {
      foreground: bodyStyle.getPropertyValue('--jp-ui-font-color0').trim(),
      background: bodyStyle.getPropertyValue('--jp-layout-color0').trim(),
      cursor: bodyStyle.getPropertyValue('--jp-ui-font-color1').trim()
    };
  }

  export function getTheme(
    theme: IGhosttyTerminal.Theme
  ): IGhosttyTerminal.IThemeObject {
    switch (theme) {
      case 'light':
        return lightTheme;
      case 'dark':
        return darkTheme;
      case 'inherit':
      default:
        return inheritTheme();
    }
  }

  export async function createTerminal(
    options: any
  ): Promise<GhosttyTerm> {
    if (!initialized) {
      await initGhostty();
      initialized = true;
    }
    return new GhosttyTerm(options);
  }
}
```

---

### 4. Plugin Entry Point (src/index.ts)

```typescript
// src/index.ts
import {
  ILayoutRestorer,
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import {
  ICommandPalette,
  IThemeManager,
  MainAreaWidget,
  WidgetTracker
} from '@jupyterlab/apputils';
import { ILauncher } from '@jupyterlab/launcher';
import { IMainMenu } from '@jupyterlab/mainmenu';
import { IRunningSessionManagers, IRunningSessions } from '@jupyterlab/running';
import { Terminal, TerminalAPI } from '@jupyterlab/services';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { ITranslator } from '@jupyterlab/translation';
import { LabIcon } from '@jupyterlab/ui-components';
import { Menu } from '@lumino/widgets';

import { GhosttyTerminal } from './widget';
import { IGhosttyTerminal, IGhosttyTerminalTracker } from './tokens';

// Custom icon for Ghostty terminal
const ghosttyIcon = new LabIcon({
  name: 'jupyterlab-ghostty:icon',
  svgstr: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
    <rect x="2" y="4" width="20" height="16" rx="2" fill="none" stroke="currentColor" stroke-width="2"/>
    <text x="6" y="16" font-family="monospace" font-size="10" fill="currentColor">&gt;_</text>
  </svg>`
});

/**
 * Command IDs for the Ghostty terminal.
 */
namespace CommandIDs {
  export const createNew = 'ghostty-terminal:create-new';
  export const open = 'ghostty-terminal:open';
  export const refresh = 'ghostty-terminal:refresh';
  export const increaseFont = 'ghostty-terminal:increase-font';
  export const decreaseFont = 'ghostty-terminal:decrease-font';
  export const setTheme = 'ghostty-terminal:set-theme';
  export const shutdown = 'ghostty-terminal:shutdown';
}

/**
 * The Ghostty terminal extension.
 */
const plugin: JupyterFrontEndPlugin<IGhosttyTerminalTracker> = {
  id: 'jupyterlab-ghostty:plugin',
  description: 'Adds Ghostty-based terminal emulator to JupyterLab.',
  autoStart: true,
  provides: IGhosttyTerminalTracker,
  requires: [ISettingRegistry, ITranslator],
  optional: [
    ICommandPalette,
    ILauncher,
    ILayoutRestorer,
    IMainMenu,
    IThemeManager,
    IRunningSessionManagers
  ],
  activate
};

export default plugin;

/**
 * Activate the Ghostty terminal extension.
 */
function activate(
  app: JupyterFrontEnd,
  settingRegistry: ISettingRegistry,
  translator: ITranslator,
  palette: ICommandPalette | null,
  launcher: ILauncher | null,
  restorer: ILayoutRestorer | null,
  mainMenu: IMainMenu | null,
  themeManager: IThemeManager | null,
  runningSessionManagers: IRunningSessionManagers | null
): IGhosttyTerminalTracker {
  const trans = translator.load('jupyterlab');
  const { serviceManager, commands } = app;
  const category = trans.__('Ghostty Terminal');
  const namespace = 'ghostty-terminal';

  const tracker = new WidgetTracker<MainAreaWidget<IGhosttyTerminal.ITerminal>>({
    namespace
  });

  // Check if terminals are available
  if (!serviceManager.terminals.isAvailable()) {
    console.warn('Ghostty terminal disabled: terminals not available on server');
    return tracker;
  }

  // Restore state
  if (restorer) {
    void restorer.restore(tracker, {
      command: CommandIDs.createNew,
      args: widget => ({ name: widget.content.session.name }),
      name: widget => `ghostty-${widget.content.session.name}`
    });
  }

  // Options from settings
  const options: Partial<IGhosttyTerminal.IOptions> = {};

  function updateOptions(settings: ISettingRegistry.ISettings): void {
    Object.keys(settings.composite).forEach((key: keyof IGhosttyTerminal.IOptions) => {
      (options as any)[key] = settings.composite[key];
    });
  }

  function updateTracker(): void {
    tracker.forEach(widget => {
      const terminal = widget.content;
      Object.keys(options).forEach((key: keyof IGhosttyTerminal.IOptions) => {
        terminal.setOption(key, options[key]);
      });
    });
  }

  // Load settings
  settingRegistry
    .load(plugin.id)
    .then(settings => {
      updateOptions(settings);
      updateTracker();
      settings.changed.connect(() => {
        updateOptions(settings);
        updateTracker();
      });
    })
    .catch(err => console.error(`Failed to load settings: ${err}`));

  // Theme changes
  themeManager?.themeChanged.connect(() => {
    tracker.forEach(widget => {
      if (widget.content.getOption('theme') === 'inherit') {
        widget.content.setOption('theme', 'inherit');
      }
    });
  });

  // Add commands
  commands.addCommand(CommandIDs.createNew, {
    label: args =>
      args['isPalette']
        ? trans.__('New Ghostty Terminal')
        : trans.__('Ghostty Terminal'),
    caption: trans.__('Start a new Ghostty terminal session'),
    icon: args => (args['isPalette'] ? undefined : ghosttyIcon),
    execute: async args => {
      const name = args['name'] as string;
      const cwd = args['cwd'] as string;
      const localPath = cwd
        ? serviceManager.contents.localPath(cwd)
        : undefined;

      let session;
      if (name) {
        const models = await TerminalAPI.listRunning(
          serviceManager.serverSettings
        );
        if (models.map(d => d.name).includes(name)) {
          session = serviceManager.terminals.connectTo({ model: { name } });
        } else {
          session = await serviceManager.terminals.startNew({
            name,
            cwd: localPath
          });
        }
      } else {
        session = await serviceManager.terminals.startNew({ cwd: localPath });
      }

      const term = new GhosttyTerminal(session, options, translator);
      term.title.icon = ghosttyIcon;
      term.title.label = '...';

      const main = new MainAreaWidget({ content: term, reveal: term.ready });
      app.shell.add(main, 'main', { type: 'Terminal' });
      void tracker.add(main);
      app.shell.activateById(main.id);
      return main;
    }
  });

  commands.addCommand(CommandIDs.refresh, {
    label: trans.__('Refresh Ghostty Terminal'),
    execute: async () => {
      const current = tracker.currentWidget;
      if (current) {
        await current.content.refresh();
      }
    },
    isEnabled: () => tracker.currentWidget !== null
  });

  commands.addCommand(CommandIDs.shutdown, {
    label: trans.__('Shutdown Ghostty Terminal'),
    execute: () => {
      const current = tracker.currentWidget;
      if (current) {
        return current.content.session.shutdown();
      }
    },
    isEnabled: () => tracker.currentWidget !== null
  });

  commands.addCommand(CommandIDs.increaseFont, {
    label: trans.__('Increase Ghostty Terminal Font Size'),
    execute: async () => {
      const { fontSize } = options;
      if (fontSize && fontSize < 72) {
        await settingRegistry.set(plugin.id, 'fontSize', fontSize + 1);
      }
    }
  });

  commands.addCommand(CommandIDs.decreaseFont, {
    label: trans.__('Decrease Ghostty Terminal Font Size'),
    execute: async () => {
      const { fontSize } = options;
      if (fontSize && fontSize > 9) {
        await settingRegistry.set(plugin.id, 'fontSize', fontSize - 1);
      }
    }
  });

  commands.addCommand(CommandIDs.setTheme, {
    label: args => {
      const theme = args['theme'] as string;
      const displayName = args['displayName'] as string;
      return args['isPalette']
        ? trans.__('Use Ghostty Theme: %1', displayName)
        : displayName;
    },
    isToggled: args => args['theme'] === options.theme,
    execute: async args => {
      const theme = args['theme'] as IGhosttyTerminal.Theme;
      await settingRegistry.set(plugin.id, 'theme', theme);
    }
  });

  // Add to command palette
  if (palette) {
    [CommandIDs.createNew, CommandIDs.refresh, CommandIDs.increaseFont, CommandIDs.decreaseFont].forEach(command => {
      palette.addItem({ command, category, args: { isPalette: true } });
    });

    ['inherit', 'light', 'dark'].forEach(theme => {
      palette.addItem({
        command: CommandIDs.setTheme,
        category,
        args: {
          theme,
          displayName: trans.__(theme.charAt(0).toUpperCase() + theme.slice(1)),
          isPalette: true
        }
      });
    });
  }

  // Add to launcher
  if (launcher) {
    launcher.add({
      command: CommandIDs.createNew,
      category: trans.__('Other'),
      rank: 1
    });
  }

  // Add to main menu
  if (mainMenu) {
    const themeMenu = new Menu({ commands });
    themeMenu.title.label = trans._p('menu', 'Ghostty Theme');
    ['inherit', 'light', 'dark'].forEach(theme => {
      themeMenu.addItem({
        command: CommandIDs.setTheme,
        args: {
          theme,
          displayName: trans.__(theme.charAt(0).toUpperCase() + theme.slice(1)),
          isPalette: false
        }
      });
    });

    mainMenu.settingsMenu.addGroup(
      [
        { command: CommandIDs.increaseFont },
        { command: CommandIDs.decreaseFont },
        { type: 'submenu', submenu: themeMenu }
      ],
      41
    );

    mainMenu.fileMenu.newMenu.addItem({
      command: CommandIDs.createNew,
      rank: 21
    });
  }

  // Add to running sessions panel
  if (runningSessionManagers) {
    const manager = serviceManager.terminals;

    class RunningGhosttyTerminal implements IRunningSessions.IRunningItem {
      constructor(private _model: Terminal.IModel) {}
      open() {
        void commands.execute(CommandIDs.open, { name: this._model.name });
      }
      icon() {
        return ghosttyIcon;
      }
      label() {
        return `ghostty/${this._model.name}`;
      }
      shutdown() {
        return manager.shutdown(this._model.name);
      }
    }

    // Note: This creates a separate section from standard terminals
    // Users can see both types in the running panel
    runningSessionManagers.add({
      name: trans.__('Ghostty Terminals'),
      supportsMultipleViews: false,
      running: () =>
        Array.from(manager.running())
          .filter(model => {
            // Only show terminals managed by this extension
            return tracker.find(w => w.content.session.name === model.name) !== undefined;
          })
          .map(model => new RunningGhosttyTerminal(model)),
      shutdownAll: () => {
        // Only shutdown terminals managed by this tracker
        const promises: Promise<void>[] = [];
        tracker.forEach(widget => {
          promises.push(widget.content.session.shutdown());
        });
        return Promise.all(promises).then(() => {});
      },
      refreshRunning: () => manager.refreshRunning(),
      runningChanged: manager.runningChanged,
      shutdownLabel: trans.__('Shut Down'),
      shutdownAllLabel: trans.__('Shut Down All')
    });
  }

  return tracker;
}

// Re-export tokens
export * from './tokens';
```

---

### 5. Settings Schema (schema/plugin.json)

```json
{
  "jupyter.lab.setting-icon": "jupyterlab-ghostty:icon",
  "jupyter.lab.setting-icon-label": "Ghostty Terminal",
  "title": "Ghostty Terminal",
  "description": "Ghostty terminal settings (powered by libghostty WASM).",
  "definitions": {
    "fontFamily": {
      "type": "string"
    },
    "fontSize": {
      "type": "integer",
      "minimum": 9,
      "maximum": 72
    },
    "lineHeight": {
      "type": "number",
      "minimum": 1.0
    },
    "theme": {
      "enum": ["dark", "light", "inherit"]
    },
    "scrollback": {
      "type": "number"
    }
  },
  "properties": {
    "fontFamily": {
      "title": "Font family",
      "description": "The font family used to render text.",
      "$ref": "#/definitions/fontFamily",
      "default": "monospace"
    },
    "fontSize": {
      "title": "Font size",
      "description": "The font size used to render text.",
      "$ref": "#/definitions/fontSize",
      "default": 13
    },
    "lineHeight": {
      "title": "Line height",
      "description": "The line height used to render text.",
      "$ref": "#/definitions/lineHeight",
      "default": 1.0
    },
    "theme": {
      "title": "Theme",
      "description": "The theme for the Ghostty terminal.",
      "$ref": "#/definitions/theme",
      "default": "inherit"
    },
    "scrollback": {
      "title": "Scrollback Buffer",
      "description": "The amount of scrollback beyond initial viewport (default: 10000)",
      "$ref": "#/definitions/scrollback",
      "default": 10000
    },
    "shutdownOnClose": {
      "title": "Shut down on close",
      "description": "Shut down the session when closing the terminal.",
      "type": "boolean",
      "default": false
    },
    "closeOnExit": {
      "title": "Close on exit",
      "description": "Close the widget when exiting the terminal.",
      "type": "boolean",
      "default": true
    },
    "cursorBlink": {
      "title": "Blinking cursor",
      "description": "Whether to blink the cursor.",
      "type": "boolean",
      "default": false
    }
  },
  "additionalProperties": false,
  "type": "object"
}
```

---

### 6. Styles (style/base.css)

```css
/*
 * Ghostty Terminal Styles
 */

.jp-GhosttyTerminal {
  min-width: 240px;
  min-height: 120px;
}

.jp-GhosttyTerminal-body {
  padding: 8px;
}

/* Theme-specific styling */
[data-term-theme='inherit'] .jp-GhosttyTerminal-body canvas {
  border: 1px solid var(--jp-layout-color0);
}

[data-term-theme='light'] .jp-GhosttyTerminal-body canvas {
  border: 1px solid #fff;
}

[data-term-theme='dark'] .jp-GhosttyTerminal-body canvas {
  border: 1px solid #000;
}

/* Ensure canvas fills container */
.jp-GhosttyTerminal canvas {
  display: block;
}
```

#### style/index.js

```javascript
import './base.css';
```

---

## Installation & Usage

### Development Installation

```bash
# Clone the extension repository
git clone https://github.com/your-org/jupyterlab-ghostty.git
cd jupyterlab-ghostty

# Install dependencies
jlpm install

# Build the extension
jlpm build

# Install in development mode
pip install -e "."

# Link for development
jupyter labextension develop . --overwrite

# Watch for changes
jlpm watch
```

### Production Installation

```bash
# Install from PyPI (once published)
pip install jupyterlab-ghostty

# Or install from source
pip install git+https://github.com/your-org/jupyterlab-ghostty.git
```

### Using Both Terminals Side-by-Side

Once installed, users will see both terminal options:

1. **Launcher**: Shows both "Terminal" (xterm.js) and "Ghostty Terminal"
2. **Command Palette**: Both `New Terminal` and `New Ghostty Terminal`
3. **File Menu**: Both options under File > New
4. **Running Panel**: Separate sections for each terminal type

### Switching to Ghostty-Only (Option B)

To fully replace the default terminal:

```bash
# Disable the default terminal extension
jupyter labextension disable @jupyterlab/terminal-extension:plugin

# The Ghostty extension will now be the only terminal option
```

---

## Extension vs Core: Trade-offs

| Aspect | Extension Approach | Core Modification |
|--------|-------------------|-------------------|
| **Installation** | Simple pip install | Requires JupyterLab rebuild |
| **Updates** | Independent release cycle | Tied to JupyterLab releases |
| **Risk** | Easy to disable/rollback | Affects all users |
| **Testing** | Side-by-side comparison | Replace only |
| **Maintenance** | Separate codebase | Integrated with core |
| **Integration** | May miss some features | Full access to internals |
| **Search** | Must implement separately | Can modify searchprovider.ts |

---

## Future Enhancements

1. **Search Support**: Implement custom search using ghostty-web's buffer API
2. **Copy/Paste Commands**: Add context menu entries
3. **Keybinding Customization**: Allow users to configure shortcuts
4. **Performance Metrics**: Compare rendering performance vs xterm.js
5. **Accessibility**: Ensure screen reader compatibility
6. **Configuration Sync**: Share settings between terminal types

---

## References

- [Feature Request Issue #17702](https://github.com/jupyterlab/jupyterlab/issues/17702)
- [ghostty-web Repository](https://github.com/coder/ghostty-web)
- [JupyterLab Extension Development](https://jupyterlab.readthedocs.io/en/latest/extension/extension_dev.html)
- [JupyterLab Extension Template](https://github.com/jupyterlab/extension-template)
- [JupyterLab Extension Examples](https://github.com/jupyterlab/extension-examples)
