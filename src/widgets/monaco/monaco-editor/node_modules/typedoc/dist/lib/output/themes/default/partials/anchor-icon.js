"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.anchorIcon = void 0;
const utils_1 = require("../../../../utils");
const anchorIcon = (anchor) => (utils_1.JSX.createElement("a", { href: `#${anchor}`, "aria-label": "Permalink", class: "tsd-anchor-icon" },
    utils_1.JSX.createElement("svg", { xmlns: "http://www.w3.org/2000/svg", class: "icon icon-tabler icon-tabler-link", viewBox: "0 0 24 24", "stroke-width": "2", stroke: "currentColor", fill: "none", "stroke-linecap": "round", "stroke-linejoin": "round" },
        utils_1.JSX.createElement("path", { stroke: "none", d: "M0 0h24v24H0z", fill: "none" }),
        utils_1.JSX.createElement("path", { d: "M10 14a3.5 3.5 0 0 0 5 0l4 -4a3.5 3.5 0 0 0 -5 -5l-.5 .5" }),
        utils_1.JSX.createElement("path", { d: "M14 10a3.5 3.5 0 0 0 -5 0l-4 4a3.5 3.5 0 0 0 5 5l.5 -.5" }))));
exports.anchorIcon = anchorIcon;
