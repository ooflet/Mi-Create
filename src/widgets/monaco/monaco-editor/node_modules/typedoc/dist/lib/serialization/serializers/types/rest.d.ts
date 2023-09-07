import { RestType } from "../../../models";
import { TypeSerializerComponent } from "../../components";
import type { RestType as JSONRestType } from "../../schema";
export declare class RestTypeSerializer extends TypeSerializerComponent<RestType> {
    supports(t: unknown): boolean;
    /**
     * Will be run after {@link TypeSerializer} so `type` will already be set.
     * @param type
     * @param obj
     */
    toObject(type: RestType, obj: Pick<JSONRestType, "type">): JSONRestType;
}
