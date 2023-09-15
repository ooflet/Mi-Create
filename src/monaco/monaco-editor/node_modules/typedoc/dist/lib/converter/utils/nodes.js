"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getHeritageTypes = exports.isNamedNode = void 0;
const ts = require("typescript");
const array_1 = require("../../utils/array");
function isNamedNode(node) {
    const name = node.name;
    return (!!name &&
        (ts.isIdentifierOrPrivateIdentifier(name) ||
            ts.isComputedPropertyName(name)));
}
exports.isNamedNode = isNamedNode;
function getHeritageTypes(declarations, kind) {
    const exprs = (0, array_1.flatMap)(declarations, (d) => {
        var _a, _b;
        return (0, array_1.flatMap)((_b = (_a = d.heritageClauses) === null || _a === void 0 ? void 0 : _a.filter((hc) => hc.token === kind)) !== null && _b !== void 0 ? _b : [], (hc) => hc.types);
    });
    const seenTexts = new Set();
    return exprs.filter((expr) => {
        const text = expr.getText();
        if (seenTexts.has(text)) {
            return false;
        }
        seenTexts.add(text);
        return true;
    });
}
exports.getHeritageTypes = getHeritageTypes;
