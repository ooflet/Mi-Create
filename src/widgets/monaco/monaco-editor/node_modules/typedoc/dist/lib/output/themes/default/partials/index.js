"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.index = void 0;
const lib_1 = require("../../lib");
const utils_1 = require("../../../../utils");
function renderCategory({ urlTo }, item, prependName = "") {
    return (utils_1.JSX.createElement("section", { class: "tsd-index-section" },
        utils_1.JSX.createElement("h3", null, prependName ? `${prependName} ${item.title}` : item.title),
        utils_1.JSX.createElement("ul", { class: "tsd-index-list" }, item.children.map((item) => (utils_1.JSX.createElement("li", { class: item.cssClasses },
            utils_1.JSX.createElement("a", { href: urlTo(item), class: "tsd-kind-icon" }, item.name ? (0, lib_1.wbr)(item.name) : utils_1.JSX.createElement("em", null, (0, lib_1.wbr)(item.kindString)))))))));
}
function index(context, props) {
    if (props.categories && props.categories.length) {
        return (utils_1.JSX.createElement("section", { class: "tsd-panel-group tsd-index-group" },
            utils_1.JSX.createElement("h2", null, "Index"),
            utils_1.JSX.createElement("section", { class: "tsd-panel tsd-index-panel" },
                utils_1.JSX.createElement("div", { class: "tsd-index-content" }, props.categories.map((item) => renderCategory(context, item))))));
    }
    if (props.groups && props.groups.length) {
        return (utils_1.JSX.createElement("section", { class: "tsd-panel-group tsd-index-group" },
            utils_1.JSX.createElement("h2", null, "Index"),
            utils_1.JSX.createElement("section", { class: "tsd-panel tsd-index-panel" },
                utils_1.JSX.createElement("div", { class: "tsd-index-content" }, props.groups.map((item) => (utils_1.JSX.createElement("section", { class: "tsd-index-section " + item.cssClasses }, item.categories ? (item.categories.map((item2) => renderCategory(context, item2, item.title))) : (utils_1.JSX.createElement(utils_1.JSX.Fragment, null,
                    utils_1.JSX.createElement("h3", null, item.title),
                    utils_1.JSX.createElement("ul", { class: "tsd-index-list" }, item.children.map((item) => (utils_1.JSX.createElement("li", { class: item.cssClasses },
                        utils_1.JSX.createElement("a", { href: context.urlTo(item), class: "tsd-kind-icon" }, item.name ? (0, lib_1.wbr)(item.name) : utils_1.JSX.createElement("em", null, (0, lib_1.wbr)(item.kindString))))))))))))))));
    }
}
exports.index = index;
