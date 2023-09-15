import { CommentTag } from "../../../models";
import { SerializerComponent } from "../../components";
import type { CommentTag as JSONCommentTag } from "../../schema";
export declare class CommentTagSerializer extends SerializerComponent<CommentTag> {
    static PRIORITY: number;
    /**
     * Filter for instances of {@link CommentTag}
     */
    serializeGroup(instance: unknown): boolean;
    supports(_t: unknown): boolean;
    toObject(tag: CommentTag, obj?: Partial<JSONCommentTag>): JSONCommentTag;
}
