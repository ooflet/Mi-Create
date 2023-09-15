import { ProjectReflection, ReflectionKind } from "../models";
import { Logger } from "../utils";
export declare function validateDocumentation(project: ProjectReflection, logger: Logger, requiredToBeDocumented: readonly (keyof typeof ReflectionKind)[]): void;
