export interface TagHierarchy extends Record<string, TagHierarchy> {
}
export declare const TAG_SEP = "->";
export declare class DataTags extends Set<string> {
    static removeSpaces(tag: string): string;
    constructor(tags?: string[] | DataTags | Set<string> | null);
    copy(): DataTags;
    equals(tags: DataTags): boolean;
    add(tag: string): this;
    has(tag: string): boolean;
    union(tags: DataTags): DataTags;
    union_(tags: DataTags): this;
    pop(tags: DataTags): DataTags;
    pop_(tags: DataTags): this;
    pop_ifcontains_(tags: DataTags): this;
    issubset(tags: DataTags): boolean;
    withParents(): DataTags;
    withChildsFrom(tagPool: DataTags): DataTags;
    allParents(): DataTags;
    toArray(): string[];
}
export declare class TagRule {
    static allParentsOf(tag: string): DataTags;
    static allChildsOf(tag: string, tag_pool: DataTags): DataTags;
    static tagHierarchy(tags: DataTags): TagHierarchy;
    static isSubset(query: DataTags, value: DataTags): boolean;
}
