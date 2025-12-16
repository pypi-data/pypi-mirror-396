import { JupyterFrontEndPlugin } from '@jupyterlab/application';
import { DocumentRegistry } from '@jupyterlab/docregistry';
import { INotebookModel, NotebookPanel } from '@jupyterlab/notebook';
import { DisposableDelegate } from '@lumino/disposable';
/** Wait until the kernel has loaded, then check if it is a MATLAB kernel. */
export declare const insertButton: (panel: NotebookPanel) => Promise<DisposableDelegate>;
export declare class MatlabToolbarButtonExtension implements DocumentRegistry.IWidgetExtension<NotebookPanel, INotebookModel> {
    createNew(panel: NotebookPanel, context: DocumentRegistry.IContext<INotebookModel>): DisposableDelegate;
}
export declare const matlabToolbarButtonPlugin: JupyterFrontEndPlugin<void>;
