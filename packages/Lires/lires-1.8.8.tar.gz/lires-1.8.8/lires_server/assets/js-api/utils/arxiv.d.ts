export interface ArxivArticle {
    id: string;
    link: string;
    title: string;
    abstract: string;
    authors: string[];
    updatedTime: string;
    publishedTime: string;
}
export declare function fetchArxivFeed(maxResults?: number, searchQuery?: string, sortBy?: string, sortOrder?: string): Promise<ArxivArticle[]>;
export declare function fetchArxivPaperByID(id: string): Promise<ArxivArticle>;
export declare function bibtexFromArxiv(paper: ArxivArticle): string;
