import type { ServerConn } from '../api/serverConn';
import type { UserInfo } from '../api/protocol';
export declare class User {
    conn: ServerConn;
    info: UserInfo;
    constructor(conn: ServerConn, info: UserInfo);
    get baseURL(): string;
    avatarURL(size?: number, t?: number | null): string;
}
export declare class UserPool {
    conn: ServerConn;
    constructor(conn: ServerConn);
    list(): Promise<User[]>;
    get(username: string): Promise<User>;
}
