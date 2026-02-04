# StevenAiDigest Visual Templates

This folder contains the **starter visual system** for StevenAiDigest.

## Outputs

- `templates/A_chart_slide_template.png`
  - 1920×1080 chart slide (A type)
- `templates/B_editorial_photo_template.png`
  - 1080×1080 editorial photo treatment (B type)
- `templates/C_memo_video_template.mp4`
  - 15s 1080×1080 modern matte gradient video (C type)
- `templates/C_memo_video_template.cmd`
  - Regenerates the MP4 via ffmpeg

## House style (locked)

- Modern editorial matte with subtle gradients
- No tacky stock motifs
- No reposted media without rights

## How to regenerate

From repo root on Windows:

```bat
python assets\visuals\templates\generate_templates.py
call assets\visuals\templates\C_memo_video_template.cmd
```

## How to use

- Replace placeholder headline and source text before posting.
- For real chart slides, export your chart as a transparent PNG and place it inside the chart container.
- For editorial photo treatments, only use licensed imagery (Canva Pro, owned photos, or paid editorial sources).
