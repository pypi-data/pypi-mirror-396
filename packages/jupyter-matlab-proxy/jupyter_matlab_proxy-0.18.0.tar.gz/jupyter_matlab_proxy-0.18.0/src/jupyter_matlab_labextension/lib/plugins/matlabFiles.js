// Copyright 2023-2025 The MathWorks, Inc.
import { ICommandPalette } from '@jupyterlab/apputils';
import { ILauncher } from '@jupyterlab/launcher';
import { newMFileIcon, matlabIcon } from '../icons';
const FACTORY = 'Editor';
const PALETTE_CATEGORY = 'Other';
const command = 'matlab:new-matlab-file';
function registerMFiles(app, launcher, palette) {
    const { commands } = app;
    const createNewMatlabFile = async (args) => {
        /** Get the directory in which the MATLAB file must be created;
         * otherwise take the current filebrowser directory. */
        const cwd = args.cwd;
        /** Create a new untitled MATLAB file. */
        const model = await commands.execute('docmanager:new-untitled', {
            path: cwd,
            type: 'file',
            ext: '.m'
        });
        /** Open the newly created file with the 'Editor'. */
        return commands.execute('docmanager:open', {
            path: model.path,
            factory: FACTORY
        });
    };
    /** Create a new MATLAB file by adding a command to the JupyterFrontEnd. */
    commands.addCommand(command, {
        label: (args) => (args.isPalette ? 'New MATLAB File' : 'MATLAB File'),
        caption: 'Create a new MATLAB file',
        icon: (args) => (args.isPalette ? undefined : newMFileIcon),
        execute: createNewMatlabFile
    });
    /** Add the command to the launcher. */
    if (launcher) {
        launcher.add({
            command,
            category: 'Other',
            rank: 1
        });
    }
    /** Add the command to the palette. */
    if (palette) {
        palette.addItem({
            command,
            args: { isPalette: true },
            category: PALETTE_CATEGORY
        });
    }
    /** Associate file type with icon. */
    app.docRegistry.addFileType({
        name: 'MATLAB',
        displayName: 'MATLAB File',
        extensions: ['.m'],
        mimeTypes: ['text/x-matlab', 'matlab'],
        icon: matlabIcon
    });
}
export const matlabMFilesPlugin = {
    id: '@mathworks/matlabMFilesPlugin',
    autoStart: true,
    optional: [ILauncher, ICommandPalette],
    activate: (app, launcher, palette) => {
        registerMFiles(app, launcher, palette);
    }
};
