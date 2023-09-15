"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.Renderer = void 0;
/**
 * Holds all logic used render and output the final documentation.
 *
 * The {@link Renderer} class is the central controller within this namespace. When invoked it creates
 * an instance of {@link Theme} which defines the layout of the documentation and fires a
 * series of {@link RendererEvent} events. Instances of {@link BasePlugin} can listen to these events and
 * alter the generated output.
 */
const fs = require("fs");
const path = require("path");
const events_1 = require("./events");
const fs_1 = require("../utils/fs");
const DefaultTheme_1 = require("./themes/default/DefaultTheme");
const components_1 = require("./components");
const component_1 = require("../utils/component");
const utils_1 = require("../utils");
const highlighter_1 = require("../utils/highlighter");
const models_1 = require("../models");
/**
 * The renderer processes a {@link ProjectReflection} using a {@link Theme} instance and writes
 * the emitted html documents to a output directory. You can specify which theme should be used
 * using the `--theme <name>` command line argument.
 *
 * {@link Renderer} is a subclass of {@link EventDispatcher} and triggers a series of events while
 * a project is being processed. You can listen to these events to control the flow or manipulate
 * the output.
 *
 *  * {@link Renderer.EVENT_BEGIN}<br>
 *    Triggered before the renderer starts rendering a project. The listener receives
 *    an instance of {@link RendererEvent}. By calling {@link RendererEvent.preventDefault} the entire
 *    render process can be canceled.
 *
 *    * {@link Renderer.EVENT_BEGIN_PAGE}<br>
 *      Triggered before a document will be rendered. The listener receives an instance of
 *      {@link PageEvent}. By calling {@link PageEvent.preventDefault} the generation of the
 *      document can be canceled.
 *
 *    * {@link Renderer.EVENT_END_PAGE}<br>
 *      Triggered after a document has been rendered, just before it is written to disc. The
 *      listener receives an instance of {@link PageEvent}. When calling
 *      {@link PageEvent.preventDefault} the the document will not be saved to disc.
 *
 *  * {@link Renderer.EVENT_END}<br>
 *    Triggered after the renderer has written all documents. The listener receives
 *    an instance of {@link RendererEvent}.
 */
