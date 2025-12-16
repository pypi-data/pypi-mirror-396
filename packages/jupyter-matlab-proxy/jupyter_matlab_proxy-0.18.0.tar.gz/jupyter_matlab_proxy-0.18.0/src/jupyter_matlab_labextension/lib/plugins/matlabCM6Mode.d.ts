import { JupyterFrontEndPlugin } from '@jupyterlab/application';
import { IEditorLanguageRegistry } from '@jupyterlab/codemirror';
/** Register language with CodeMirror */
export declare function addMATLABCodeMirror(languageRegistry: IEditorLanguageRegistry): void;
export declare const matlabCodeMirror6Plugin: JupyterFrontEndPlugin<void>;
export default matlabCodeMirror6Plugin;
