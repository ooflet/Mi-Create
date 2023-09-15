import type { DefaultThemeRenderContext } from "../DefaultThemeRenderContext";
import { JSX } from "../../../../utils";
import type { SignatureReflection } from "../../../../models";
export declare const memberSignatureTitle: (context: DefaultThemeRenderContext, props: SignatureReflection, { hideName, arrowStyle }?: {
    hideName?: boolean | undefined;
    arrowStyle?: boolean | undefined;
}) => JSX.Element;
