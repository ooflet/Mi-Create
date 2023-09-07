"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.SourceLinkPlugin = exports.Repository = void 0;
const Path = require("path");
const child_process_1 = require("child_process");
const components_1 = require("../components");
const base_path_1 = require("../utils/base-path");
const converter_1 = require("../converter");
const utils_1 = require("../../utils");
const models_1 = require("../../models");
const TEN_MEGABYTES = 1024 * 10000;
function git(...args) {
    return (0, child_process_1.spawnSync)("git", args, {
        encoding: "utf-8",
        windowsHide: true,
        maxBuffer: TEN_MEGABYTES,
    });
}
/**
 * Stores data of a repository.
 */
class Repository {
    /**
     * Create a new Repository instance.
     *
     * @param path  The root path of the repository.
     */
    constructor(path, gitRevision, repoLinks) {
        /**
         * A list of all files tracked by the repository.
         */
        this.files = [];
        /**
         * The hostname for this GitHub/Bitbucket/.etc project.
         *
         * Defaults to: `github.com` (for normal, public GitHub instance projects)
         *
         * Can be the hostname for an enterprise version of GitHub, e.g. `github.acme.com`
         * (if found as a match in the list of git remotes).
         */
        this.hostname = "github.com";
        /**
         * Whether this is a GitHub, Bitbucket, or other type of repository.
         */
        this.type = models_1.RepositoryType.GitHub;
        this.path = path;
        this.branch = gitRevision || "master";
        for (let i = 0, c = repoLinks.length; i < c; i++) {
            let match = /(github(?:\.[a-z]+)*\.[a-z]{2,})[:/]([^/]+)\/(.*)/.exec(repoLinks[i]);
            // Github Enterprise
            if (!match) {
                match = /(\w+\.githubprivate.com)[:/]([^/]+)\/(.*)/.exec(repoLinks[i]);
            }
            if (!match) {
                match = /(bitbucket.org)[:/]([^/]+)\/(.*)/.exec(repoLinks[i]);
            }
            if (!match) {
                match = /(gitlab.com)[:/]([^/]+)\/(.*)/.exec(repoLinks[i]);
            }
            if (match) {
                this.hostname = match[1];
                this.user = match[2];
                this.project = match[3];
                if (this.project.substr(-4) === ".git") {
                    this.project = this.project.substr(0, this.project.length - 4);
                }
                break;
            }
        }
        if (this.hostname.includes("bitbucket.org")) {
            this.type = models_1.RepositoryType.Bitbucket;
        }
        else if (this.hostname.includes("gitlab.com")) {
            this.type = models_1.RepositoryType.GitLab;
        }
        else {
            this.type = models_1.RepositoryType.GitHub;
        }
        let out = git("-C", path, "ls-files");
        if (out.status === 0) {
            out.stdout.split("\n").forEach((file) => {
                if (file !== "") {
                    this.files.push(base_path_1.BasePath.normalize(path + "/" + file));
                }
            });
        }
        if (!gitRevision) {
            out = git("-C", path, "rev-parse", "--short", "HEAD");
            if (out.status === 0) {
                this.branch = out.stdout.replace("\n", "");
            }
        }
    }
    /**
     * Check whether the given file is tracked by this repository.
     *
     * @param fileName  The name of the file to test for.
     * @returns TRUE when the file is part of the repository, otherwise FALSE.
     */
    contains(fileName) {
        return this.files.includes(fileName);
    }
    /**
     * Get the URL of the given file on GitHub or Bitbucket.
     *
     * @param fileName  The file whose URL should be determined.
     * @returns A URL pointing to the web preview of the given file or undefined.
     */
    getURL(fileName) {
        if (!this.user || !this.project || !this.contains(fileName)) {
            return;
        }
        return [
            `https://${this.hostname}`,
            this.user,
            this.project,
            this.type === models_1.RepositoryType.GitLab ? "-" : undefined,
            this.type === models_1.RepositoryType.Bitbucket ? "src" : "blob",
            this.branch,
            fileName.substr(this.path.length + 1),
        ]
            .filter((s) => !!s)
            .join("/");
    }
    /**
     * Try to create a new repository instance.
     *
     * Checks whether the given path is the root of a valid repository and if so
     * creates a new instance of {@link Repository}.
     *
     * @param path  The potential repository root.
     * @returns A new instance of {@link Repository} or undefined.
     */
    static tryCreateRepository(path, gitRevision, gitRemote) {
        const out = git("-C", path, "rev-parse", "--show-toplevel");
        const remotesOutput = git("-C", path, "remote", "get-url", gitRemote);
        if (out.status !== 0 || remotesOutput.status !== 0) {
            return;
        }
        return new Repository(base_path_1.BasePath.normalize(out.stdout.replace("\n", "")), gitRevision, remotesOutput.stdout.split("\n"));
    }
    static getLineNumberAnchor(lineNumber, repositoryType) {
        switch (repositoryType) {
            default:
            case models_1.RepositoryType.GitHub:
            case models_1.RepositoryType.GitLab:
                return "L" + lineNumber;
            case models_1.RepositoryType.Bitbucket:
                return "lines-" + lineNumber;
        }
    }
}
exports.Repository = Repository;
/**
 * A handler that watches for repositories with GitHub origin and links
 * their source files to the related GitHub pages.
 */
