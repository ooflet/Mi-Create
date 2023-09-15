import { SerializerComponent } from "../components";
import { DecoratorWrapper } from "./models/decorator-wrapper";
import type { Decorator } from "../schema";
export declare class DecoratorContainerSerializer extends SerializerComponent<DecoratorWrapper> {
    static PRIORITY: number;
    /**
     * Filter for instances of {@link DecoratorWrapper}
     */
    serializeGroup(instance: unknown): boolean;
    supports(): boolean;
    toObject({ decorator }: DecoratorWrapper, obj?: Partial<Decorator>): Decorator;
}
