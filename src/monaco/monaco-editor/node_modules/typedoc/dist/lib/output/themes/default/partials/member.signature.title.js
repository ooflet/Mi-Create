"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.memberSignatureTitle = void 0;
const lib_1 = require("../../lib");
const utils_1 = require("../../../../utils");
const memberSignatureTitle = (context, props, { hideName = false, arrowStyle = false } = {}) => {
    var _a;
    return (utils_1.JSX.createElement(utils_1.JSX.Fragment, null,
        !hideName ? ((0, lib_1.wbr)(props.name)) : (utils_1.JSX.createElement(utils_1.JSX.Fragment, null, props.kindString === "Constructor signature" && (utils_1.JSX.createElement(utils_1.JSX.Fragment, null,
            !!props.flags.isAbstract && utils_1.JSX.createElement("span", { class: "tsd-signature-symbol" }, "abstract "),
            utils_1.JSX.createElement("span", { class: "tsd-signature-symbol" }, "new "))))),
        (0, lib_1.renderTypeParametersSignature)(props.typeParameters),
        utils_1.JSX.createElement("span", { class: "tsd-signature-symbol" }, "("),
        (0, lib_1.join)(", ", (_a = props.parameters) !== null && _a !== void 0 ? _a : [], (item) => (utils_1.JSX.createElement(utils_1.JSX.Fragment, null,
            !!item.flags.isRest && utils_1.JSX.createElement("span", { class: "tsd-signature-symbol" }, "..."),
            item.name,
            utils_1.JSX.createElement("span", { class: "tsd-signature-symbol" },
                !!item.flags.isOptional && "?",
                !!item.defaultValue && "?",
                ": "),
            context.type(item.type)))),
        utils_1.JSX.createElement("span", { class: "tsd-signature-symbol" }, ")"),
        !!props.type && (utils_1.JSX.createElement(utils_1.JSX.Fragment, null,
            utils_1.JSX.createElement("span", { class: "tsd-signature-symbol" }, arrowStyle ? " => " : ": "),
            context.type(props.type)))));
};
exports.memberSignatureTitle = memberSignatureTitle;
