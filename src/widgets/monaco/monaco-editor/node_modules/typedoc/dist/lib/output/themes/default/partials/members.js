"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.members = void 0;
const utils_1 = require("../../../../utils");
function members(context, props) {
    var _a;
    if (props.categories && props.categories.length) {
        return (utils_1.JSX.createElement(utils_1.JSX.Fragment, null, props.categories.map((item) => !item.allChildrenHaveOwnDocument() && (utils_1.JSX.createElement("section", { class: "tsd-panel-group tsd-member-group " + props.cssClasses },
            utils_1.JSX.createElement("h2", null, item.title),
            item.children.map((item) => !item.hasOwnDocument && context.member(item)))))));
    }
    return utils_1.JSX.createElement(utils_1.JSX.Fragment, null, (_a = props.groups) === null || _a === void 0 ? void 0 : _a.map((item) => !item.allChildrenHaveOwnDocument() && context.membersGroup(item)));
}
exports.members = members;
