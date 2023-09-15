import { NamedTupleMember, TupleType } from "../../../models";
import { TypeSerializerComponent } from "../../components";
import type { TupleType as JSONTupleType, NamedTupleMemberType as JSONNamedTupleMemberType } from "../../schema";
export declare class TupleTypeSerializer extends TypeSerializerComponent<TupleType> {
    supports(t: unknown): boolean;
    toObject(tuple: TupleType, obj: Pick<JSONTupleType, "type">): JSONTupleType;
}
export declare class NamedTupleMemberTypeSerializer extends TypeSerializerComponent<NamedTupleMember> {
    supports(t: unknown): boolean;
    toObject(tuple: NamedTupleMember, obj: Pick<JSONNamedTupleMemberType, "type">): JSONNamedTupleMemberType;
}
