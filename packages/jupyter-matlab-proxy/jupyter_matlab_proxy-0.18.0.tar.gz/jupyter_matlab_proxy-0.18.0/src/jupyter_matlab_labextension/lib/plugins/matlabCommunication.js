// Copyright 2025 The MathWorks, Inc.
import { INotebookTracker } from '@jupyterlab/notebook';
import { Token } from '@lumino/coreutils';
import { DisposableDelegate } from '@lumino/disposable';
import { NotebookInfo } from '../utils/notebook';
export class MatlabCommunicationExtension {
    constructor() {
        this._comms = new Map();
    }
    /*
     * Attempts to open a comm channel with a retry mechanism.
     * @param kernel The kernel for which a comm channel is being created.

     * @returns A promise that resolves when the comm is open.
    */
    async _createAndOpenCommWithRetry(kernel, channelName) {
        let attempt = 1;
        let delayInMS = 200;
        const maxRetries = 5;
        while (attempt <= maxRetries) {
            try {
                // Creates comm object on the client side
                const comm = kernel.createComm(channelName);
                // Attempts to open a channel with the kernel
                await comm.open().done;
                console.log('Communication channel opened successfully with ID:', comm.commId);
                return comm;
            }
            catch (error) {
                console.error('Error opening communication channel', error);
                console.error(`Attempt #${attempt} failed. Waiting ${delayInMS}ms before next attempt.`);
            }
            // Wait for the delay
            await new Promise(resolve => setTimeout(resolve, delayInMS));
            // Update
            delayInMS *= 2;
            attempt += 1;
        }
        console.error(`Failed to create communication channel after ${attempt} attempts.`);
        return null;
    }
    createNew(panel, context) {
        panel.sessionContext.ready
            .then(async () => {
            var _a;
            const kernel = (_a = panel.sessionContext.session) === null || _a === void 0 ? void 0 : _a.kernel;
            // If kernel is available, create channel and set up listeners.
            if (!kernel) {
                console.error("Kernel not ready! Can't create communication channel");
                return new DisposableDelegate(() => { });
            }
            const notebookInfo = new NotebookInfo();
            await notebookInfo.update(panel);
            if (!notebookInfo.isMatlabNotebook()) {
                console.debug('Not a MATLAB notebook, skipping communication setup');
                return new DisposableDelegate(() => { });
            }
            console.log('MATLAB Communication plugin activated for ', panel.id);
            // Create a unique channel name for this notebook
            const channelName = 'matlab_comm_' + panel.id;
            console.log('Attempting to establish communication with the kernel');
            const comm = await this._createAndOpenCommWithRetry(kernel, channelName);
            if (!comm) {
                return new DisposableDelegate(() => { });
            }
            // Listen for messages from the kernel
            comm.onMsg = (msg) => {
                const data = msg.content.data;
                console.debug('Recieved data from kernel: ', data);
            };
            // Handle comm close
            comm.onClose = (msg) => {
                console.debug(`Received data:${msg} for comm close event.`);
                console.log(`Comm with ID:${comm.commId} closed.`);
            };
            this._comms.set(panel.id, comm);
        })
            .catch((error) => {
            console.error('Notebook panel was not ready', error);
        });
        return new DisposableDelegate(() => {
            const comm = this._comms.get(panel.id);
            if (comm && !comm.isDisposed) {
                comm.close();
                this._comms.delete(panel.id);
            }
        });
    }
    getComm(notebookId) {
        const commChannel = this._comms.get(notebookId);
        if (!commChannel) {
            throw new Error(`No communication channel found for notebook ID: ${notebookId}`);
        }
        return commChannel;
    }
    deleteComms() {
        this._comms.clear();
    }
}
// A unique token for the comm service
export const IMatlabCommunication = new Token('@mathworks/matlab-comm:IMatlabCommunication');
export const matlabCommPlugin = {
    id: '@mathworks/matlabCommPlugin',
    autoStart: true,
    requires: [INotebookTracker],
    provides: IMatlabCommunication,
    activate: (app) => {
        const matlabCommExtension = new MatlabCommunicationExtension();
        app.docRegistry.addWidgetExtension('Notebook', matlabCommExtension);
        // Dispose resources created by this plugin when the page unloads.
        // Need to handle this separately for the case when jupyterlab tab is closed directly
        window.addEventListener('beforeunload', () => {
            matlabCommExtension.deleteComms();
        });
        return matlabCommExtension;
    }
};
