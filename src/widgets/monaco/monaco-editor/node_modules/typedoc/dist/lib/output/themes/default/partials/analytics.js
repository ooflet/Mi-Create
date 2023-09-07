"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.analytics = void 0;
const utils_1 = require("../../../../utils");
function analytics(context) {
    const gaID = context.options.getValue("gaID");
    const gaSite = context.options.getValue("gaSite");
    if (!gaID)
        return;
    const script = `
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
    (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
        m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','//www.google-analytics.com/analytics.js','ga');
ga('create', '${gaID}', '${gaSite}');
ga('send', 'pageview');
`.trim();
    return (utils_1.JSX.createElement("script", null,
        utils_1.JSX.createElement(utils_1.JSX.Raw, { html: script })));
}
exports.analytics = analytics;
