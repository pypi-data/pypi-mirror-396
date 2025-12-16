"use strict";
(self["webpackChunkjupyterlab_ghostty"] = self["webpackChunkjupyterlab_ghostty"] || []).push([["lib_index_js"],{

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   IGhosttyTerminal: () => (/* reexport safe */ _tokens__WEBPACK_IMPORTED_MODULE_11__.IGhosttyTerminal),
/* harmony export */   IGhosttyTerminalTracker: () => (/* reexport safe */ _tokens__WEBPACK_IMPORTED_MODULE_11__.IGhosttyTerminalTracker),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/application */ "webpack/sharing/consume/default/@jupyterlab/application");
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/launcher */ "webpack/sharing/consume/default/@jupyterlab/launcher");
/* harmony import */ var _jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/mainmenu */ "webpack/sharing/consume/default/@jupyterlab/mainmenu");
/* harmony import */ var _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _jupyterlab_running__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @jupyterlab/running */ "webpack/sharing/consume/default/@jupyterlab/running");
/* harmony import */ var _jupyterlab_running__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_running__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @jupyterlab/settingregistry */ "webpack/sharing/consume/default/@jupyterlab/settingregistry");
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_6__);
/* harmony import */ var _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! @jupyterlab/translation */ "webpack/sharing/consume/default/@jupyterlab/translation");
/* harmony import */ var _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_7___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_translation__WEBPACK_IMPORTED_MODULE_7__);
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_8___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_8__);
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_9___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_9__);
/* harmony import */ var _widget__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! ./widget */ "./lib/widget.js");
/* harmony import */ var _tokens__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! ./tokens */ "./lib/tokens.js");












const ghosttyIconSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
  <rect x="2" y="4" width="20" height="16" rx="2" fill="none" stroke="currentColor" stroke-width="2"/>
  <text x="6" y="16" font-family="monospace" font-size="10" fill="currentColor">&gt;_</text>
