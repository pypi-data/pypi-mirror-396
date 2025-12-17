export declare function resolveAbsoluteURL(url: string): string;
export declare function formatAuthorName(author: string): string;
export declare function isVisiable(el: HTMLElement): boolean;
export declare function copyToClipboard(textToCopy: string): Promise<boolean>;
export declare function openURLExternal(url: string): void;
export declare function lazify(func: Function, delay: number): (...args: any[]) => void;
/** Extract page, number and volume from bibtex
 * @param bibtex - bibtex string
 * @returns - formatted volume, number, and pages
 */
export declare function volInfoFromBibtex(bibtex: string): string;
