import { ContainerReflection } from "../../../models";
import { ReflectionSerializerComponent } from "../../components";
import type { ContainerReflection as JSONContainerReflection, Reflection as JSONReflection } from "../../schema";
export declare class ContainerReflectionSerializer extends ReflectionSerializerComponent<ContainerReflection> {
    supports(t: unknown): boolean;
    /**
     * Will be run after {@link ReflectionSerializer} so will be passed the result of that serialization.
     * @param container
     * @param obj
     */
    toObject(container: ContainerReflection, obj: JSONReflection): JSONContainerReflection;
}
