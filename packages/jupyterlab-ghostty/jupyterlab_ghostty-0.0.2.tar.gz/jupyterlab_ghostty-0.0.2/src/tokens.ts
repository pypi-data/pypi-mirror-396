import { IWidgetTracker, MainAreaWidget } from '@jupyterlab/apputils';
import { Token } from '@lumino/coreutils';
import { ISignal } from '@lumino/signaling';
import { Widget } from '@lumino/widgets';
import { Terminal } from '@jupyterlab/services';

export const IGhosttyTerminalTracker = new Token<IGhosttyTerminalTracker>(
  'jupyterlab-ghostty:IGhosttyTerminalTracker',
  'A widget tracker for Ghostty terminals.'
);

export interface IGhosttyTerminalTracker
  extends IWidgetTracker<MainAreaWidget<IGhosttyTerminal.ITerminal>> {}

export namespace IGhosttyTerminal {
  export interface ITerminal extends Widget {
    session: Terminal.ITerminalConnection;
    getOption<K extends keyof IOptions>(option: K): IOptions[K];
    setOption<K extends keyof IOptions>(option: K, value: IOptions[K]): void;
    refresh(): Promise<void>;
    hasSelection(): boolean;
    paste(data: string): void;
    getSelection(): string | null;
    themeChanged: ISignal<this, void>;
  }

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

  export const defaultOptions: IOptions = {
    theme: 'inherit',
    fontFamily: 'Menlo, Consolas, "DejaVu Sans Mono", monospace',
    fontSize: 13,
    lineHeight: 1.0,
    scrollback: 10000,
    shutdownOnClose: false,
    closeOnExit: true,
    cursorBlink: false,
    initialCommand: '',
    autoFit: true
  };

  export type Theme = 'light' | 'dark' | 'inherit';

  export interface IThemeObject {
    foreground: string;
    background: string;
    cursor?: string;
    cursorAccent?: string;
    selectionBackground?: string;
    selectionForeground?: string;
    // Standard ANSI colors (0-7)
    black?: string;
    red?: string;
    green?: string;
    yellow?: string;
    blue?: string;
    magenta?: string;
    cyan?: string;
    white?: string;
    // Bright ANSI colors (8-15)
    brightBlack?: string;
    brightRed?: string;
    brightGreen?: string;
    brightYellow?: string;
    brightBlue?: string;
    brightMagenta?: string;
    brightCyan?: string;
    brightWhite?: string;
  }
}
