import type { RendererHooks } from "../..";
import type { ReferenceType, Reflection } from "../../../models";
import type { Options } from "../../../utils";
import type { DefaultTheme } from "./DefaultTheme";
export declare class DefaultThemeRenderContext {
    private theme;
    options: Options;
    constructor(theme: DefaultTheme, options: Options);
    hook: (name: keyof RendererHooks) => import("../../../utils/jsx.elements").JsxElement[];
    /** Avoid this in favor of urlTo if possible */
    relativeURL: (url: string | undefined) => string | undefined;
    urlTo: (reflection: Reflection) => string | undefined;
    markdown: (md: string | undefined) => string;
    attemptExternalResolution: (type: ReferenceType) => string | undefined;
    reflectionTemplate: (props: import("../..").PageEvent<import("../../../models").ContainerReflection>) => import("../../../utils/jsx.elements").JsxElement;
    indexTemplate: (props: import("../..").PageEvent<import("../../../models").ProjectReflection>) => import("../../../utils/jsx.elements").JsxElement;
    defaultLayout: (props: import("../..").PageEvent<Reflection>) => import("../../../utils/jsx.elements").JsxElement;
    analytics: () => import("../../../utils/jsx.elements").JsxElement | undefined;
    breadcrumb: (props: Reflection) => import("../../../utils/jsx.elements").JsxElement | undefined;
    comment: (props: Reflection) => import("../../../utils/jsx.elements").JsxElement | undefined;
    footer: (props: import("../..").PageEvent<Reflection>) => import("../../../utils/jsx.elements").JsxElement;
    header: (props: import("../..").PageEvent<Reflection>) => import("../../../utils/jsx.elements").JsxElement;
    hierarchy: (props: import("../../../models").DeclarationHierarchy) => import("../../../utils/jsx.elements").JsxElement;
    index: (props: import("../../../models").ContainerReflection) => import("../../../utils/jsx.elements").JsxElement | undefined;
    member: (props: import("../../../models").DeclarationReflection) => import("../../../utils/jsx.elements").JsxElement;
    memberDeclaration: (props: import("../../../models").DeclarationReflection) => import("../../../utils/jsx.elements").JsxElement;
    memberGetterSetter: (props: import("../../../models").DeclarationReflection) => import("../../../utils/jsx.elements").JsxElement;
    memberReference: (props: import("../../../models").ReferenceReflection) => import("../../../utils/jsx.elements").JsxElement;
    memberSignatureBody: (r_0: import("../../../models").SignatureReflection, r_1?: {
        hideSources?: boolean | undefined;
    } | undefined) => import("../../../utils/jsx.elements").JsxElement;
    memberSignatureTitle: (r_0: import("../../../models").SignatureReflection, r_1?: {
        hideName?: boolean | undefined;
        arrowStyle?: boolean | undefined;
    } | undefined) => import("../../../utils/jsx.elements").JsxElement;
    memberSignatures: (props: import("../../../models").DeclarationReflection) => import("../../../utils/jsx.elements").JsxElement;
    memberSources: (props: import("../../../models").DeclarationReflection | import("../../../models").SignatureReflection) => import("../../../utils/jsx.elements").JsxElement;
    members: (props: import("../../../models").ContainerReflection) => import("../../../utils/jsx.elements").JsxElement;
    membersGroup: (group: import("../../../models").ReflectionGroup) => import("../../../utils/jsx.elements").JsxElement;
    navigation: (props: import("../..").PageEvent<Reflection>) => import("../../../utils/jsx.elements").JsxElement;
    parameter: (props: import("../../../models").DeclarationReflection) => import("../../../utils/jsx.elements").JsxElement;
    type: (type: import("../../../models").Type | undefined) => import("../../../utils/jsx.elements").JsxElement;
    typeAndParent: (props: import("../../../models").Type) => import("../../../utils/jsx.elements").JsxElement;
    typeParameters: (typeParameters: import("../../../models").TypeParameterReflection[]) => import("../../../utils/jsx.elements").JsxElement;
}
