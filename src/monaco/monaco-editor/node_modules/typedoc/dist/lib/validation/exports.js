"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.validateExports = void 0;
const path_1 = require("path");
const ts = require("typescript");
const models_1 = require("../models");
const utils_1 = require("../utils");
function makeIntentionallyExportedHelper(intentional, logger) {
    const used = new Set();
    const processed = intentional.map((v) => {
        const index = v.lastIndexOf(":");
        if (index === -1) {
            return ["", v];
        }
        return [v.substring(0, index), v.substring(index + 1)];
    });
    return {
        has(symbol) {
            var _a;
            // If it isn't declared anywhere, we can't produce a good error message about where
            // the non-exported symbol is, so even if it isn't ignored, pretend it is. In practice,
            // this will happen incredibly rarely, since symbols without declarations are very rare.
            // I know of only two instances:
            // 1. `undefined` in `globalThis`
            // 2. Properties on non-homomorphic mapped types, e.g. the symbol for "foo" on `Record<"foo", 1>`
            // There might be others, so still check this here rather than asserting, but print a debug log
            // so that we can possibly improve this in the future.
            if (!((_a = symbol.declarations) === null || _a === void 0 ? void 0 : _a.length)) {
                logger.verbose(`The symbol ${symbol.name} has no declarations, implicitly allowing missing export.`);
                return true;
            }
            // Don't produce warnings for third-party symbols.
            if (symbol.declarations.some((d) => d.getSourceFile().fileName.includes("node_modules"))) {
                return true;
            }
            for (const [index, [file, name]] of processed.entries()) {
                if (symbol.name === name &&
                    symbol.declarations.some((d) => d.getSourceFile().fileName.endsWith(file))) {
                    used.add(index);
                    return true;
                }
            }
            return false;
        },
        getUnused() {
            return intentional.filter((_, i) => !used.has(i));
        },
    };
}
function validateExports(project, logger, intentionallyNotExported) {
    var _a, _b, _c, _d, _e, _f, _g, _h;
    let current = project;
    const queue = [];
    const intentional = makeIntentionallyExportedHelper(intentionallyNotExported, logger);
    const warned = new Set();
    const visitor = (0, models_1.makeRecursiveVisitor)({
        reference(type) {
            // If we don't have a symbol, then this was an intentionally broken reference.
            const symbol = type.getSymbol();
            if (!type.reflection && symbol) {
                if ((symbol.flags & ts.SymbolFlags.TypeParameter) === 0 &&
                    !intentional.has(symbol) &&
                    !warned.has(symbol)) {
                    warned.add(symbol);
                    const decl = symbol.declarations[0];
                    const { line } = ts.getLineAndCharacterOfPosition(decl.getSourceFile(), decl.getStart());
                    const file = (0, utils_1.normalizePath)((0, path_1.relative)(process.cwd(), decl.getSourceFile().fileName));
                    logger.warn(`${type.name}, defined at ${file}:${line + 1}, is referenced by ${current.getFullName()} but not included in the documentation.`);
                }
            }
        },
        reflection(type) {
            queue.push(type.declaration);
        },
    });
    const add = (item) => {
        if (!item)
            return;
        if (item instanceof models_1.Reflection) {
            queue.push(item);
        }
        else {
            queue.push(...item);
        }
    };
    do {
        if (current instanceof models_1.ContainerReflection) {
            add(current.children);
        }
        if (current instanceof models_1.DeclarationReflection) {
            (_a = current.type) === null || _a === void 0 ? void 0 : _a.visit(visitor);
            add(current.typeParameters);
            add(current.signatures);
            add(current.indexSignature);
            add(current.getSignature);
            add(current.setSignature);
            (_b = current.overwrites) === null || _b === void 0 ? void 0 : _b.visit(visitor);
            // Do not check inheritedFrom, it doesn't always make sense to export a base type.
            // Do not validate implementationOf will always be defined or intentionally broken.
            // Do not check extendedTypes, it doesn't always make sense to export a base type.
            // Do not validate extendedBy, guaranteed to all be in the documentation.
            (_c = current.implementedTypes) === null || _c === void 0 ? void 0 : _c.forEach((type) => type.visit(visitor));
            // Do not validate implementedBy, guaranteed to all be in the documentation.
        }
        if (current instanceof models_1.SignatureReflection) {
            add(current.parameters);
            add(current.typeParameters);
            (_d = current.type) === null || _d === void 0 ? void 0 : _d.visit(visitor);
            (_e = current.overwrites) === null || _e === void 0 ? void 0 : _e.visit(visitor);
            // Do not check inheritedFrom, it doesn't always make sense to export a base type.
            // Do not validate implementationOf will always be defined or intentionally broken.
        }
        if (current instanceof models_1.ParameterReflection) {
            (_f = current.type) === null || _f === void 0 ? void 0 : _f.visit(visitor);
        }
        if (current instanceof models_1.TypeParameterReflection) {
            (_g = current.type) === null || _g === void 0 ? void 0 : _g.visit(visitor);
            (_h = current.default) === null || _h === void 0 ? void 0 : _h.visit(visitor);
        }
    } while ((current = queue.shift()));
    const unusedIntentional = intentional.getUnused();
    if (unusedIntentional.length) {
        logger.warn("The following symbols were marked as intentionally not exported, but were either not referenced in the documentation, or were exported:\n\t" +
            unusedIntentional.join("\n\t"));
    }
}
exports.validateExports = validateExports;
