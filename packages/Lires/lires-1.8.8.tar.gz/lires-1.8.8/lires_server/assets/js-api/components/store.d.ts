import { DataBase } from '../core/dataClass';
import { UserPool } from '../core/user';
import { DataTags } from '../core/tag';
import { ServerConn } from '../api/serverConn';
import { ServerWebsocketConn } from '../api/serverWebsocketConn';
import { formatAuthorName } from '../utils/misc';
export { formatAuthorName };
import type { SearchStatus, PopupStyle, TagStatus } from './interface';
import type { UserInfo } from '../api/protocol';
interface PopupValue {
    content: string;
    styleType: PopupStyle;
}
export declare const useUIStateStore: import("pinia").StoreDefinition<"uiStatus", {
    tagStatus: TagStatus;
    shownDataUIDs: string[];
    shownDataScores: number[];
    searchState: SearchStatus;
    unfoldedDataUIDs: string[];
    recentlyReadDataUIDs: string[];
    preferredReaderLeftPanelWidthPerc: number;
    showMiscPanel: boolean;
    showNotePreview: boolean;
    popupValues: Record<string, PopupValue>;
    databaseLoadingStatus: {
        nCurrent: number;
        nTotal: number;
    };
    dataEditorOpened: boolean;
}, {
    databaseLoadingProgress(): number;
    focusedDataUID(): string | null;
}, {
    updateShownData(): void;
    addRecentlyReadDataUID(uid: string): void;
    showPopup(content: string, style?: PopupStyle, time?: number): void;
    reloadDatabase(): void;
}>;
export declare const useConnectionStore: import("pinia").StoreDefinition<"connection", {
    conn: ServerConn;
    wsConn: ServerWebsocketConn;
}, {}, {}>;
export declare const useDataStore: import("pinia").StoreDefinition<"data", {
    database: DataBase;
    userPool: UserPool;
    user: UserInfo;
}, {
    allTags(): DataTags;
}, {
    clearUserInfo(): void;
    reload(onStart?: () => void, onSuccess?: () => void, onError?: (err: Error) => void): void;
}>;
export declare const useSettingsStore: import("pinia").StoreDefinition<"settings", {
    __encKey: string;
    __showTagPanel: boolean;
    __showHomeInfoPanel: boolean;
    __show3DScatterPlot: boolean;
    __readerLayoutType: string;
    __numItemsPerPage: string;
    __backendHost: string;
    __backendPort: string;
    loggedIn: boolean;
}, {
    encKey(): string;
    backendHost(): string;
    backendPort(): string;
    showTagPanel(): boolean;
    showHomeInfoPanel(): boolean;
    show3DScatterPlot(): boolean;
    readerLayoutType(): number;
    numItemsPerPage(): number;
}, {
    setEncKey(key: string, keep?: boolean | undefined): void;
    setBackendHost(url: string): void;
    setBackendPort(port: string): void;
    setShowTagPanel(show: boolean): void;
    setShowHomeInfoPanel(show: boolean): void;
    setShow3DScatterPlot(show: boolean): void;
    setReaderLayoutType(type: number): void;
    setNumItemsPerPage(num: number): void;
    backend(): string;
}>;
