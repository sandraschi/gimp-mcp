"""G'MIC art filter pipeline: apply artistic filter → adjust → frame → export.

Demonstrates G'MIC 500+ filter integration with color adjustments.
"""

STEPS = [
    ("snapshot_before", "Capture original", "gimp_snapshot_tool", {"max_size": 512}),
    ("gmic_art", "Apply G'MIC artistic filter (oil painting)", "gimp_gmic",
     {"operation": "apply_named", "filter_name": "Artistic - Oil painting", "category": "Artistic"}),
    ("snapshot_mid", "Capture after G'MIC", "gimp_snapshot_tool", {"max_size": 512}),
    ("adjust_color", "Boost saturation and contrast", "gimp_color",
     {"operation": "brightness_contrast", "brightness": 0.0, "contrast": 0.3}),
    ("add_border", "Add border/frame", "gimp_filter",
     {"operation": "artistic", "filter_type": "border", "size": 20, "color": "#333333"}),
    ("snapshot_after", "Capture framed result", "gimp_snapshot_tool", {"max_size": 512}),
    ("export", "Export artwork", "gimp_file",
     {"operation": "save", "output_path": "output_gmic_art.png"}),
]
DESCRIPTION = "Apply G'MIC artistic filter (oil painting), boost color, add border frame, export artwork."
