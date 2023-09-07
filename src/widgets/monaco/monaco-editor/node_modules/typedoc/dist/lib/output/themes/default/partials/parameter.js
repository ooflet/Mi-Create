"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.parameter = void 0;
const lib_1 = require("../../lib");
const utils_1 = require("../../../../utils");
const models_1 = require("../../../../models");
const parameter = (context, props) => {
    var _a, _b, _c;
    return (utils_1.JSX.createElement(utils_1.JSX.Fragment, null,
        utils_1.JSX.createElement("ul", { class: "tsd-parameters" },
            !!props.signatures && (utils_1.JSX.createElement("li", { class: "tsd-parameter-signature" },
                utils_1.JSX.createElement("ul", { class: "tsd-signatures " + props.cssClasses }, props.signatures.map((item) => (utils_1.JSX.createElement("li", { class: "tsd-signature tsd-kind-icon" }, context.memberSignatureTitle(item, { hideName: true }))))),
                utils_1.JSX.createElement("ul", { class: "tsd-descriptions" }, props.signatures.map((item) => (utils_1.JSX.createElement("li", { class: "tsd-description" }, context.memberSignatureBody(item, { hideSources: true }))))))),
            !!props.indexSignature && (utils_1.JSX.createElement(utils_1.JSX.Fragment, null,
                utils_1.JSX.createElement("li", { class: "tsd-parameter-index-signature" },
                    utils_1.JSX.createElement("h5", null,
                        utils_1.JSX.createElement("span", { class: "tsd-signature-symbol" }, "["), (_b = (_a = props.indexSignature) === null || _a === void 0 ? void 0 : _a.parameters) === null || _b === void 0 ? void 0 :
                        _b.map((item) => (utils_1.JSX.createElement(utils_1.JSX.Fragment, null,
                            !!item.flags.isRest && utils_1.JSX.createElement("span", { class: "tsd-signature-symbol" }, "..."),
                            item.name,
                            ": ",
                            context.type(item.type)))),
                        utils_1.JSX.createElement("span", { class: "tsd-signature-symbol" }, "]: "),
                        context.type(props.indexSignature.type)),
                    context.comment(props.indexSignature),
                    props.indexSignature.type instanceof models_1.ReflectionType &&
                        context.parameter(props.indexSignature.type.declaration)))), (_c = props.children) === null || _c === void 0 ? void 0 :
            _c.map((item) => {
                var _a;
                return (utils_1.JSX.createElement(utils_1.JSX.Fragment, null, item.signatures ? (utils_1.JSX.createElement("li", { class: "tsd-parameter" },
                    utils_1.JSX.createElement("h5", null,
                        !!item.flags.isRest && utils_1.JSX.createElement("span", { class: "tsd-signature-symbol" }, "..."),
                        (0, lib_1.wbr)(item.name),
                        utils_1.JSX.createElement("span", { class: "tsd-signature-symbol" },
                            !!item.flags.isOptional && "?",
                            ":"),
                        "function"),
                    context.memberSignatures(item))) : item.type ? (utils_1.JSX.createElement(utils_1.JSX.Fragment, null,
                    utils_1.JSX.createElement("li", { class: "tsd-parameter" },
                        utils_1.JSX.createElement("h5", null,
                            (0, lib_1.renderFlags)(item.flags),
                            !!item.flags.isRest && utils_1.JSX.createElement("span", { class: "tsd-signature-symbol" }, "..."),
                            (0, lib_1.wbr)(item.name),
                            utils_1.JSX.createElement("span", { class: "tsd-signature-symbol" },
                                !!item.flags.isOptional && "?",
                                ": "),
                            context.type(item.type)),
                        context.comment(item),
                        !!item.children && context.parameter(item),
                        item.type instanceof models_1.ReflectionType && context.parameter(item.type.declaration)))) : (utils_1.JSX.createElement(utils_1.JSX.Fragment, null,
                    item.getSignature && (utils_1.JSX.createElement(utils_1.JSX.Fragment, null,
                        utils_1.JSX.createElement("li", { class: "tsd-parameter" },
                            utils_1.JSX.createElement("h5", null,
                                (0, lib_1.renderFlags)(item.getSignature.flags),
                                utils_1.JSX.createElement("span", { class: "tsd-signature-symbol" }, "get "),
                                (0, lib_1.wbr)(item.name),
                                utils_1.JSX.createElement("span", { class: "tsd-signature-symbol" }, "(): "),
                                context.type(item.getSignature.type)),
                            context.comment(item.getSignature)))),
                    item.setSignature && (utils_1.JSX.createElement(utils_1.JSX.Fragment, null,
                        utils_1.JSX.createElement("li", { class: "tsd-parameter" },
                            utils_1.JSX.createElement("h5", null,
                                (0, lib_1.renderFlags)(item.setSignature.flags),
                                utils_1.JSX.createElement("span", { class: "tsd-signature-symbol" }, "set "),
                                (0, lib_1.wbr)(item.name),
                                utils_1.JSX.createElement("span", { class: "tsd-signature-symbol" }, "("), (_a = item.setSignature.parameters) === null || _a === void 0 ? void 0 :
                                _a.map((item) => (utils_1.JSX.createElement(utils_1.JSX.Fragment, null,
                                    item.name,
                                    utils_1.JSX.createElement("span", { class: "tsd-signature-symbol" }, ": "),
                                    context.type(item.type)))),
                                utils_1.JSX.createElement("span", { class: "tsd-signature-symbol" }, "): "),
                                context.type(item.setSignature.type)),
                            context.comment(item.setSignature))))))));
            }))));
};
exports.parameter = parameter;
