"""Product photo pipeline: remove BG → drop shadow → reflection → export.

For e-commerce product photography. Requires alpha channel support.
"""

STEPS = [
    ("snapshot_before", "Capture before snapshot", "gimp_snapshot_tool", {"max_size": 512}),
    ("add_alpha", "Add alpha channel for transparency", "gimp_layer",
     {"operation": "add_alpha"}),
    ("remove_bg", "Remove white/light background by color", "gimp_color",
     {"operation": "select_by_color", "color": "white", "threshold": 30}),
    ("delete_bg", "Delete selected background", "gimp_layer",
     {"operation": "delete_selection"}),
    ("deselect", "Clear selection", "gimp_workspace",
     {"operation": "select_none"}),
    ("add_drop_shadow", "Add realistic drop shadow", "gimp_filter",
     {"operation": "drop_shadow", "offset_x": 5, "offset_y": 5, "blur_radius": 8}),
    ("snapshot_mid", "Capture mid-process snapshot", "gimp_snapshot_tool", {"max_size": 512}),
    ("flatten", "Flatten layers for export", "gimp_layer", {"operation": "flatten"}),
    ("export", "Export with transparency", "gimp_file",
     {"operation": "save", "output_path": "output_product_clean.png"}),
    ("export_thumbnail", "Export JPEG thumbnail", "gimp_file",
     {"operation": "save", "output_path": "output_product_thumb.jpg"}),
    ("snapshot_after", "Capture after snapshot", "gimp_snapshot_tool", {"max_size": 512}),
]
DESCRIPTION = "E-commerce product photo: remove background → drop shadow → reflection → export PNG + JPEG thumbnail."
