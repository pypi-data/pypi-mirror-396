import type { DataPoint } from "./dataClass";
import type { Router } from "vue-router";
export interface FrontMatterData {
    links?: Record<string, string>;
}
export declare function parseMarkdown(content: string, { router, datapoint, }: {
    router?: Router;
    datapoint?: DataPoint;
}): string;
