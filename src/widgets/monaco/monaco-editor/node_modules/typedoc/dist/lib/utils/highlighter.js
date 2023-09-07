"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getStyles = exports.highlight = exports.getSupportedLanguages = exports.isSupportedLanguage = exports.loadHighlighter = void 0;
const assert_1 = require("assert");
const shiki_1 = require("shiki");
const array_1 = require("./array");
const JSX = require("./jsx");
const aliases = new Map();
for (const lang of shiki_1.BUNDLED_LANGUAGES) {
    for (const alias of lang.aliases || []) {
        aliases.set(alias, lang.id);
    }
}
const supportedLanguages = (0, array_1.unique)(["text", ...aliases.keys(), ...shiki_1.BUNDLED_LANGUAGES.map((lang) => lang.id)]).sort();
class DoubleHighlighter {
    constructor(highlighter, light, dark) {
        this.highlighter = highlighter;
        this.light = light;
        this.dark = dark;
        this.schemes = new Map();
    }
    highlight(code, lang) {
        const lightTokens = this.highlighter.codeToThemedTokens(code, lang, this.light, { includeExplanation: false });
        const darkTokens = this.highlighter.codeToThemedTokens(code, lang, this.dark, { includeExplanation: false });
        // If this fails... something went *very* wrong.
        (0, assert_1.ok)(lightTokens.length === darkTokens.length);
        const docEls = [];
        for (let line = 0; line < lightTokens.length; line++) {
            const lightLine = lightTokens[line];
            const darkLine = darkTokens[line];
            // Different themes can have different grammars... so unfortunately we have to deal with different
            // sets of tokens.Example: light_plus and dark_plus tokenize " = " differently in the `schemes`
            // declaration for this file.
            const lineEls = [];
            while (lightLine.length && darkLine.length) {
                // Simple case, same token.
                if (lightLine[0].content === darkLine[0].content) {
                    lineEls.push(JSX.createElement("span", { class: this.getClass(lightLine[0].color, darkLine[0].color) }, lightLine[0].content));
                    lightLine.shift();
                    darkLine.shift();
                    continue;
                }
                if (lightLine[0].content.length < darkLine[0].content.length) {
                    lineEls.push(JSX.createElement("span", { class: this.getClass(lightLine[0].color, darkLine[0].color) }, lightLine[0].content));
                    darkLine[0].content = darkLine[0].content.substr(lightLine[0].content.length);
                    lightLine.shift();
                    continue;
                }
                lineEls.push(JSX.createElement("span", { class: this.getClass(lightLine[0].color, darkLine[0].color) }, darkLine[0].content));
                lightLine[0].content = lightLine[0].content.substr(darkLine[0].content.length);
                darkLine.shift();
            }
            if (line + 1 !== lightTokens.length) {
                lineEls.push(JSX.createElement("br", null));
            }
            docEls.push(lineEls);
        }
        return JSX.renderElement(JSX.createElement(JSX.Fragment, null, docEls));
    }
    getStyles() {
        const style = [":root {"];
        const lightRules = [];
        const darkRules = [];
        let i = 0;
        for (const key of this.schemes.keys()) {
            const [light, dark] = key.split(" | ");
            style.push(`    --light-hl-${i}: ${light};`);
            style.push(`    --dark-hl-${i}: ${dark};`);
            lightRules.push(`    --hl-${i}: var(--light-hl-${i});`);
            darkRules.push(`    --hl-${i}: var(--dark-hl-${i});`);
            i++;
        }
        // GH#1836, our page background is white, but it would be nice to be able to see
        // a difference between the code blocks and the background of the page. There's
        // probably a better solution to this... revisit once #1794 is merged.
        let lightBackground = this.highlighter.getTheme(this.light).bg;
        if (isWhite(lightBackground)) {
            lightBackground = "#F5F5F5";
        }
        style.push(`    --light-code-background: ${lightBackground};`);
        style.push(`    --dark-code-background: ${this.highlighter.getTheme(this.dark).bg};`);
        lightRules.push(`    --code-background: var(--light-code-background);`);
        darkRules.push(`    --code-background: var(--dark-code-background);`);
        style.push("}", "");
        style.push("@media (prefers-color-scheme: light) { :root {");
        style.push(...lightRules);
        style.push("} }", "");
        style.push("@media (prefers-color-scheme: dark) { :root {");
        style.push(...darkRules);
        style.push("} }", "");
        style.push("body.light {");
        style.push(...lightRules);
        style.push("}", "");
        style.push("body.dark {");
        style.push(...darkRules);
        style.push("}", "");
        for (i = 0; i < this.schemes.size; i++) {
            style.push(`.hl-${i} { color: var(--hl-${i}); }`);
        }
        style.push("pre, code { background: var(--code-background); }", "");
        return style.join("\n");
    }
    getClass(lightColor, darkColor) {
        const key = `${lightColor} | ${darkColor}`;
        let scheme = this.schemes.get(key);
        if (scheme == null) {
            scheme = `hl-${this.schemes.size}`;
            this.schemes.set(key, scheme);
        }
        return scheme;
    }
}
let highlighter;
async function loadHighlighter(lightTheme, darkTheme) {
    if (highlighter)
        return;
    const hl = await (0, shiki_1.getHighlighter)({ themes: [lightTheme, darkTheme] });
    highlighter = new DoubleHighlighter(hl, lightTheme, darkTheme);
}
exports.loadHighlighter = loadHighlighter;
function isSupportedLanguage(lang) {
    return getSupportedLanguages().includes(lang);
}
exports.isSupportedLanguage = isSupportedLanguage;
function getSupportedLanguages() {
    return supportedLanguages;
}
exports.getSupportedLanguages = getSupportedLanguages;
function highlight(code, lang) {
    var _a;
    (0, assert_1.ok)(highlighter, "Tried to highlight with an uninitialized highlighter");
    if (!isSupportedLanguage(lang)) {
        return code;
    }
    if (lang === "text") {
        return JSX.renderElement(JSX.createElement(JSX.Fragment, null, code));
    }
    return highlighter.highlight(code, (_a = aliases.get(lang)) !== null && _a !== void 0 ? _a : lang);
}
exports.highlight = highlight;
function getStyles() {
    (0, assert_1.ok)(highlighter, "Tried to highlight with an uninitialized highlighter");
    return highlighter.getStyles();
}
exports.getStyles = getStyles;
function isWhite(color) {
    const colors = new Set(color.toLowerCase().replace(/[^a-f0-9]/g, ""));
    return colors.size === 1 && colors.has("f");
}
