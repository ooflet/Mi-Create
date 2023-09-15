import { IndexedAccessType } from "../../../models";
import { TypeSerializerComponent } from "../../components";
import type { Type as JSONType, IndexedAccessType as JSONIndexedAccessType } from "../../schema";
export declare class IndexedAccessTypeSerializer extends TypeSerializerComponent<IndexedAccessType> {
    supports(item: unknown): boolean;
    toObject(type: IndexedAccessType, obj: Pick<JSONIndexedAccessType, "type"> & JSONType): JSONIndexedAccessType;
}
