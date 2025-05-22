
# Vision Realizer RIN v2 (Fixed 2025-05-15)

## Setup

```bash
python -m venv rinenv
source rinenv/bin/activate
pip install -r requirements.txt
```

## Running the asynchronous data fetcher

```bash
python infrastructure/data_fetcher.py
```

## Running the bot

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
python application/bot.py
```

## Launching the Streamlit UI

```bash
streamlit run presentation/ui_streamlit/ui.py
```

## Testing

```bash
pip install pytest
pytest
```

## Notes
* All imports of `rin_logger` have been replaced with `infrastructure.file_logger`.
* `infrastructure/data_fetcher.py` is now fully asynchronous using `aiohttp` & `asyncio`.
* Add your API keys and pair lists in `config/market_config.json`.
