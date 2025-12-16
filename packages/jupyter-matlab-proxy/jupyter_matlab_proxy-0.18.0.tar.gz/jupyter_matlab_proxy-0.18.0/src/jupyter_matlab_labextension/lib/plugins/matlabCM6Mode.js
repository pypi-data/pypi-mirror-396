// Copyright 2023-2025 The MathWorks, Inc.
import { IEditorLanguageRegistry } from '@jupyterlab/codemirror';
/** Register language with CodeMirror */
export function addMATLABCodeMirror(languageRegistry) {
    languageRegistry.addLanguage({
        name: 'matlab',
        displayName: 'MATLAB',
        mime: 'text/x-matlab',
        extensions: ['m', 'mlx'],
        filename: /^[a-zA-Z][a-zA-Z0-9_]*\.m$/,
        async load() {
            const m = await import('../codemirror-lang-matlab/codemirror-lang-matlab');
            return m.matlab();
        }
    });
}
export const matlabCodeMirror6Plugin = {
    id: '@mathworks/matlabCodeMirror6Plugin',
    autoStart: true,
    requires: [IEditorLanguageRegistry],
    activate: (app, codeMirror) => {
        addMATLABCodeMirror(codeMirror);
    }
};
export default matlabCodeMirror6Plugin;
