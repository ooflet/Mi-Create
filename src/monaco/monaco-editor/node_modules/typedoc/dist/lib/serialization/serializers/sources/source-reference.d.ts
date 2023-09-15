import { SerializerComponent } from "../../components";
import { SourceReferenceWrapper } from "../models";
import type { SourceReference as JSONSourceReference } from "../../schema";
export declare class SourceReferenceContainerSerializer extends SerializerComponent<SourceReferenceWrapper> {
    static PRIORITY: number;
    serializeGroup(instance: unknown): boolean;
    supports(): boolean;
    toObject({ sourceReference: ref }: SourceReferenceWrapper, obj?: Partial<JSONSourceReference>): JSONSourceReference;
}
