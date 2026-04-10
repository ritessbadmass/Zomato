This folder contained the **legacy** flat `main.py` / `data_loader.py` layout.

The codebase now follows **phase-wise architecture** under `src/restaurant_rec/`. Use:

```bash
cd ..
pip install -e .
uvicorn restaurant_rec.phase4.app:app --reload --host 127.0.0.1 --port 8000
```

Legacy files may remain for reference; new work should target `src/restaurant_rec/`.
