import { SignatureReflection } from "../../../models";
import { ReflectionSerializerComponent } from "../../components";
import type { SignatureReflection as JSONSignatureReflection, Reflection as JSONReflection } from "../../schema";
export declare class SignatureReflectionSerializer extends ReflectionSerializerComponent<SignatureReflection> {
    supports(t: unknown): boolean;
    toObject(signature: SignatureReflection, obj: JSONReflection): JSONSignatureReflection;
}
