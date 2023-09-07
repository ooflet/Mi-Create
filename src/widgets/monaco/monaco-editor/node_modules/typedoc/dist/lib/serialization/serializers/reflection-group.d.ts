import { ReflectionGroup } from "../../models/ReflectionGroup";
import { SerializerComponent } from "../components";
import type { ReflectionGroup as JSONReflectionGroup } from "../schema";
export declare class ReflectionGroupSerializer extends SerializerComponent<ReflectionGroup> {
    static PRIORITY: number;
    /**
     * Filter for instances of {@link ReflectionGroup}
     */
    serializeGroup(instance: unknown): boolean;
    supports(): boolean;
    toObject(group: ReflectionGroup, obj?: Partial<JSONReflectionGroup>): JSONReflectionGroup;
}
