import type { DataInfoT } from "../api/protocol";
import type { ServerConn } from "../api/serverConn";
import { DataTags } from "./tag";
export declare class DataPoint {
    summary: DataInfoT;
    supp: Record<'note' | 'abstract', string | null>;
    conn: ServerConn;
    constructor(conn: ServerConn, summary: DataInfoT);
    get backendUrl(): string;
    get dtype(): string;
    get tags(): DataTags;
    get uid(): string;
    get title(): string;
    get authors(): string[];
    get year(): string;
    get publication(): string | null;
    get url(): string | null;
    get bibtex(): string;
    toString(): string;
    fetchAbstract(): Promise<string>;
    uploadAbstract(abstract: string): Promise<boolean>;
    fetchNote(): Promise<string>;
    uploadNote(note: string): Promise<boolean>;
    deleteMiscFile(fname: string): Promise<boolean>;
    renameMiscFile(fname: string, newname: string): Promise<boolean>;
    listMiscFiles(): Promise<Record<'fname' | 'rpath' | 'url', string>[]>;
    uploadMisc(files: File[]): Promise<string[]>;
    uploadDocument(doc: File): Promise<DataInfoT>;
    freeDocument(): Promise<DataInfoT>;
    update(summary?: null | DataInfoT): Promise<DataInfoT>;
    destory(): void;
    authorAbbr(): string;
    authorYear(): string;
    yearAuthor(hyphen?: string): string;
    isDummy(): boolean;
    getRawDocURL(): string;
    /**
     * will wrap the url with backend pdfjs viewer if the url is a pdf
     */
    getOpenDocURL({ extraPDFViewerParams, urlHashMark, }?: {
        extraPDFViewerParams?: Record<string, string>;
        urlHashMark?: string;
    }): string;
    fileType(): "" | "html" | "pdf" | "url" | "unknown";
}
export declare class DataBase {
    private cache;
    private tags;
    private uids;
    private dataInfoAcquireMutex;
    conn: ServerConn;
    _initliazed: boolean;
    constructor(conn: ServerConn);
    get initialized(): boolean;
    init(): Promise<void>;
    allTags(): DataTags;
    allKeys(): string[];
    updateKeyCache(): Promise<void>;
    updateTagCache(): Promise<void>;
    update(summary: DataInfoT, syncTags?: boolean): Promise<DataPoint>;
    clear(): void;
    delete(uuid: string, syncTags?: boolean): Promise<void>;
    hasCache(uuid: string): boolean;
    getDummy(): DataPoint;
    aget(uid: string): Promise<DataPoint>;
    agetMany(uuids: string[], strict_exist?: boolean, fallback?: boolean): Promise<DataPoint[]>;
    agetByAuthor(author: string): Promise<DataPoint[]>;
    getCacheByTags(tags: string[] | DataTags): DataPoint[];
}
