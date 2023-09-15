"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.hasBeenLoadedMultipleTimes = void 0;
/**
 * This is a hack to make it possible to detect and warn about installation setups
 * which result in TypeDoc being installed multiple times. If TypeDoc has been loaded
 * multiple times, then parts of it will not work as expected.
 */
const loadSymbol = Symbol.for("typedoc_loads");
const getLoads = () => globalThis[loadSymbol] || 0;
// @ts-expect-error there's no way to add symbols to globalThis, sadly.
globalThis[loadSymbol] = getLoads() + 1;
function hasBeenLoadedMultipleTimes() {
    return getLoads() !== 1;
}
exports.hasBeenLoadedMultipleTimes = hasBeenLoadedMultipleTimes;