let Renderer = class Renderer extends component_1.ChildableComponent {
    constructor() {
        super(...arguments);
        this.themes = new Map([
            ["default", DefaultTheme_1.DefaultTheme],
        ]);
        this.unknownSymbolResolvers = new Map();
        /**
         * Hooks which will be called when rendering pages.
         * Note:
         * - Hooks added during output will be discarded at the end of rendering.
         * - Hooks added during a page render will be discarded at the end of that page's render.
         *
         * See {@link RendererHooks} for a description of each available hook, and when it will be called.
         */
        this.hooks = new utils_1.EventHooks();
    }
    /**
     * Define a new theme that can be used to render output.
     * This API will likely be changing in TypeDoc 0.23.
     * (sorry... changing as soon as it's introduced)
     * As it is, it provides reasonable flexibility, but doesn't give users a sufficiently
     * easy way to overwrite parts of a theme.
     * @param name
     * @param theme
     */
    defineTheme(name, theme) {
        if (this.themes.has(name)) {
            throw new Error(`The theme "${name}" has already been defined.`);
        }
        this.themes.set(name, theme);
    }
    /**
     * Adds a new resolver that the theme can used to try to figure out how to link to a symbol
     * declared by a third-party library which is not included in the documentation.
     * @param packageName the npm package name that this resolver can handle to limit which files it will be tried on.
     *   If the resolver will create links for Node builtin types, it should be set to `@types/node`.
     *   Links for builtin types live in the default lib files under `typescript`.
     * @param resolver a function that will be called to create links for a given symbol name in the registered path.
     *  If the provided name is not contained within the docs, should return `undefined`.
     * @since 0.22.0
     */
    addUnknownSymbolResolver(packageName, resolver) {
        const existing = this.unknownSymbolResolvers.get(packageName);
        if (existing) {
            existing.push(resolver);
        }
        else {
            this.unknownSymbolResolvers.set(packageName, [resolver]);
        }
    }
    /**
     * Marked as internal for now. Using this requires the internal `getSymbol()` method on ReferenceType.
     * Someday that needs to be fixed so that this can be made public. ReferenceTypes really shouldn't store
     * symbols so that we don't need to keep the program around forever.
     * @internal
     */
    attemptExternalResolution(type) {
        if (!type.qualifiedName || !type.package) {
            return;
        }
        const resolvers = this.unknownSymbolResolvers.get(type.package);
        for (const resolver of resolvers || []) {
            const resolved = resolver(type.qualifiedName);
            if (resolved)
                return resolved;
        }
    }
    /**
     * Render the given project reflection to the specified output directory.
     *
     * @param project  The project that should be rendered.
     * @param outputDirectory  The path of the directory the documentation should be rendered to.
     */
    async render(project, outputDirectory) {
        const momento = this.hooks.saveMomento();
        const start = Date.now();
        await (0, highlighter_1.loadHighlighter)(this.lightTheme, this.darkTheme);
        this.application.logger.verbose(`Renderer: Loading highlighter took ${Date.now() - start}ms`);
        if (!this.prepareTheme() ||
            !(await this.prepareOutputDirectory(outputDirectory))) {
            return;
        }
        const output = new events_1.RendererEvent(events_1.RendererEvent.BEGIN, outputDirectory, project);
        output.urls = this.theme.getUrls(project);
        this.trigger(output);
        if (!output.isDefaultPrevented) {
            output.urls.forEach((mapping) => {
                this.renderDocument(output.createPageEvent(mapping));
            });
            this.trigger(events_1.RendererEvent.END, output);
        }
        this.theme = void 0;
        this.hooks.restoreMomento(momento);
    }
    /**
     * Render a single page.
     *
     * @param page An event describing the current page.
     * @return TRUE if the page has been saved to disc, otherwise FALSE.
     */
    renderDocument(page) {
        const momento = this.hooks.saveMomento();
        this.trigger(events_1.PageEvent.BEGIN, page);
        if (page.isDefaultPrevented) {
            this.hooks.restoreMomento(momento);
            return false;
        }
        if (page.model instanceof models_1.Reflection) {
            page.contents = this.theme.render(page);
        }
        else {
            throw new Error("Should be unreachable");
        }
        this.trigger(events_1.PageEvent.END, page);
        this.hooks.restoreMomento(momento);
        if (page.isDefaultPrevented) {
            return false;
        }
        try {
            (0, fs_1.writeFileSync)(page.filename, page.contents);
        }
        catch (error) {
            this.application.logger.error(`Could not write ${page.filename}`);
            return false;
        }
        return true;
    }
    /**
     * Ensure that a theme has been setup.
     *
     * If a the user has set a theme we try to find and load it. If no theme has
     * been specified we load the default theme.
     *
     * @returns TRUE if a theme has been setup, otherwise FALSE.
     */
    prepareTheme() {
        if (!this.theme) {
            const ctor = this.themes.get(this.themeName);
            if (!ctor) {
                this.application.logger.error(`The theme '${this.themeName}' is not defined. The available themes are: ${[
                    ...this.themes.keys(),
                ].join(", ")}`);
                return false;
            }
            else {
                this.theme = new ctor(this);
            }
        }
        return true;
    }
    /**
     * Prepare the output directory. If the directory does not exist, it will be
     * created. If the directory exists, it will be emptied.
     *
     * @param directory  The path to the directory that should be prepared.
     * @returns TRUE if the directory could be prepared, otherwise FALSE.
     */
    async prepareOutputDirectory(directory) {
        if (this.cleanOutputDir) {
            try {
                await (0, fs_1.remove)(directory);
            }
            catch (error) {
                this.application.logger.warn("Could not empty the output directory.");
                return false;
            }
        }
        try {
            fs.mkdirSync(directory, { recursive: true });
        }
        catch (error) {
            this.application.logger.error(`Could not create output directory ${directory}.`);
            return false;
        }
        if (this.githubPages) {
            try {
                const text = "TypeDoc added this file to prevent GitHub Pages from " +
                    "using Jekyll. You can turn off this behavior by setting " +
                    "the `githubPages` option to false.";
                fs.writeFileSync(path.join(directory, ".nojekyll"), text);
            }
            catch (error) {
                this.application.logger.warn("Could not create .nojekyll file.");
                return false;
            }
        }
        if (this.cname) {
            fs.writeFileSync(path.join(directory, "CNAME"), this.cname);
        }
        return true;
    }
};
/** @event */
Renderer.EVENT_BEGIN_PAGE = events_1.PageEvent.BEGIN;
/** @event */
Renderer.EVENT_END_PAGE = events_1.PageEvent.END;
/** @event */
Renderer.EVENT_BEGIN = events_1.RendererEvent.BEGIN;
/** @event */
Renderer.EVENT_END = events_1.RendererEvent.END;
__decorate([
    (0, utils_1.BindOption)("theme")
], Renderer.prototype, "themeName", void 0);
__decorate([
    (0, utils_1.BindOption)("cleanOutputDir")
], Renderer.prototype, "cleanOutputDir", void 0);
__decorate([
    (0, utils_1.BindOption)("cname")
], Renderer.prototype, "cname", void 0);
__decorate([
    (0, utils_1.BindOption)("gaID")
], Renderer.prototype, "gaID", void 0);
__decorate([
    (0, utils_1.BindOption)("gaSite")
], Renderer.prototype, "gaSite", void 0);
__decorate([
    (0, utils_1.BindOption)("githubPages")
], Renderer.prototype, "githubPages", void 0);
__decorate([
    (0, utils_1.BindOption)("hideGenerator")
], Renderer.prototype, "hideGenerator", void 0);
__decorate([
    (0, utils_1.BindOption)("lightHighlightTheme")
], Renderer.prototype, "lightTheme", void 0);
__decorate([
    (0, utils_1.BindOption)("darkHighlightTheme")
], Renderer.prototype, "darkTheme", void 0);
Renderer = __decorate([
    (0, component_1.Component)({ name: "renderer", internal: true, childClass: components_1.RendererComponent })
], Renderer);
exports.Renderer = Renderer;
// HACK: THIS HAS TO STAY DOWN HERE
// if you try to move it up to the top of the file, then you'll run into stuff being used before it has been defined.
require("./plugins");
