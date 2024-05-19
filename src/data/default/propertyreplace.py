propertyIds = {
    "@Alignment": "num_alignment",
    "@Alpha": "widget_alpha",
    "@Background_ImageName": "widget_background_bitmap",
    "@BgImage_rotate_xc": "analog_bg_anchor_x",
    "@BgImage_rotate_yc": "analog_bg_anchor_y",
    "@Bitmap": "widget_bitmap",
    "@BitmapList": "widget_bitmaplist",
    "@Blanking": "num_hide_zeros",
    "@Butt_cap_ending_style_En": "arc_rounded_caps",
    "@DefaultIndex": "imagelist_default_index",
    "@Digits": "num_digits",
    "@EndAngle": "arc_end_angle",
    "@Foreground_ImageName": "arc_image",
    "@Height": "widget_height",
    "@HourHand_ImageName": "analog_hour_image",
    "@HourImage_rotate_xc": "analog_hour_anchor_x",
    "@HourImage_rotate_yc": "analog_hour_anchor_y",
    "@HourHandCorrection_En": "analog_hour_smooth_motion",
    "@Index_Src": "imagelist_source",
    "@Line_Width": "arc_thickness",
    "@MinuteHand_Image": "analog_minute_image",
    "@MinuteImage_rotate_xc": "analog_minute_anchor_x",
    "@MinuteImage_rotate_yc": "analog_minute_anchor_y",
    "@MinuteHandCorrection_En": "analog_minute_smooth_motion",
    "@Name": "widget_name",
    "@Radius": "arc_radius",
    "@Range_Max": "arc_max_value",
    "@Range_Max_Src": "arc_max_value_source",
    "@Range_Min": "arc_min_value",
    "@Range_MinStep": "arc_min_step_value",
    "@Range_Step": "arc_step_value",
    "@Range_Val_Src": "arc_source",
    "@Rotate_xc": "arc_pos_x",
    "@Rotate_yc": "arc_pos_y",
    "@SecondHand_Image": "analog_second_image",
    "@SecondImage_rotate_xc": "analog_second_anchor_x",
    "@SecondImage_rotate_yc": "analog_second_anchor_y",
    "@Shape": "widget_type",
    "@Spacing": "num_spacing",
    "@StartAngle": "arc_start_angle",
    "@Value_Src": "num_source",
    "@Visible_Src": "widget_visiblity_source",
    "@Width": "widget_size_width",
    "@X": "widget_pos_x",
    "@Y": "widget_pos_y",
    "WidgetType": "WidgetType"
}

with open("defaultItems.json", "r+") as file:
    text = file.read()

    for item in propertyIds:
        text = text.replace(item, propertyIds[item])

    file.write(text)