</svg>`;
const ghosttyIcon = new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_8__.LabIcon({
    name: 'jupyterlab-ghostty:icon',
    svgstr: ghosttyIconSvg
});
var CommandIDs;
(function (CommandIDs) {
    CommandIDs.createNew = 'ghostty-terminal:create-new';
    CommandIDs.open = 'ghostty-terminal:open';
    CommandIDs.refresh = 'ghostty-terminal:refresh';
    CommandIDs.increaseFont = 'ghostty-terminal:increase-font';
    CommandIDs.decreaseFont = 'ghostty-terminal:decrease-font';
    CommandIDs.setTheme = 'ghostty-terminal:set-theme';
    CommandIDs.shutdown = 'ghostty-terminal:shutdown';
})(CommandIDs || (CommandIDs = {}));
const plugin = {
    id: 'jupyterlab-ghostty:plugin',
    description: 'Adds Ghostty-based terminal emulator to JupyterLab.',
    autoStart: true,
    provides: _tokens__WEBPACK_IMPORTED_MODULE_11__.IGhosttyTerminalTracker,
    requires: [_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_6__.ISettingRegistry, _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_7__.ITranslator],
    optional: [
        _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ICommandPalette,
        _jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_2__.ILauncher,
        _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__.ILayoutRestorer,
        _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_3__.IMainMenu,
        _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.IThemeManager,
        _jupyterlab_running__WEBPACK_IMPORTED_MODULE_4__.IRunningSessionManagers
    ],
    activate
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);
function activate(app, settingRegistry, translator, palette, launcher, restorer, mainMenu, themeManager, runningSessionManagers) {
    const trans = translator.load('jupyterlab');
    const { serviceManager, commands } = app;
    const category = trans.__('Ghostty Terminal');
    const namespace = 'ghostty-terminal';
    const tracker = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.WidgetTracker({
        namespace
    });
    if (!serviceManager.terminals.isAvailable()) {
        console.warn('Ghostty terminal disabled: terminals not available on server');
        return tracker;
    }
    if (restorer) {
        void restorer.restore(tracker, {
            command: CommandIDs.createNew,
            args: widget => ({ name: widget.content.session.name }),
            name: widget => `ghostty-${widget.content.session.name}`
        });
    }
    const options = {};
    function updateOptions(settings) {
        const composite = settings.composite;
        Object.keys(composite).forEach(key => {
            options[key] = composite[key];
        });
    }
    function updateTracker() {
        tracker.forEach(widget => {
            const terminal = widget.content;
            Object.keys(options).forEach(key => {
                const k = key;
                terminal.setOption(k, options[k]);
            });
        });
    }
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
    themeManager?.themeChanged.connect(() => {
        tracker.forEach(widget => {
            if (widget.content.getOption('theme') === 'inherit') {
                widget.content.setOption('theme', 'inherit');
            }
        });
    });
    commands.addCommand(CommandIDs.createNew, {
        label: args => args['isPalette']
            ? trans.__('New Ghostty Terminal')
            : trans.__('Ghostty Terminal'),
        caption: trans.__('Start a new Ghostty terminal session'),
        icon: args => (args['isPalette'] ? undefined : ghosttyIcon),
        execute: async (args) => {
            const name = args['name'];
            const cwd = args['cwd'];
            const localPath = cwd
                ? serviceManager.contents.localPath(cwd)
                : undefined;
            let session;
            if (name) {
                const models = await _jupyterlab_services__WEBPACK_IMPORTED_MODULE_5__.TerminalAPI.listRunning(serviceManager.serverSettings);
                if (models.map(d => d.name).includes(name)) {
                    session = serviceManager.terminals.connectTo({ model: { name } });
                }
                else {
                    session = await serviceManager.terminals.startNew({
                        name,
                        cwd: localPath
                    });
                }
            }
            else {
                session = await serviceManager.terminals.startNew({ cwd: localPath });
            }
            const term = new _widget__WEBPACK_IMPORTED_MODULE_10__.GhosttyTerminal(session, options, translator);
            term.title.icon = ghosttyIcon;
            term.title.label = '...';
            const main = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.MainAreaWidget({ content: term, reveal: term.ready });
            app.shell.add(main, 'main', { type: 'Terminal' });
            void tracker.add(main);
            app.shell.activateById(main.id);
            return main;
        }
    });
    commands.addCommand(CommandIDs.open, {
        label: trans.__('Open Ghostty Terminal'),
        execute: async (args) => {
            const name = args['name'];
            if (!name) {
                return;
            }
            const existing = tracker.find(widget => widget.content.session.name === name);
            if (existing) {
                app.shell.activateById(existing.id);
                return existing;
            }
            return commands.execute(CommandIDs.createNew, { name });
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
            const displayName = args['displayName'];
            return args['isPalette']
                ? trans.__('Use Ghostty Theme: %1', displayName)
                : displayName;
        },
        isToggled: args => args['theme'] === options.theme,
        execute: async (args) => {
            const theme = args['theme'];
            await settingRegistry.set(plugin.id, 'theme', theme);
        }
    });
    if (palette) {
        [
            CommandIDs.createNew,
            CommandIDs.refresh,
            CommandIDs.increaseFont,
            CommandIDs.decreaseFont
        ].forEach(command => {
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
    if (launcher) {
        launcher.add({
            command: CommandIDs.createNew,
            category: trans.__('Other'),
            rank: 1
        });
    }
    if (mainMenu) {
        const themeMenu = new _lumino_widgets__WEBPACK_IMPORTED_MODULE_9__.Menu({ commands });
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
        mainMenu.settingsMenu.addGroup([
            { command: CommandIDs.increaseFont },
            { command: CommandIDs.decreaseFont },
            { type: 'submenu', submenu: themeMenu }
        ], 41);
        mainMenu.fileMenu.newMenu.addItem({
            command: CommandIDs.createNew,
            rank: 21
        });
    }
    if (runningSessionManagers) {
        const manager = serviceManager.terminals;
        class RunningGhosttyTerminal {
            constructor(_model) {
                this._model = _model;
            }
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
        // Creates a separate section from standard terminals in the running panel
        runningSessionManagers.add({
            name: trans.__('Ghostty Terminals'),
            supportsMultipleViews: false,
            running: () => Array.from(manager.running())
                .filter(model => {
                return (tracker.find(w => w.content.session.name === model.name) !==
                    undefined);
            })
                .map(model => new RunningGhosttyTerminal(model)),
            shutdownAll: () => {
                const promises = [];
                tracker.forEach(widget => {
                    promises.push(widget.content.session.shutdown());
                });
                return Promise.all(promises).then(() => { });
            },
            refreshRunning: () => manager.refreshRunning(),
            runningChanged: manager.runningChanged,
            shutdownLabel: trans.__('Shut Down'),
            shutdownAllLabel: trans.__('Shut Down All')
        });
    }
    console.log('JupyterLab extension jupyterlab-ghostty is activated!');
    return tracker;
}



/***/ }),

/***/ "./lib/tokens.js":
/*!***********************!*\
  !*** ./lib/tokens.js ***!
  \***********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   IGhosttyTerminal: () => (/* binding */ IGhosttyTerminal),
/* harmony export */   IGhosttyTerminalTracker: () => (/* binding */ IGhosttyTerminalTracker)
/* harmony export */ });
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/coreutils */ "webpack/sharing/consume/default/@lumino/coreutils");
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__);

const IGhosttyTerminalTracker = new _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__.Token('jupyterlab-ghostty:IGhosttyTerminalTracker', 'A widget tracker for Ghostty terminals.');
var IGhosttyTerminal;
(function (IGhosttyTerminal) {
    IGhosttyTerminal.defaultOptions = {
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
})(IGhosttyTerminal || (IGhosttyTerminal = {}));


/***/ }),

/***/ "./lib/widget.js":
/*!***********************!*\
  !*** ./lib/widget.js ***!
  \***********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   GhosttyTerminal: () => (/* binding */ GhosttyTerminal)
/* harmony export */ });
/* harmony import */ var _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/translation */ "webpack/sharing/consume/default/@jupyterlab/translation");
/* harmony import */ var _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_translation__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @lumino/coreutils */ "webpack/sharing/consume/default/@lumino/coreutils");
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_lumino_coreutils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _lumino_domutils__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @lumino/domutils */ "webpack/sharing/consume/default/@lumino/domutils");
/* harmony import */ var _lumino_domutils__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_lumino_domutils__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _lumino_messaging__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @lumino/messaging */ "webpack/sharing/consume/default/@lumino/messaging");
/* harmony import */ var _lumino_messaging__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_lumino_messaging__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @lumino/signaling */ "webpack/sharing/consume/default/@lumino/signaling");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _tokens__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./tokens */ "./lib/tokens.js");







const TERMINAL_CLASS = 'jp-GhosttyTerminal';
const TERMINAL_BODY_CLASS = 'jp-GhosttyTerminal-body';
class GhosttyTerminal extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_5__.Widget {
    constructor(session, options = {}, translator) {
        super();
        this._needsResize = true;
        this._offsetWidth = -1;
        this._offsetHeight = -1;
        this._isReady = false;
        this._ready = new _lumino_coreutils__WEBPACK_IMPORTED_MODULE_1__.PromiseDelegate();
        this._term = null;
        this._fitAddon = null;
        this._termOpened = false;
        this._themeChanged = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_4__.Signal(this);
        translator = translator || _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_0__.nullTranslator;
        this._trans = translator.load('jupyterlab');
        this.session = session;
        this._options = { ..._tokens__WEBPACK_IMPORTED_MODULE_6__.IGhosttyTerminal.defaultOptions, ...options };
        this.addClass(TERMINAL_CLASS);
        this._setThemeAttribute(this._options.theme);
        let buffer = '';
        const bufferMessage = (sender, msg) => {
            if (msg.type === 'stdout' && msg.content) {
                buffer += msg.content[0];
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
            }
            else {
                session.connectionStatusChanged.connect(this._initialConnection, this);
            }
            this.update();
        })
            .catch(reason => {
            console.error('Failed to create Ghostty terminal.\n', reason);
            this._ready.reject(reason);
        });
    }
    get ready() {
        return this._ready.promise;
    }
    getOption(option) {
        return this._options[option];
    }
    setOption(option, value) {
        if (option !== 'theme' && this._options[option] === value) {
            return;
        }
        this._options[option] = value;
        if (!this._term) {
            return;
        }
        switch (option) {
            case 'fontFamily':
                this._term.options.fontFamily = value;
                break;
            case 'fontSize':
                this._term.options.fontSize = value;
                break;
            case 'scrollback':
                this._term.options.scrollback = value;
                break;
            case 'theme':
                this._term.options.theme = Private.getTheme(value);
                this._setThemeAttribute(value);
                this._themeChanged.emit();
                break;
            default:
                break;
        }
        this._needsResize = true;
        this.update();
    }
    dispose() {
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
    async refresh() {
        if (!this.isDisposed && this._isReady) {
            await this.session.reconnect();
            this._term?.clear();
        }
    }
    hasSelection() {
        return this._isReady ? this._term?.hasSelection() ?? false : false;
    }
    paste(data) {
        if (this._isReady) {
            this._term?.paste(data);
        }
    }
    getSelection() {
        return this._isReady ? this._term?.getSelection() ?? null : null;
    }
    processMessage(msg) {
        super.processMessage(msg);
        if (msg.type === 'fit-request') {
            this.onFitRequest(msg);
        }
    }
    get themeChanged() {
        return this._themeChanged;
    }
    onAfterAttach(msg) {
        this.update();
    }
    onAfterShow(msg) {
        this.update();
    }
    onResize(msg) {
        this._offsetWidth = msg.width;
        this._offsetHeight = msg.height;
        this._needsResize = true;
        this.update();
    }
    onUpdateRequest(msg) {
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
    onFitRequest(msg) {
        _lumino_messaging__WEBPACK_IMPORTED_MODULE_3__.MessageLoop.sendMessage(this, _lumino_widgets__WEBPACK_IMPORTED_MODULE_5__.Widget.ResizeMessage.UnknownSize);
    }
    onActivateRequest(msg) {
        this._term?.focus();
    }
    _initialConnection() {
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
    _initializeTerm() {
        const term = this._term;
        term.onData((data) => {
            if (!this.isDisposed) {
                this.session.send({ type: 'stdin', content: [data] });
            }
        });
        term.onTitleChange((title) => {
            this.title.label = title;
        });
        // On non-Mac platforms, allow Ctrl+C to copy when text is selected
        if (!_lumino_domutils__WEBPACK_IMPORTED_MODULE_2__.Platform.IS_MAC) {
            term.attachCustomKeyEventHandler((event) => {
                if (event.ctrlKey && event.key === 'c' && term.hasSelection()) {
                    return false;
                }
                return true;
            });
        }
    }
    _onMessage(sender, msg) {
        switch (msg.type) {
            case 'stdout':
                if (msg.content) {
                    // Write directly - ghostty-web has a 60fps render loop with dirty tracking
                    this._term?.write(msg.content[0]);
                }
                break;
            case 'disconnect':
                this._term?.write('\r\n\r\n[Finished… Term Session]\r\n');
                break;
        }
    }
    _resizeTerminal() {
        if (!this._term || !this._fitAddon)
            return;
        // Use FitAddon for proper terminal sizing
        if (this._options.autoFit) {
            try {
                this._fitAddon.fit();
            }
            catch (err) {
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
    _setSessionSize() {
        if (!this._term || this.isDisposed)
            return;
        const content = [
            this._term.rows,
            this._term.cols,
            this._offsetHeight,
            this._offsetWidth
        ];
        this.session.send({ type: 'set_size', content });
    }
    _setThemeAttribute(theme) {
        if (this.isDisposed)
            return;
        this.node.setAttribute('data-term-theme', theme ? theme.toLowerCase() : 'inherit');
    }
}
var Private;
(function (Private) {
    Private.id = 0;
    let initialized = false;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let GhosttyTerminal_;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let GhosttyFitAddon_;
    Private.lightTheme = {
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
    Private.darkTheme = {
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
    function inheritTheme() {
        const bodyStyle = getComputedStyle(document.body);
        const bg = bodyStyle.getPropertyValue('--jp-layout-color0').trim();
        // Detect if dark theme by checking background luminance
        const isDark = bg && bg.toLowerCase() < '#808080';
        const baseTheme = isDark ? Private.darkTheme : Private.lightTheme;
        return {
            foreground: bodyStyle.getPropertyValue('--jp-ui-font-color0').trim() ||
                baseTheme.foreground,
            background: bg || baseTheme.background,
            cursor: bodyStyle.getPropertyValue('--jp-ui-font-color1').trim() ||
                baseTheme.cursor,
            cursorAccent: baseTheme.cursorAccent,
            selectionBackground: bodyStyle.getPropertyValue('--jp-editor-selected-background').trim() ||
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
    Private.inheritTheme = inheritTheme;
    function getTheme(theme) {
        switch (theme) {
            case 'light':
                return Private.lightTheme;
            case 'dark':
                return Private.darkTheme;
            case 'inherit':
            default:
                return inheritTheme();
        }
    }
    Private.getTheme = getTheme;
    async function createTerminal(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    options) {
        if (!initialized) {
            const ghostty = await __webpack_require__.e(/*! import() */ "webpack_sharing_consume_default_ghostty-web_ghostty-web").then(__webpack_require__.t.bind(__webpack_require__, /*! ghostty-web */ "webpack/sharing/consume/default/ghostty-web/ghostty-web", 23));
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
    Private.createTerminal = createTerminal;
})(Private || (Private = {}));


/***/ })

}]);
//# sourceMappingURL=lib_index_js.9b90d34f702d353d745e.js.map