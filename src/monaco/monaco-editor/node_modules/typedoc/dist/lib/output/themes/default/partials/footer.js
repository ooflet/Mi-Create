"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.footer = void 0;
const utils_1 = require("../../../../utils");
const lib_1 = require("../../lib");
function footer(context, props) {
    var _a;
    const hideLegend = context.options.getValue("hideLegend");
    const hideGenerator = context.options.getValue("hideGenerator");
    return (utils_1.JSX.createElement(utils_1.JSX.Fragment, null,
        utils_1.JSX.createElement("footer", { class: (0, lib_1.classNames)({
                "with-border-bottom": !hideGenerator,
            }) },
            utils_1.JSX.createElement("div", { class: "container" },
                !hideLegend && ((_a = props.legend) === null || _a === void 0 ? void 0 : _a.length) && (utils_1.JSX.createElement(utils_1.JSX.Fragment, null,
                    utils_1.JSX.createElement("h2", null, "Legend"),
                    utils_1.JSX.createElement("div", { class: "tsd-legend-group" }, props.legend.map((item) => (utils_1.JSX.createElement("ul", { class: "tsd-legend" }, item.map((item) => (utils_1.JSX.createElement("li", { class: item.classes.join(" ") },
                        utils_1.JSX.createElement("span", { class: "tsd-kind-icon" }, item.name)))))))))),
                utils_1.JSX.createElement("h2", null, "Settings"),
                utils_1.JSX.createElement("p", null,
                    "Theme",
                    " ",
                    utils_1.JSX.createElement("select", { id: "theme" },
                        utils_1.JSX.createElement("option", { value: "os" }, "OS"),
                        utils_1.JSX.createElement("option", { value: "light" }, "Light"),
                        utils_1.JSX.createElement("option", { value: "dark" }, "Dark"))))),
        !hideGenerator && (utils_1.JSX.createElement("div", { class: "container tsd-generator" },
            utils_1.JSX.createElement("p", null,
                "Generated using ",
                utils_1.JSX.createElement("a", { href: "https://typedoc.org/", target: "_blank" }, "TypeDoc"))))));
}
exports.footer = footer;
