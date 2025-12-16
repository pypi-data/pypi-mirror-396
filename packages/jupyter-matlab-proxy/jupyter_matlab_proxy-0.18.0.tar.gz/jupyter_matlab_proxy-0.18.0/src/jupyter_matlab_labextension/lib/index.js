// Copyright 2023-2025 The MathWorks, Inc.
import { matlabToolbarButtonPlugin } from './plugins/matlabToolbarButton';
import { matlabMFilesPlugin } from './plugins/matlabFiles';
import { matlabCodeMirror6Plugin } from './plugins/matlabCM6Mode';
import { matlabCommPlugin } from './plugins/matlabCommunication';
const plugins = [
    matlabToolbarButtonPlugin,
    matlabMFilesPlugin,
    matlabCodeMirror6Plugin,
    matlabCommPlugin
];
export default plugins;
