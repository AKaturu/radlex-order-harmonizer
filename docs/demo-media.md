# Demo Media

The README demo media is generated from a real CLI demo run against synthetic local procedure names and RadLex Playbook entries.

```bash
python -m pip install -e ".[media]"
python scripts/generate_demo_media.py
```

Generated assets:

- `docs/assets/demo-poster.png`
- `docs/assets/demo.gif`
- `docs/assets/demo.mp4`

The generated procedure names are synthetic. Real deployments should use local order dictionaries approved for the intended workflow.
