import { NotebookPanel } from '@jupyterlab/notebook';
/**
 * Tracks metadata and kernel state for the currently active Jupyter notebook panel.
 * Provides helpers to determine whether the notebook is a MATLAB notebook, whether
 * its kernel is busy, resolve the notebook's file path, and control the kernel.
 */
export declare class NotebookInfo {
    private _notebookName;
    private _isMatlabNotebook;
    private _isBusy;
    private _panel;
    isMatlabNotebook(): boolean;
    isBusy(): boolean;
    getCurrentFilePath(): string | undefined;
    waitForIdleStatus(): Promise<void>;
    update(panel: NotebookPanel | null): Promise<void>;
    interrupt(): void;
    getCurrentFilename(): string | undefined;
}
