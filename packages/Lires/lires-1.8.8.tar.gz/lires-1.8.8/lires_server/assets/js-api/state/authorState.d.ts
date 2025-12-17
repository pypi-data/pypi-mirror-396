import { type Ref } from 'vue';
/**
 * @param authorNames The names of the authors to get papers for
 * @returns A reactive object containing the paper ids for each author,
 * and a function to update the paper ids
 */
export declare function useAuthorPapers(authorNames: Ref<string[]>): {
    authorPapers: Ref<Record<string, string[]>>;
    updateAuthorPapers: () => void;
};
