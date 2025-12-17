declare function setCookie(key: string, value: string, expDays?: number | null): void;
declare function isCookieKept(key: string): boolean;
declare function getCookie(key: string): string;
export { setCookie, getCookie, isCookieKept };
