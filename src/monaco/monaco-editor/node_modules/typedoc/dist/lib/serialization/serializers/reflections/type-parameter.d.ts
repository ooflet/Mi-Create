import { TypeParameterReflection } from "../../../models";
import { ReflectionSerializerComponent } from "../../components";
import type { TypeParameterReflection as JSONTypeParameterReflection, Reflection as JSONReflection } from "../../schema";
export declare class TypeParameterReflectionSerializer extends ReflectionSerializerComponent<TypeParameterReflection> {
    supports(t: unknown): boolean;
    toObject(typeParameter: TypeParameterReflection, obj: JSONReflection): JSONTypeParameterReflection;
}
