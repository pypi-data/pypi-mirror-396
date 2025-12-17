declare class Fetcher {
    _baseUrlGetter: () => string;
    _tokenGetter: () => string;
    _sessionIDGetter: () => string;
    constructor({ baseUrlGetter, tokenGetter, sessionIDGetter }: {
        baseUrlGetter?: () => string;
        tokenGetter?: () => string;
        sessionIDGetter?: () => string;
    });
    get baseUrl(): string;
    get token(): string;
    get sessionID(): string;
    get(path: string, params?: Record<string, string>): Promise<Response>;
    post(path: string, body?: Record<string, any>): Promise<Response>;
    put(path: string, file: File): Promise<Response>;
    delete(path: string, body?: Record<string, any>): Promise<Response>;
    private _fetch;
}
export default Fetcher;
