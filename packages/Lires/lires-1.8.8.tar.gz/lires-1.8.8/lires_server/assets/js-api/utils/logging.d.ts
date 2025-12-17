type logLevel_t = "debug" | "info" | "warn" | "error";
interface Logger_t {
    DEFAULT_LOGLEVEL: logLevel_t;
    LOGLEVEL_ORDER: logLevel_t[];
    name: string;
    info(s: string): void;
    warn(s: string): void;
    debug(s: string): void;
    error(s: string): void;
}
declare abstract class LoggerAbstract implements Logger_t {
    readonly DEFAULT_LOGLEVEL: logLevel_t;
    readonly LOGLEVEL_ORDER: logLevel_t[];
    name: string;
    constructor(name: string);
    info(s: string): void;
    warn(s: string): void;
    debug(s: string): void;
    error(s: string): void;
    protected formatString(s: string, level: logLevel_t): string;
    protected get timeString(): string;
    protected abstract log(s: string, level: logLevel_t): void;
    protected abstract get dstLevel(): logLevel_t;
}
export declare class Logger extends LoggerAbstract {
    protected log(s: string, level: logLevel_t): void;
    protected get dstLevel(): logLevel_t;
}
export declare function getLogger(name: string): Logger_t;
export {};
