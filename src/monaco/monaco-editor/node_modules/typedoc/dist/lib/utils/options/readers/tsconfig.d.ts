import type { OptionsReader, Options } from "../options";
import type { Logger } from "../../loggers";
export declare class TSConfigReader implements OptionsReader {
    /**
     * Note: Runs after the {@link TypeDocReader}.
     */
    priority: number;
    name: string;
    /**
     * Not considered part of the public API. You can use it, but it might break.
     * @internal
     */
    static findConfigFile(file: string): string | undefined;
    read(container: Options, logger: Logger): void;
}
