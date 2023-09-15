import { Reflection, ReflectionFlags, TypeParameterReflection } from "../../models";
import { JSX } from "../../utils";
export declare function stringify(data: unknown): string;
/**
 * Insert word break tags ``<wbr>`` into the given string.
 *
 * Breaks the given string at ``_``, ``-`` and capital letters.
 *
 * @param str The string that should be split.
 * @return The original string containing ``<wbr>`` tags where possible.
 */
export declare function wbr(str: string): (string | JSX.Element)[];
export declare function join<T>(joiner: JSX.Children, list: readonly T[], cb: (x: T) => JSX.Children): JSX.Element;
export declare function renderFlags(flags: ReflectionFlags): JSX.Element;
export declare function classNames(names: Record<string, boolean | null | undefined>): string;
export declare function hasTypeParameters(reflection: Reflection): reflection is Reflection & {
    typeParameters: TypeParameterReflection[];
};
export declare function renderTypeParametersSignature(typeParameters: readonly TypeParameterReflection[] | undefined): JSX.Element;
