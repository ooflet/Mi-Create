import { Reflection, SomeType } from "../../models";
export declare function removeUndefined(type: SomeType): SomeType;
/**
 * Copy the comment of the source reflection to the target reflection.
 *
 * @param target - Reflection with comment containing `inheritdoc` tag
 * @param source - Referenced reflection
 */
export declare function copyComment(target: Reflection, source: Reflection): void;
