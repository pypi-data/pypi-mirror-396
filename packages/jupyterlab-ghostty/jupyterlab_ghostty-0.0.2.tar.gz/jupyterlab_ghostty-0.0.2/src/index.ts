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

const ghosttyIconSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
  <rect x="2" y="4" width="20" height="16" rx="2" fill="none" stroke="currentColor" stroke-width="2"/>
  <text x="6" y="16" font-family="monospace" font-size="10" fill="currentColor">&gt;_</text>
</svg>`;

const ghosttyIcon = new LabIcon({
  name: 'jupyterlab-ghostty:icon',
  svgstr: ghosttyIconSvg
});

namespace CommandIDs {
  export const createNew = 'ghostty-terminal:create-new';
  export const open = 'ghostty-terminal:open';
  export const refresh = 'ghostty-terminal:refresh';
  export const increaseFont = 'ghostty-terminal:increase-font';
  export const decreaseFont = 'ghostty-terminal:decrease-font';
  export const setTheme = 'ghostty-terminal:set-theme';
  export const shutdown = 'ghostty-terminal:shutdown';
}

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

  const tracker = new WidgetTracker<
    MainAreaWidget<IGhosttyTerminal.ITerminal>
  >({
    namespace
  });

  if (!serviceManager.terminals.isAvailable()) {
    console.warn(
      'Ghostty terminal disabled: terminals not available on server'
    );
    return tracker;
  }

  if (restorer) {
    void restorer.restore(tracker, {
      command: CommandIDs.createNew,
      args: widget => ({ name: widget.content.session.name }),
      name: widget => `ghostty-${widget.content.session.name}`
    });
  }

  const options: Partial<IGhosttyTerminal.IOptions> = {};

  function updateOptions(settings: ISettingRegistry.ISettings): void {
    const composite = settings.composite as Record<string, unknown>;
    Object.keys(composite).forEach(key => {
      (options as Record<string, unknown>)[key] = composite[key];
    });
  }

  function updateTracker(): void {
    tracker.forEach(widget => {
      const terminal = widget.content;
      Object.keys(options).forEach(key => {
        const k = key as keyof IGhosttyTerminal.IOptions;
        terminal.setOption(k, options[k] as IGhosttyTerminal.IOptions[typeof k]);
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

  commands.addCommand(CommandIDs.open, {
    label: trans.__('Open Ghostty Terminal'),
    execute: async args => {
      const name = args['name'] as string;
      if (!name) {
        return;
      }

      const existing = tracker.find(
        widget => widget.content.session.name === name
      );
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

    // Creates a separate section from standard terminals in the running panel
    runningSessionManagers.add({
      name: trans.__('Ghostty Terminals'),
      supportsMultipleViews: false,
      running: () =>
        Array.from(manager.running())
          .filter(model => {
            return (
              tracker.find(w => w.content.session.name === model.name) !==
              undefined
            );
          })
          .map(model => new RunningGhosttyTerminal(model)),
      shutdownAll: () => {
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

  console.log('JupyterLab extension jupyterlab-ghostty is activated!');

  return tracker;
}

export * from './tokens';
