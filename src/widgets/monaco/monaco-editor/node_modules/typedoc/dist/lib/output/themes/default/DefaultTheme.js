"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DefaultTheme = void 0;
const theme_1 = require("../../theme");
const index_1 = require("../../../models/reflections/index");
const UrlMapping_1 = require("../../models/UrlMapping");
const events_1 = require("../../events");
const DefaultThemeRenderContext_1 = require("./DefaultThemeRenderContext");
const utils_1 = require("../../../utils");
/**
 * Default theme implementation of TypeDoc. If a theme does not provide a custom
 * {@link Theme} implementation, this theme class will be used.
 */
class DefaultTheme extends theme_1.Theme {
    /**
     * Create a new DefaultTheme instance.
     *
     * @param renderer  The renderer this theme is attached to.
     * @param basePath  The base path of this theme.
     */
    constructor(renderer) {
        super(renderer);
        this.reflectionTemplate = (pageEvent) => {
            return this.getRenderContext(pageEvent).reflectionTemplate(pageEvent);
        };
        this.indexTemplate = (pageEvent) => {
            return this.getRenderContext(pageEvent).indexTemplate(pageEvent);
        };
        this.defaultLayoutTemplate = (pageEvent) => {
            return this.getRenderContext(pageEvent).defaultLayout(pageEvent);
        };
        /**
         * Mappings of reflections kinds to templates used by this theme.
         */
        this.mappings = [
            {
                kind: [index_1.ReflectionKind.Class],
                isLeaf: false,
                directory: "classes",
                template: this.reflectionTemplate,
            },
            {
                kind: [index_1.ReflectionKind.Interface],
                isLeaf: false,
                directory: "interfaces",
                template: this.reflectionTemplate,
            },
            {
                kind: [index_1.ReflectionKind.Enum],
                isLeaf: false,
                directory: "enums",
                template: this.reflectionTemplate,
            },
            {
                kind: [index_1.ReflectionKind.Namespace, index_1.ReflectionKind.Module],
                isLeaf: false,
                directory: "modules",
                template: this.reflectionTemplate,
            },
        ];
        this.markedPlugin = renderer.getComponent("marked");
        this.listenTo(renderer, events_1.RendererEvent.BEGIN, this.onRendererBegin, 1024);
    }
    getRenderContext(_pageEvent) {
        if (!this._renderContext) {
            this._renderContext = new DefaultThemeRenderContext_1.DefaultThemeRenderContext(this, this.application.options);
        }
        return this._renderContext;
    }
    /**
     * Map the models of the given project to the desired output files.
     *
     * @param project  The project whose urls should be generated.
     * @returns        A list of {@link UrlMapping} instances defining which models
     *                 should be rendered to which files.
     */
    getUrls(project) {
        var _a;
        const urls = [];
        if (false == hasReadme(this.application.options.getValue("readme"))) {
            project.url = "index.html";
            urls.push(new UrlMapping_1.UrlMapping("index.html", project, this.reflectionTemplate));
        }
        else {
            project.url = "modules.html";
            urls.push(new UrlMapping_1.UrlMapping("modules.html", project, this.reflectionTemplate));
            urls.push(new UrlMapping_1.UrlMapping("index.html", project, this.indexTemplate));
        }
        (_a = project.children) === null || _a === void 0 ? void 0 : _a.forEach((child) => {
            if (child instanceof index_1.DeclarationReflection) {
                this.buildUrls(child, urls);
            }
        });
        return urls;
    }
    /**
     * Triggered before the renderer starts rendering a project.
     *
     * @param event  An event object describing the current render operation.
     */
    onRendererBegin(event) {
        if (event.project.groups) {
            event.project.groups.forEach(DefaultTheme.applyGroupClasses);
        }
        for (const id in event.project.reflections) {
            const reflection = event.project.reflections[id];
            if (reflection instanceof index_1.DeclarationReflection) {
                DefaultTheme.applyReflectionClasses(reflection);
            }
            if (reflection instanceof index_1.ContainerReflection && reflection.groups) {
                reflection.groups.forEach(DefaultTheme.applyGroupClasses);
            }
        }
    }
    /**
     * Return a url for the given reflection.
     *
     * @param reflection  The reflection the url should be generated for.
     * @param relative    The parent reflection the url generation should stop on.
     * @param separator   The separator used to generate the url.
     * @returns           The generated url.
     */
    static getUrl(reflection, relative, separator = ".") {
        let url = reflection.getAlias();
        if (reflection.parent && reflection.parent !== relative && !(reflection.parent instanceof index_1.ProjectReflection)) {
            url = DefaultTheme.getUrl(reflection.parent, relative, separator) + separator + url;
        }
        return url;
    }
    /**
     * Return the template mapping for the given reflection.
     *
     * @param reflection  The reflection whose mapping should be resolved.
     * @returns           The found mapping or undefined if no mapping could be found.
     */
    getMapping(reflection) {
        return this.mappings.find((mapping) => reflection.kindOf(mapping.kind));
    }
    /**
     * Build the url for the the given reflection and all of its children.
     *
     * @param reflection  The reflection the url should be created for.
     * @param urls        The array the url should be appended to.
     * @returns           The altered urls array.
     */
    buildUrls(reflection, urls) {
        const mapping = this.getMapping(reflection);
        if (mapping) {
            if (!reflection.url || !DefaultTheme.URL_PREFIX.test(reflection.url)) {
                const url = [mapping.directory, DefaultTheme.getUrl(reflection) + ".html"].join("/");
                urls.push(new UrlMapping_1.UrlMapping(url, reflection, mapping.template));
                reflection.url = url;
                reflection.hasOwnDocument = true;
            }
            for (const child of reflection.children || []) {
                if (mapping.isLeaf) {
                    DefaultTheme.applyAnchorUrl(child, reflection);
                }
                else {
                    this.buildUrls(child, urls);
                }
            }
        }
        else if (reflection.parent) {
            DefaultTheme.applyAnchorUrl(reflection, reflection.parent);
        }
        return urls;
    }
    render(page) {
        const templateOutput = this.defaultLayoutTemplate(page);
        return "<!DOCTYPE html>" + utils_1.JSX.renderElement(templateOutput);
    }
    /**
     * Generate an anchor url for the given reflection and all of its children.
     *
     * @param reflection  The reflection an anchor url should be created for.
     * @param container   The nearest reflection having an own document.
     */
    static applyAnchorUrl(reflection, container) {
        if (!reflection.url || !DefaultTheme.URL_PREFIX.test(reflection.url)) {
            const anchor = DefaultTheme.getUrl(reflection, container, ".");
            reflection.url = container.url + "#" + anchor;
            reflection.anchor = anchor;
            reflection.hasOwnDocument = false;
        }
        reflection.traverse((child) => {
            if (child instanceof index_1.DeclarationReflection) {
                DefaultTheme.applyAnchorUrl(child, container);
            }
            return true;
        });
    }
    /**
     * Generate the css classes for the given reflection and apply them to the
     * {@link DeclarationReflection.cssClasses} property.
     *
     * @param reflection  The reflection whose cssClasses property should be generated.
     */
    static applyReflectionClasses(reflection) {
        const classes = [];
        let kind;
        if (reflection.kind === index_1.ReflectionKind.Accessor) {
            if (!reflection.getSignature) {
                classes.push("tsd-kind-set-signature");
            }
            else if (!reflection.setSignature) {
                classes.push("tsd-kind-get-signature");
            }
            else {
                classes.push("tsd-kind-accessor");
            }
        }
        else {
            kind = index_1.ReflectionKind[reflection.kind];
            classes.push(DefaultTheme.toStyleClass("tsd-kind-" + kind));
        }
        if (reflection.parent && reflection.parent instanceof index_1.DeclarationReflection) {
            kind = index_1.ReflectionKind[reflection.parent.kind];
            classes.push(DefaultTheme.toStyleClass(`tsd-parent-kind-${kind}`));
        }
        let hasTypeParameters = !!reflection.typeParameters;
        reflection.getAllSignatures().forEach((signature) => {
            hasTypeParameters = hasTypeParameters || !!signature.typeParameters;
        });
        if (hasTypeParameters) {
            classes.push("tsd-has-type-parameter");
        }
        if (reflection.overwrites) {
            classes.push("tsd-is-overwrite");
        }
        if (reflection.inheritedFrom) {
            classes.push("tsd-is-inherited");
        }
        if (reflection.flags.isPrivate) {
            classes.push("tsd-is-private");
        }
        if (reflection.flags.isProtected) {
            classes.push("tsd-is-protected");
        }
        if (reflection.flags.isStatic) {
            classes.push("tsd-is-static");
        }
        if (reflection.flags.isExternal) {
            classes.push("tsd-is-external");
        }
        reflection.cssClasses = classes.join(" ");
    }
    /**
     * Generate the css classes for the given reflection group and apply them to the
     * {@link ReflectionGroup.cssClasses} property.
     *
     * @param group  The reflection group whose cssClasses property should be generated.
     */
    static applyGroupClasses(group) {
        const classes = [];
        if (group.allChildrenAreInherited) {
            classes.push("tsd-is-inherited");
        }
        if (group.allChildrenArePrivate) {
            classes.push("tsd-is-private");
        }
        if (group.allChildrenAreProtectedOrPrivate) {
            classes.push("tsd-is-private-protected");
        }
        if (group.allChildrenAreExternal) {
            classes.push("tsd-is-external");
        }
        group.cssClasses = classes.join(" ");
    }
    /**
     * Transform a space separated string into a string suitable to be used as a
     * css class, e.g. "constructor method" > "Constructor-method".
     */
    static toStyleClass(str) {
        return str.replace(/(\w)([A-Z])/g, (_m, m1, m2) => m1 + "-" + m2).toLowerCase();
    }
}
exports.DefaultTheme = DefaultTheme;
DefaultTheme.URL_PREFIX = /^(http|ftp)s?:\/\//;
function hasReadme(readme) {
    return !readme.endsWith("none");
}
