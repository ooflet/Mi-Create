"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.MarkdownEvent = exports.PageEvent = exports.RendererEvent = void 0;
const Path = require("path");
const events_1 = require("../utils/events");
/**
 * An event emitted by the {@link Renderer} class at the very beginning and
 * ending of the entire rendering process.
 *
 * @see {@link Renderer.EVENT_BEGIN}
 * @see {@link Renderer.EVENT_END}
 */
class RendererEvent extends events_1.Event {
    constructor(name, outputDirectory, project) {
        super(name);
        this.outputDirectory = outputDirectory;
        this.project = project;
    }
    /**
     * Create an {@link PageEvent} event based on this event and the given url mapping.
     *
     * @internal
     * @param mapping  The mapping that defines the generated {@link PageEvent} state.
     * @returns A newly created {@link PageEvent} instance.
     */
    createPageEvent(mapping) {
        const event = new PageEvent(PageEvent.BEGIN);
        event.project = this.project;
        event.url = mapping.url;
        event.model = mapping.model;
        event.template = mapping.template;
        event.filename = Path.join(this.outputDirectory, mapping.url);
        return event;
    }
}
exports.RendererEvent = RendererEvent;
/**
 * Triggered before the renderer starts rendering a project.
 * @event
 */
RendererEvent.BEGIN = "beginRender";
/**
 * Triggered after the renderer has written all documents.
 * @event
 */
RendererEvent.END = "endRender";
/**
 * An event emitted by the {@link Renderer} class before and after the
 * markup of a page is rendered.
 *
 * @see {@link Renderer.EVENT_BEGIN_PAGE}
 * @see {@link Renderer.EVENT_END_PAGE}
 */
class PageEvent extends events_1.Event {
}
exports.PageEvent = PageEvent;
/**
 * Triggered before a document will be rendered.
 * @event
 */
PageEvent.BEGIN = "beginPage";
/**
 * Triggered after a document has been rendered, just before it is written to disc.
 * @event
 */
PageEvent.END = "endPage";
/**
 * An event emitted by the {@link MarkedPlugin} on the {@link Renderer} after a chunk of
 * markdown has been processed. Allows other plugins to manipulate the result.
 *
 * @see {@link MarkedPlugin.EVENT_PARSE_MARKDOWN}
 */
class MarkdownEvent extends events_1.Event {
    constructor(name, originalText, parsedText) {
        super(name);
        this.originalText = originalText;
        this.parsedText = parsedText;
    }
}
exports.MarkdownEvent = MarkdownEvent;
/**
 * Triggered on the renderer when this plugin parses a markdown string.
 * @event
 */
MarkdownEvent.PARSE = "parseMarkdown";
