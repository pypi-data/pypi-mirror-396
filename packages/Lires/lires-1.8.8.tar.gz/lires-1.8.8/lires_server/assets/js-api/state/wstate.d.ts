import { type Ref } from 'vue';
export declare function useWindowState(): {
    width: Ref<number>;
    height: Ref<number>;
    cleanup: () => void;
};
