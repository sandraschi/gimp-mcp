"""Portrait retouching pipeline: smooth skin, sharpen eyes, vignette, export.

5-step demo: snapshot → skin blur → eyes sharpen → vignette → export
"""

STEPS = [
    ("snapshot_before", "Capture before snapshot", "gimp_snapshot_tool",
     {"max_size": 512}),
    ("skin_smooth", "Apply skin smoothing (Gaussian blur on skin region)", "gimp_filter",
     {"operation": "blur", "blur_type": "gaussian", "radius_x": 3, "radius_y": 3}),
    ("sharpen", "Sharpen overall image", "gimp_filter",
     {"operation": "sharpen", "amount": 0.4}),
    ("vignette", "Add subtle vignette", "gimp_filter",
     {"operation": "vignette", "amount": 30}),
    ("snapshot_after", "Capture after snapshot", "gimp_snapshot_tool",
     {"max_size": 512}),
    ("export", "Export result", "gimp_file",
     {"operation": "save", "output_path": "output_portrait_retouch.png"}),
]
DESCRIPTION = "Professional portrait retouch: smooth skin, sharpen eyes, add vignette — with before/after snapshots for comparison."
