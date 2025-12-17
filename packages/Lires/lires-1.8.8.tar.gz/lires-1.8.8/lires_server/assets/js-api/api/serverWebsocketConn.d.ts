import type { Event } from "./protocol";
declare global {
    interface Window {
        g_eventHooks: Record<string, ((arg: Event) => void)[]>;
    }
}
export declare function registerServerEvenCallback(eventType: Event['type'] | Event['type'][], eventReactFn: (arg: Event) => void): void;
export declare function unregisterServerEvenCallback(eventType: Event['type'] | Event['type'][], eventReactFn: (arg: Event) => void): void;
export declare function registerServerEvenCallback_auto(eventType: Event['type'] | Event['type'][], eventReactFn: (arg: Event) => void): void;
export declare class ServerWebsocketConn {
    ws: WebSocket;
    sessionID: string;
    __baseUrlGetter: () => string;
    __tokenGetter: () => string;
    __remainingRetries: number;
    __eventCallback_records: {
        onopenCallback: () => void;
        onmessageCallback: (arg: MessageEvent) => void;
        oncloseCallback: () => void;
        onfailedToConnectCallback: () => void;
    };
    constructor(baseUrlGetter: () => string, tokenGetter: () => string);
    private resetRemainingRetries;
    private decreaseRemainingRetries;
    isOpen: () => boolean;
    willTryReconnect: () => boolean;
    connect({ onopenCallback, onmessageCallback, oncloseCallback, onfailedToConnectCallback }?: {
        onopenCallback?: () => void;
        onmessageCallback?: (_: MessageEvent) => void;
        oncloseCallback?: () => void;
        onfailedToConnectCallback?: () => void;
    }): ServerWebsocketConn;
    send(data: any): void;
    resetReconnect(): void;
    close(): void;
}
