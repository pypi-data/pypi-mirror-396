import type { Router } from "vue-router";
export declare class URLRouter {
    router: Router;
    constructor(router: Router);
    getURLParams(): Record<string, string>;
    setURLParam(k: string, v: string): void;
    updateURLWithParam(k: string, v: string): string;
}