let SourceLinkPlugin = class SourceLinkPlugin extends components_1.ConverterComponent {
    constructor() {
        super(...arguments);
        /**
         * List of known repositories.
         */
        this.repositories = {};
        /**
         * List of paths known to be not under git control.
         */
        this.ignoredPaths = [];
    }
    /**
     * Create a new GitHubHandler instance.
     *
     * @param converter  The converter this plugin should be attached to.
     */
    initialize() {
        if (git("--version").status === 0) {
            this.listenTo(this.owner, converter_1.Converter.EVENT_RESOLVE_END, this.onEndResolve);
        }
    }
    /**
     * Check whether the given file is placed inside a repository.
     *
     * @param fileName  The name of the file a repository should be looked for.
     * @returns The found repository info or undefined.
     */
    getRepository(fileName) {
        // Check for known non-repositories
        const dirName = Path.dirname(fileName);
        for (let i = 0, c = this.ignoredPaths.length; i < c; i++) {
            if (this.ignoredPaths[i] === dirName) {
                return;
            }
        }
        // Check for known repositories
        for (const path of Object.keys(this.repositories)) {
            if (fileName.substr(0, path.length).toLowerCase() === path) {
                return this.repositories[path];
            }
        }
        // Try to create a new repository
        const repository = Repository.tryCreateRepository(dirName, this.gitRevision, this.gitRemote);
        if (repository) {
            this.repositories[repository.path.toLowerCase()] = repository;
            return repository;
        }
        // No repository found, add path to ignored paths
        const segments = dirName.split("/");
        for (let i = segments.length; i > 0; i--) {
            this.ignoredPaths.push(segments.slice(0, i).join("/"));
        }
    }
    /**
     * Triggered when the converter has finished resolving a project.
     *
     * @param context  The context object describing the current state the converter is in.
     */
    onEndResolve(context) {
        const project = context.project;
        project.files.forEach((sourceFile) => {
            const repository = this.getRepository(sourceFile.fullFileName);
            if (repository) {
                sourceFile.url = repository.getURL(sourceFile.fullFileName);
                sourceFile.repositoryType = repository.type;
            }
        });
        for (const key in project.reflections) {
            const reflection = project.reflections[key];
            if (reflection.sources) {
                reflection.sources.forEach((source) => {
                    if (source.file && source.file.url) {
                        source.url =
                            source.file.url +
                                "#" +
                                Repository.getLineNumberAnchor(source.line, source.file.repositoryType);
                    }
                });
            }
        }
    }
};
__decorate([
    (0, utils_1.BindOption)("gitRevision")
], SourceLinkPlugin.prototype, "gitRevision", void 0);
__decorate([
    (0, utils_1.BindOption)("gitRemote")
], SourceLinkPlugin.prototype, "gitRemote", void 0);
SourceLinkPlugin = __decorate([
    (0, components_1.Component)({ name: "source-link" })
], SourceLinkPlugin);
exports.SourceLinkPlugin = SourceLinkPlugin;
