# Base Algae Sound Experiment

Python research workspace for an algae sound-frequency experiment. The project includes one script for running timed tone exposure in Microsoft Edge and one script for plotting measured turbidity/lux data.

## Project Structure

- `algae_sound_experiment_edge.py`: automates a browser tone generator and logs exposure sessions.
- `graph.py`: plots grouped algae turbidity/lux measurements with error bars.
- `algae_sound_experiment_log.csv`: logged experiment sessions.
- `Base.pptx`, `EEC-33.pdf`, and the included journal PDF: reference/presentation materials.

## Setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

On Windows, use `.venv\Scripts\python.exe`.

## Run Tone Exposure

```bash
.venv/bin/python algae_sound_experiment_edge.py
```

Important runtime notes:

- The script uses Microsoft Edge and Selenium.
- Windows-only volume control uses `pycaw` and `comtypes`.
- `TEST_MODE = True` currently runs short 10-second exposures; set it to `False` for the full configured duration.

## Plot Results

```bash
.venv/bin/python graph.py
```

## Notes

- The experiment script opens an external tone-generator website.
- Logged CSV data and reference documents are kept because they are part of the research workspace.
- Local virtual environments and matplotlib caches should stay out of git.
