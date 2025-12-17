interface InputBlock {
    type: "markdown";
    content: string;
    authors: string[];
    references: ReferenceItem[];
}
interface ReferenceItem {
    type: "uid";
    content: string;
}
