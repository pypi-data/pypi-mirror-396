interface ExtractFileTypes {
    citation: File[];
    document: File[];
    unknown: File[];
}
export declare function classifyFiles(files: FileList | File[]): ExtractFileTypes;
export {};
