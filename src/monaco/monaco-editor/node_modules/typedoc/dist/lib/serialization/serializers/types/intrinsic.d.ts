import { IntrinsicType } from "../../../models";
import { TypeSerializerComponent } from "../../components";
import type { IntrinsicType as JSONIntrinsicType } from "../../schema";
export declare class IntrinsicTypeSerializer extends TypeSerializerComponent<IntrinsicType> {
    supports(t: unknown): boolean;
    /**
     * Will be run after {@link TypeSerializer} so `type` will already be set.
     * @param type
     * @param obj
     */
    toObject(type: IntrinsicType, obj: Pick<JSONIntrinsicType, "type">): JSONIntrinsicType;
}
