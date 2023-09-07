"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.comment = void 0;
const utils_1 = require("../../../../utils");
function comment({ markdown }, props) {
    var _a, _b;
    if (!((_a = props.comment) === null || _a === void 0 ? void 0 : _a.hasVisibleComponent()))
        return;
    return (utils_1.JSX.createElement("div", { class: "tsd-comment tsd-typography" },
        !!props.comment.shortText && (utils_1.JSX.createElement("div", { class: "lead" },
            utils_1.JSX.createElement(utils_1.Raw, { html: "\n" + markdown(props.comment.shortText) }))),
        !!props.comment.text && (utils_1.JSX.createElement("div", null,
            utils_1.JSX.createElement(utils_1.Raw, { html: markdown(props.comment.text) }))),
        ((_b = props.comment.tags) === null || _b === void 0 ? void 0 : _b.length) > 0 && (utils_1.JSX.createElement("dl", { class: "tsd-comment-tags" }, props.comment.tags.map((item) => (utils_1.JSX.createElement(utils_1.JSX.Fragment, null,
            utils_1.JSX.createElement("dt", null,
                item.tagName,
                item.paramName ? ` ${item.paramName}` : ""),
            utils_1.JSX.createElement("dd", null,
                utils_1.JSX.createElement(utils_1.Raw, { html: markdown(item.text) })))))))));
}
exports.comment = comment;
