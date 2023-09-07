import { TypeOperatorType } from "../../../models";
import { TypeSerializerComponent } from "../../components";
import type { TypeOperatorType as JSONTypeOperatorType } from "../../schema";
export declare class TypeOperatorTypeSerializer extends TypeSerializerComponent<TypeOperatorType> {
    supports(t: unknown): boolean;
    toObject(type: TypeOperatorType, obj: Pick<JSONTypeOperatorType, "type">): JSONTypeOperatorType;
}
