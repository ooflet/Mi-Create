"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ReflectionCategory = void 0;
/**
 * A category of reflections.
 *
 * Reflection categories are created by the ´CategoryPlugin´ in the resolving phase
 * of the dispatcher. The main purpose of categories is to be able to more easily
 * render human readable children lists in templates.
 */
class ReflectionCategory {
    /**
     * Create a new ReflectionCategory instance.
     *
     * @param title The title of this category.
     */
    constructor(title) {
        /**
         * All reflections of this category.
         */
        this.children = [];
        this.title = title;
    }
    /**
     * Do all children of this category have a separate document?
     */
    allChildrenHaveOwnDocument() {
        return this.children.every((child) => child.hasOwnDocument);
    }
}
exports.ReflectionCategory = ReflectionCategory;
