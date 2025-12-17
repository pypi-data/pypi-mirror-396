import type { UserInfo } from "../api/protocol";
export declare function saveAuthentication(encKey: string, userInfo: UserInfo | null, stayLogin: boolean): void;
export declare function checkSettingsLogout(): boolean;
export declare function settingsLogout(): void;
export declare function settingsAuthentication(): Promise<UserInfo | null>;
export declare function getEncKey(username: string, password: string): string;
