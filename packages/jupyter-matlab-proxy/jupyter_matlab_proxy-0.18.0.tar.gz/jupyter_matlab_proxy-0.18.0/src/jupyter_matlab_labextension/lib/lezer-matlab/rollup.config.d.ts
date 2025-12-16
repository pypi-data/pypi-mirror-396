declare namespace _default {
    export { entryModule as input };
    export const output: {
        format: string;
        file: string;
    }[];
    export function external(id: any): boolean;
    export const plugins: import("rollup").Plugin<any>[];
}
export default _default;
declare const entryModule: "./src/parser.js";
