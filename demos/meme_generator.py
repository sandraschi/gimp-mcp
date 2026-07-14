"""Meme generator: open template → add top text → add bottom text → apply classic滤镜 → export.

Shows text layer creation and composite operations.
"""

STEPS = [
    ("snapshot_before", "Capture blank canvas", "gimp_snapshot_tool", {"max_size": 512}),
    ("add_top_text", "Add top text ('WHEN THE CODE COMPILES')", "gimp_file",
     {"operation": "add_text", "text": "WHEN THE CODE COMPILES",
      "font_size": 48, "color": "white", "position_x": 50, "position_y": 30}),
    ("add_bottom_text", "Add bottom text ('FIRST TRY')", "gimp_file",
     {"operation": "add_text", "text": "FIRST TRY",
      "font_size": 48, "color": "white", "position_x": 50, "position_y": 400}),
    ("add_outline", "Add stroke outline to text layers", "gimp_filter",
     {"operation": "artistic", "filter_type": "outline", "amount": 2}),
    ("snapshot_mid", "Capture text layout", "gimp_snapshot_tool", {"max_size": 512}),
    ("flatten", "Flatten for final export", "gimp_layer", {"operation": "flatten"}),
    ("export", "Export meme", "gimp_file",
     {"operation": "save", "output_path": "output_meme.png"}),
    ("snapshot_after", "Capture final meme", "gimp_snapshot_tool", {"max_size": 512}),
]
DESCRIPTION = "Meme generator: add Impact-style top/bottom text with outline stroke, then export shareable PNG."
