export declare class ThemeMode {
    static registerThemeChangeCallback(callback: Function): void;
    static unregisterThemeChangeCallback(callback: Function): void;
    static toggleDarkMode(): void;
    static isDefaultDarkMode(): boolean;
    static isDarkMode(): boolean;
    static setDefaultDarkMode(): void;
    static setDarkMode(mode: boolean, save?: boolean): void;
    static getThemeMode(): 'light' | 'dark' | 'auto';
    static clear(): void;
}
export declare function inPlacePopByValue(arr: Array<any>, toPop: any): void;
export declare function isChildDOMElement(child: HTMLElement, parent: HTMLElement): boolean;
export declare function deepCopy(obj: any): any;
export declare function sortByScore<T>(arr: T[], scores: number[], reverse?: boolean): [T[], number[]];
