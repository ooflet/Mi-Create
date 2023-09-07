"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SourceFile = void 0;
const Path = require("path");
/**
 * Exposes information about a source file.
 *
 * One may access a list of all source files through the {@link ProjectReflection.files} property or as
 * a tree structure through the {@link ProjectReflection.directory} property.
 *
 * Furthermore each reflection carries references to the related SourceFile with their
 * {@link DeclarationReflection.sources} property. It is an array of of {@link SourceReference} instances
 * containing the reference in their {@link SourceReference.file} field.
 */
class SourceFile {
    /**
     * Create a new SourceFile instance.
     *
     * @param fullFileName  The full file name.
     */
    constructor(fullFileName) {
        /**
         * A list of all reflections that are declared in this file.
         */
        this.reflections = [];
        this.fileName = fullFileName;
        this.fullFileName = fullFileName;
        this.name = Path.basename(fullFileName);
    }
}
exports.SourceFile = SourceFile;
