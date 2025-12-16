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
import { IGhosttyTerminal } from './tokens';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type GhosttyTerm = any;
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type GhosttyFitAddon = any;

const TERMINAL_CLASS = 'jp-GhosttyTerminal';
const TERMINAL_BODY_CLASS = 'jp-GhosttyTerminal-body';

export class GhosttyTerminal
  extends Widget
  implements IGhosttyTerminal.ITerminal
{
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

    Private.createTerminal({
      theme: Private.getTheme(this._options.theme),
      fontSize: this._options.fontSize,
      fontFamily: this._options.fontFamily,
      scrollback: this._options.scrollback,
      cursorBlink: this._options.cursorBlink
    })
      .then(({ term, fitAddon }) => {
        this._term = term;
        this._fitAddon = fitAddon;
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
          session.connectionStatusChanged.connect(
            this._initialConnection,
            this
          );
        }
        this.update();
      })
      .catch(reason => {
        console.error('Failed to create Ghostty terminal.\n', reason);
        this._ready.reject(reason);
      });
  }

  get ready(): Promise<void> {
    return this._ready.promise;
  }

  readonly session: TerminalNS.ITerminalConnection;

  getOption<K extends keyof IGhosttyTerminal.IOptions>(
    option: K
  ): IGhosttyTerminal.IOptions[K] {
    return this._options[option];
  }

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
        this._term.options.theme = Private.getTheme(
          value as IGhosttyTerminal.Theme
        );
        this._setThemeAttribute(value as IGhosttyTerminal.Theme);
        this._themeChanged.emit();
        break;
      default:
        break;
    }

    this._needsResize = true;
    this.update();
  }

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

  async refresh(): Promise<void> {
    if (!this.isDisposed && this._isReady) {
      await this.session.reconnect();
      this._term?.clear();
    }
  }

  hasSelection(): boolean {
    return this._isReady ? this._term?.hasSelection() ?? false : false;
  }

  paste(data: string): void {
    if (this._isReady) {
      this._term?.paste(data);
    }
  }

  getSelection(): string | null {
    return this._isReady ? this._term?.getSelection() ?? null : null;
  }

  processMessage(msg: Message): void {
    super.processMessage(msg);
    if (msg.type === 'fit-request') {
      this.onFitRequest(msg);
    }
  }

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
      const termContainer = this.node.querySelector('canvas')?.parentElement;
      if (termContainer) {
        termContainer.classList.add(TERMINAL_BODY_CLASS);
      }
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

    this.session.connectionStatusChanged.disconnect(
      this._initialConnection,
      this
    );
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

    // On non-Mac platforms, allow Ctrl+C to copy when text is selected
    if (!Platform.IS_MAC) {
      term.attachCustomKeyEventHandler((event: KeyboardEvent) => {
        if (event.ctrlKey && event.key === 'c' && term.hasSelection()) {
          return false;
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
    if (!this._term || !this._fitAddon) return;

    // Use FitAddon for proper terminal sizing
    if (this._options.autoFit) {
      try {
        this._fitAddon.fit();
      } catch (err) {
        console.error('Error fitting terminal:', err);
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
  private _fitAddon: GhosttyFitAddon | null = null;
  private _termOpened = false;
  private _trans: TranslationBundle;
  private _themeChanged = new Signal<this, void>(this);
}

namespace Private {
  export let id = 0;
  let initialized = false;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let GhosttyTerminal_: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let GhosttyFitAddon_: any;

  export const lightTheme: IGhosttyTerminal.IThemeObject = {
    foreground: '#000000',
    background: '#ffffff',
    cursor: '#616161',
    cursorAccent: '#ffffff',
    selectionBackground: '#add6ff',
    selectionForeground: '#000000',
    black: '#000000',
    red: '#cd3131',
    green: '#00bc00',
    yellow: '#949800',
    blue: '#0451a5',
    magenta: '#bc05bc',
    cyan: '#0598bc',
    white: '#555555',
    brightBlack: '#666666',
    brightRed: '#cd3131',
    brightGreen: '#14ce14',
    brightYellow: '#b5ba00',
    brightBlue: '#0451a5',
    brightMagenta: '#bc05bc',
    brightCyan: '#0598bc',
    brightWhite: '#a5a5a5'
  };

  export const darkTheme: IGhosttyTerminal.IThemeObject = {
    foreground: '#d4d4d4',
    background: '#1e1e1e',
    cursor: '#ffffff',
    cursorAccent: '#000000',
    selectionBackground: '#264f78',
    selectionForeground: '#ffffff',
    black: '#000000',
    red: '#cd3131',
    green: '#0dbc79',
    yellow: '#e5e510',
    blue: '#2472c8',
    magenta: '#bc3fbc',
    cyan: '#11a8cd',
    white: '#e5e5e5',
    brightBlack: '#666666',
    brightRed: '#f14c4c',
    brightGreen: '#23d18b',
    brightYellow: '#f5f543',
    brightBlue: '#3b8eea',
    brightMagenta: '#d670d6',
    brightCyan: '#29b8db',
    brightWhite: '#ffffff'
  };

  export function inheritTheme(): IGhosttyTerminal.IThemeObject {
    const bodyStyle = getComputedStyle(document.body);
    const bg = bodyStyle.getPropertyValue('--jp-layout-color0').trim();
    // Detect if dark theme by checking background luminance
    const isDark = bg && bg.toLowerCase() < '#808080';
    const baseTheme = isDark ? darkTheme : lightTheme;

    return {
      foreground:
        bodyStyle.getPropertyValue('--jp-ui-font-color0').trim() ||
        baseTheme.foreground,
      background: bg || baseTheme.background,
      cursor:
        bodyStyle.getPropertyValue('--jp-ui-font-color1').trim() ||
        baseTheme.cursor,
      cursorAccent: baseTheme.cursorAccent,
      selectionBackground:
        bodyStyle.getPropertyValue('--jp-editor-selected-background').trim() ||
        baseTheme.selectionBackground,
      selectionForeground: baseTheme.selectionForeground,
      black: baseTheme.black,
      red: baseTheme.red,
      green: baseTheme.green,
      yellow: baseTheme.yellow,
      blue: baseTheme.blue,
      magenta: baseTheme.magenta,
      cyan: baseTheme.cyan,
      white: baseTheme.white,
      brightBlack: baseTheme.brightBlack,
      brightRed: baseTheme.brightRed,
      brightGreen: baseTheme.brightGreen,
      brightYellow: baseTheme.brightYellow,
      brightBlue: baseTheme.brightBlue,
      brightMagenta: baseTheme.brightMagenta,
      brightCyan: baseTheme.brightCyan,
      brightWhite: baseTheme.brightWhite
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
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    options: any
  ): Promise<{ term: GhosttyTerm; fitAddon: GhosttyFitAddon }> {
    if (!initialized) {
      const ghostty = await import('ghostty-web');
      await ghostty.init();
      GhosttyTerminal_ = ghostty.Terminal;
      GhosttyFitAddon_ = ghostty.FitAddon;
      initialized = true;
    }
    const term = new GhosttyTerminal_(options);
    const fitAddon = new GhosttyFitAddon_();
    term.loadAddon(fitAddon);
    return { term, fitAddon };
  }
}
