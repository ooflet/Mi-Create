"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DecoratorWrapper = void 0;
/**
 * An internal concrete implementation for the {@link Decorator} interface
 * so it can be identified
 */
class DecoratorWrapper {
    constructor(decorator) {
        this.decorator = decorator;
    }
}
exports.DecoratorWrapper = DecoratorWrapper;
