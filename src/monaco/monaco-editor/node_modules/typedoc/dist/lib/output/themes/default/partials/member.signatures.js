"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.memberSignatures = void 0;
const utils_1 = require("../../../../utils");
const memberSignatures = (context, props) => {
    var _a, _b;
    return (utils_1.JSX.createElement(utils_1.JSX.Fragment, null,
        utils_1.JSX.createElement("ul", { class: "tsd-signatures " + props.cssClasses }, (_a = props.signatures) === null || _a === void 0 ? void 0 : _a.map((item) => (utils_1.JSX.createElement("li", { class: "tsd-signature tsd-kind-icon" }, context.memberSignatureTitle(item))))),
        utils_1.JSX.createElement("ul", { class: "tsd-descriptions" }, (_b = props.signatures) === null || _b === void 0 ? void 0 : _b.map((item) => (utils_1.JSX.createElement("li", { class: "tsd-description" }, context.memberSignatureBody(item)))))));
};
exports.memberSignatures = memberSignatures;
