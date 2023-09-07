"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SourceDirectory = void 0;
const array_1 = require("../../utils/array");
/**
 * Exposes information about a directory containing source files.
 *
 * One my access the root directory of a project through the {@link ProjectReflection.directory}
 * property. Traverse through directories by utilizing the {@link SourceDirectory.parent} or
 * {@link SourceDirectory.directories} properties.
 */
class SourceDirectory {
    /**
     * Create a new SourceDirectory instance.
     *
     * @param name  The new of directory.
     * @param parent  The parent directory instance.
     */
    constructor(name, parent) {
        /**
         * A list of all subdirectories.
         */
        this.directories = {};
        /**
         * A list of all files in this directory.
         */
        this.files = [];
        if (name && parent) {
            this.name = name;
            this.dirName = (parent.dirName ? parent.dirName + "/" : "") + name;
            this.parent = parent;
        }
    }
    /**
     * Return a string describing this directory and its contents.
     *
     * @param indent  Used internally for indention.
     * @returns A string representing this directory and all of its children.
     */
    toString(indent = "") {
        let res = indent + this.name;
        for (const dir of Object.values(this.directories)) {
            res += "\n" + dir.toString(indent + "  ");
        }
        this.files.forEach((file) => {
            res += "\n" + indent + "  " + file.fileName;
        });
        return res;
    }
    /**
     * Return a list of all reflections exposed by the files within this directory.
     *
     * @returns An aggregated list of all {@link DeclarationReflection} defined in the
     * files of this directory.
     */
    getAllReflections() {
        return (0, array_1.flatMap)(this.files, (file) => file.reflections);
    }
}
exports.SourceDirectory = SourceDirectory;
