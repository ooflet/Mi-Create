import { ProjectReflection } from "../models";
import { Logger } from "../utils";
export declare function validateExports(project: ProjectReflection, logger: Logger, intentionallyNotExported: readonly string[]): void;
