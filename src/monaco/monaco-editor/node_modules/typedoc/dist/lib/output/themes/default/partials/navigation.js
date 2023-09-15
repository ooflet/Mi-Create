"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.navigation = void 0;
const models_1 = require("../../../../models");
const utils_1 = require("../../../../utils");
const lib_1 = require("../../lib");
function navigation(context, props) {
    return (utils_1.JSX.createElement(utils_1.JSX.Fragment, null,
        primaryNavigation(context, props),
        secondaryNavigation(context, props)));
}
exports.navigation = navigation;
function primaryNavigation(context, props) {
    // Create the navigation for the current page:
    // If there are modules marked as "external" then put them in their own group.
    const modules = props.model.project.getChildrenByKind(models_1.ReflectionKind.SomeModule);
    const projectLinkName = modules.some((m) => m.kindOf(models_1.ReflectionKind.Module)) ? "Modules" : "Exports";
    const [ext, int] = (0, utils_1.partition)(modules, (m) => m.flags.isExternal);
    if (ext.length === 0) {
        return (utils_1.JSX.createElement("nav", { class: "tsd-navigation primary" },
            utils_1.JSX.createElement("ul", null,
                utils_1.JSX.createElement("li", { class: (0, lib_1.classNames)({ current: props.model.isProject() }) },
                    utils_1.JSX.createElement("a", { href: context.urlTo(props.model.project) }, projectLinkName)),
                int.map(link))));
    }
    return (utils_1.JSX.createElement("nav", { class: "tsd-navigation primary" },
        utils_1.JSX.createElement("ul", null,
            utils_1.JSX.createElement("li", { class: (0, lib_1.classNames)({ current: props.model.isProject() }) },
                utils_1.JSX.createElement("a", { href: context.urlTo(props.model.project) }, projectLinkName)),
            utils_1.JSX.createElement("li", { class: "label tsd-is-external" },
                utils_1.JSX.createElement("span", null, "Internals")),
            int.map(link),
            utils_1.JSX.createElement("li", { class: "label tsd-is-external" },
                utils_1.JSX.createElement("span", null, "Externals")),
            ext.map(link))));
    function link(mod) {
        var _a;
        const current = inPath(mod, props.model);
        let childNav;
        if (current) {
            const childModules = (_a = mod.children) === null || _a === void 0 ? void 0 : _a.filter((m) => m.kindOf(models_1.ReflectionKind.SomeModule));
            if (childModules === null || childModules === void 0 ? void 0 : childModules.length) {
                childNav = utils_1.JSX.createElement("ul", null, childModules.map(link));
            }
        }
        return (utils_1.JSX.createElement("li", { class: (0, lib_1.classNames)({ current }) + " " + mod.cssClasses },
            utils_1.JSX.createElement("a", { href: context.urlTo(mod) }, (0, lib_1.wbr)(mod.name)),
            childNav));
    }
}
function secondaryNavigation(context, props) {
    const children = props.model instanceof models_1.ContainerReflection ? props.model.children || [] : [];
    // Multiple entry points, and on main project page.
    if (props.model.isProject() && props.model.getChildrenByKind(models_1.ReflectionKind.Module).length) {
        return;
    }
    // TODO: TypeDoc 0.21 did special things here. If there were more than 40
    // children of this page's parent, it only displayed this page's children.
    // Otherwise, it displayed *everything*. For now, only display page children.
    // It seems weird to do this according to a random hardcoded number. At the very
    // least this should be added as a configurable flag, but maybe even the whole
    // behavior should be configurable globally...
    const pageNavigation = (utils_1.JSX.createElement("ul", null, children
        .filter((child) => !child.kindOf(models_1.ReflectionKind.SomeModule))
        .map((child) => {
        return (utils_1.JSX.createElement("li", { class: child.cssClasses },
            utils_1.JSX.createElement("a", { href: context.urlTo(child), class: "tsd-kind-icon" }, (0, lib_1.wbr)(child.name))));
    })));
    if (props.model.kindOf(models_1.ReflectionKind.SomeModule | models_1.ReflectionKind.Project)) {
        return utils_1.JSX.createElement("nav", { class: "tsd-navigation secondary menu-sticky" }, pageNavigation);
    }
    return (utils_1.JSX.createElement("nav", { class: "tsd-navigation secondary menu-sticky" },
        utils_1.JSX.createElement("ul", null,
            utils_1.JSX.createElement("li", { class: "current " + props.model.cssClasses },
                utils_1.JSX.createElement("a", { href: context.urlTo(props.model), class: "tsd-kind-icon" }, (0, lib_1.wbr)(props.model.name)),
                pageNavigation))));
}
function inPath(thisPage, toCheck) {
    while (toCheck) {
        if (toCheck.isProject())
            return false;
        if (thisPage === toCheck)
            return true;
        toCheck = toCheck.parent;
    }
    return false;
}
