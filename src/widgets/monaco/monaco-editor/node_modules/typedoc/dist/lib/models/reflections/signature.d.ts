import { Type, ReferenceType } from "../types";
import { Reflection, TraverseCallback } from "./abstract";
import type { ParameterReflection } from "./parameter";
import type { TypeParameterReflection } from "./type-parameter";
import type { DeclarationReflection } from "./declaration";
import type { ReflectionKind } from "./kind";
export declare class SignatureReflection extends Reflection {
    /**
     * Create a new SignatureReflection to contain a specific type of signature.
     */
    constructor(name: string, kind: SignatureReflection["kind"], parent: DeclarationReflection);
    kind: ReflectionKind.SetSignature | ReflectionKind.GetSignature | ReflectionKind.IndexSignature | ReflectionKind.CallSignature | ReflectionKind.ConstructorSignature;
    parent: DeclarationReflection;
    parameters?: ParameterReflection[];
    typeParameters?: TypeParameterReflection[];
    type?: Type;
    /**
     * A type that points to the reflection that has been overwritten by this reflection.
     *
     * Applies to interface and class members.
     */
    overwrites?: ReferenceType;
    /**
     * A type that points to the reflection this reflection has been inherited from.
     *
     * Applies to interface and class members.
     */
    inheritedFrom?: ReferenceType;
    /**
     * A type that points to the reflection this reflection is the implementation of.
     *
     * Applies to class members.
     */
    implementationOf?: ReferenceType;
    /**
     * Traverse all potential child reflections of this reflection.
     *
     * The given callback will be invoked for all children, signatures and type parameters
     * attached to this reflection.
     *
     * @param callback  The callback function that should be applied for each child reflection.
     */
    traverse(callback: TraverseCallback): void;
    /**
     * Return a string representation of this reflection.
     */
    toString(): string;
}
