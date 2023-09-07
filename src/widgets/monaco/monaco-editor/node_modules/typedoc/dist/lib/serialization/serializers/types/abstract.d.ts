import { Type } from "../../../models";
import { TypeSerializerComponent } from "../../components";
import type { Type as JSONType } from "../../schema";
export declare class TypeSerializer extends TypeSerializerComponent<Type> {
    static PRIORITY: number;
    supports(t: unknown): boolean;
    toObject(type: Type, obj?: Partial<JSONType>): JSONType;
}
