import { JupyterFrontEndPlugin } from '@jupyterlab/application';
import { DocumentRegistry } from '@jupyterlab/docregistry';
import { INotebookModel, NotebookPanel } from '@jupyterlab/notebook';
import { KernelMessage } from '@jupyterlab/services';
import { JSONObject, JSONValue, Token } from '@lumino/coreutils';
import { DisposableDelegate } from '@lumino/disposable';
type CommunicationData = {
    action: string;
    data: JSONValue;
};
export interface ICommunicationChannel {
    readonly commId: string;
    readonly targetName: string;
    readonly isDisposed: boolean;
    onMsg: (msg: KernelMessage.ICommMsgMsg) => void | PromiseLike<void>;
    onClose: (msg: KernelMessage.ICommCloseMsg) => void | PromiseLike<void>;
    close: (data?: JSONValue, metadata?: JSONObject, buffers?: (ArrayBuffer | ArrayBufferView)[]) => void;
    send: (data: CommunicationData, metadata?: JSONObject, buffers?: (ArrayBuffer | ArrayBufferView)[], disposeOnDone?: boolean) => void;
}
export interface ICommunicationService {
    getComm(notebookID: string): ICommunicationChannel;
}
export declare class MatlabCommunicationExtension implements DocumentRegistry.IWidgetExtension<NotebookPanel, INotebookModel>, ICommunicationService {
    private _comms;
    private _createAndOpenCommWithRetry;
    createNew(panel: NotebookPanel, context: DocumentRegistry.IContext<INotebookModel>): DisposableDelegate;
    getComm(notebookId: string): ICommunicationChannel;
    deleteComms(): void;
}
export declare const IMatlabCommunication: Token<ICommunicationService>;
export declare const matlabCommPlugin: JupyterFrontEndPlugin<MatlabCommunicationExtension>;
export {};
