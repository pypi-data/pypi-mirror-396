export declare const FileSelectButton: import("vue").DefineComponent<import("vue").ExtractPropTypes<{
    asLink: {
        type: BooleanConstructor;
        default: boolean;
    };
    text: {
        type: StringConstructor;
        default: string;
    };
    action: {
        type: FunctionConstructor;
        required: true;
    };
    style: {
        type: ObjectConstructor;
        default: () => {};
    };
}>, () => any, {}, {}, {}, import("vue").ComponentOptionsMixin, import("vue").ComponentOptionsMixin, {}, string, import("vue").PublicProps, Readonly<import("vue").ExtractPropTypes<{
    asLink: {
        type: BooleanConstructor;
        default: boolean;
    };
    text: {
        type: StringConstructor;
        default: string;
    };
    action: {
        type: FunctionConstructor;
        required: true;
    };
    style: {
        type: ObjectConstructor;
        default: () => {};
    };
}>> & Readonly<{}>, {
    text: string;
    style: Record<string, any>;
    asLink: boolean;
}, {}, {}, {}, string, import("vue").ComponentProvideOptions, true, {}, any>;
export declare const TextInputWindow: import("vue").DefineComponent<import("vue").ExtractPropTypes<{
    action: {
        type: FunctionConstructor;
        required: true;
    };
    show: {
        type: BooleanConstructor;
        required: true;
    };
    title: {
        type: StringConstructor;
        default: string;
    };
    text: {
        type: StringConstructor;
        default: string;
    };
    placeholder: {
        type: StringConstructor;
        default: string;
    };
    buttonText: {
        type: StringConstructor;
        default: string;
    };
}>, () => any, {}, {}, {}, import("vue").ComponentOptionsMixin, import("vue").ComponentOptionsMixin, {}, "update:show", import("vue").PublicProps, Readonly<import("vue").ExtractPropTypes<{
    action: {
        type: FunctionConstructor;
        required: true;
    };
    show: {
        type: BooleanConstructor;
        required: true;
    };
    title: {
        type: StringConstructor;
        default: string;
    };
    text: {
        type: StringConstructor;
        default: string;
    };
    placeholder: {
        type: StringConstructor;
        default: string;
    };
    buttonText: {
        type: StringConstructor;
        default: string;
    };
}>> & Readonly<{}>, {
    title: string;
    text: string;
    placeholder: string;
    buttonText: string;
}, {}, {}, {}, string, import("vue").ComponentProvideOptions, true, {}, any>;
export declare const EditableParagraph: import("vue").DefineComponent<import("vue").ExtractPropTypes<{
    contentEditable: {
        type: BooleanConstructor;
        default: boolean;
    };
    style: {
        type: ObjectConstructor;
        default: () => {};
    };
}>, () => any, {}, {}, {}, import("vue").ComponentOptionsMixin, import("vue").ComponentOptionsMixin, {}, "change" | "finish", import("vue").PublicProps, Readonly<import("vue").ExtractPropTypes<{
    contentEditable: {
        type: BooleanConstructor;
        default: boolean;
    };
    style: {
        type: ObjectConstructor;
        default: () => {};
    };
}>> & Readonly<{}>, {
    style: Record<string, any>;
    contentEditable: boolean;
}, {}, {}, {}, string, import("vue").ComponentProvideOptions, true, {}, any>;
export declare const MenuAttached: import("vue").DefineComponent<import("vue").ExtractPropTypes<{
    menuItems: {
        type: ArrayConstructor;
        required: true;
    };
}>, () => any, {}, {}, {}, import("vue").ComponentOptionsMixin, import("vue").ComponentOptionsMixin, {}, string, import("vue").PublicProps, Readonly<import("vue").ExtractPropTypes<{
    menuItems: {
        type: ArrayConstructor;
        required: true;
    };
}>> & Readonly<{}>, {}, {}, {}, {}, string, import("vue").ComponentProvideOptions, true, {}, any>;
export declare const CircularImage: import("vue").DefineComponent<import("vue").ExtractPropTypes<{
    href: {
        type: StringConstructor;
        required: true;
    };
    size: {
        type: StringConstructor;
        required: true;
    };
    alt: {
        type: StringConstructor;
        default: string;
    };
}>, () => any, {}, {}, {}, import("vue").ComponentOptionsMixin, import("vue").ComponentOptionsMixin, {}, "click", import("vue").PublicProps, Readonly<import("vue").ExtractPropTypes<{
    href: {
        type: StringConstructor;
        required: true;
    };
    size: {
        type: StringConstructor;
        required: true;
    };
    alt: {
        type: StringConstructor;
        default: string;
    };
}>> & Readonly<{}>, {
    alt: string;
}, {}, {}, {}, string, import("vue").ComponentProvideOptions, true, {}, any>;
