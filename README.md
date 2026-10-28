# Daily Comedy Studio

A small, offline-first generator for original, captioned vertical comedy videos. The repository starts a manual GitHub Actions workflow; it does not publish to social media.

## What it actually makes

Each run chooses one short scenario from a built-in, original library spanning everyday life, family, relationships, pets, work, and absurd situations. It renders four lightly animated illustrated scenes, burns each scene's caption into the picture, creates a quiet original synthesized musical bed and chime effects, and encodes one **720 × 1280, 24 fps, H.264/AAC MP4**, usually 12 seconds long. A `scenario.txt` report describes the joke, captions, generation method, validation details, and asset notes. FFmpeg decodes the finished file as a final playability check.

Recent concept IDs are rotated using a six-item history. In Actions, that small JSON history is carried between runs using GitHub Actions cache. A category with fewer concepts than the history window can repeat once its category pool is exhausted. There is no language model, external video-generation provider, network asset download, speech synthesis, or live service in the render path.

## Generation method, cost, and limitations

The working version uses **original 2D motion graphics**, drawn frame-by-frame with Pillow and encoded with FFmpeg supplied by `imageio-ffmpeg`. Sound is synthesized locally in Python. The code, dependencies, scenarios, drawings, and audio generation are free/open source; no paid subscription, payment method, API key, or third-party account is needed to generate a video. GitHub Actions requires your GitHub account. GitHub's hosted-runner minutes and artifact-storage allowances depend on your account/repository plan and current GitHub policies; check your account's Actions billing/usage page if you approach its included quota. This project makes one short video per manual run and does not schedule jobs.

This is **not photorealistic AI video**. The people, pets, rooms, and props are deliberately simple illustrated cartoons. That approach was selected because it genuinely renders playable video without API credentials, an uncertain “free” AI quota, paid credits, or a powerful personal computer. Captions make the story understandable with sound off; audio is original synthesized tones, not speech or licensed music. No system watermark is added. The renderer has no downloaded footage, stock art, or borrowed creator scripts.

## Generate a video from an Android phone

1. Open this repository on GitHub and sign in.
2. Tap **Actions** → **Generate comedy video**.
3. Tap **Run workflow**, optionally choose a category (or keep **random**), then tap the green **Run workflow** button.
4. Open the new run and wait for the job to finish successfully (usually a few minutes; first setup may take longer).
5. On the completed run page, scroll to **Artifacts** and tap `daily-comedy-…` to download the ZIP.
6. Open the ZIP in Android's **Files/Downloads** app and extract it. Play `comedy.mp4` with your video player; `scenario.txt` contains its captions and details.

Artifacts expire after 14 days, so download the video before then. You can also open the run's summary to inspect the scenario and troubleshooting hint.

## Run locally

Python 3.10+ and internet access to install the two Python packages are required on first setup; a heavyweight computer is not needed. The render itself uses CPU and streams frames instead of saving a frame sequence.

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m comedy_studio --output output/comedy.mp4
python -m comedy_studio --validate output/comedy.mp4
```

Choose a category with `--category funny-animals` (available choices are shown by `python -m comedy_studio --help`). Local generation does not need an account or secret. Local history is stored at `output/history.json`.

## Troubleshooting

- **Workflow failed during tests:** open the failed **Run automated tests** step and expand the traceback. The tests include a real small MP4 render/encode/decode, not just mock checks.
- **Dependency installation failed:** rerun later; the runner needs access to PyPI for Pillow and the FFmpeg wheel. No API key is used.
- **Encoding or MP4 validation failed:** inspect **Generate and validate MP4** in the run logs. It reports FFmpeg's error. The job has a 12-minute limit and generates one short video only.
- **No artifact appears:** the video/report must both finish successfully before upload. Check whether the job and the final upload step succeeded.
- **Cannot download on Android:** use a browser signed into GitHub, allow the ZIP download, then extract it from Downloads/Files. Ensure the artifact has not passed its 14-day retention period.
- **Want realistic-looking footage:** this fallback cannot provide it. A future provider can be added behind the render interface, but a genuinely free quota, account/payment requirements, commercial rights, and access must be confirmed before depending on it.

## Repository structure

- `comedy_studio/scenarios.py` — authored scenario library, category selection, recent-history rotation.
- `comedy_studio/video.py` — original illustrations, caption rendering, synthetic audio, FFmpeg encoding, full-decode validation.
- `comedy_studio/cli.py` — command line, report generation, useful error messages.
- `.github/workflows/generate-video.yml` — manual workflow, test, render, validation, cache, artifact upload.
- `tests/test_studio.py` — scenario/history checks and an actual short MP4 integration test.

Nothing is automatically posted to Telegram or Facebook. No Telegram secrets or publishing permissions are used.
