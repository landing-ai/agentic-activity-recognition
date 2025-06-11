# 🏃‍♂️  Agentic Activity Recognition · Streamlit Demo App

A self‑contained Streamlit app that lets you:

1. **Upload or live‑stream video** (≤ 30 min per file or continuous RTSP/WebRTC chunks).  
2. Send **natural‑language prompts** to Landing AI’s `POST /tools/activity_recognition` endpoint.  
3. **Step through detected events**—timestamps, bounding boxes, descriptions—inside the browser.  
4. **Experiment with recall vs. precision** via the built‑in **Specificity** slider.  

> **Important**  
> This demo is for **prompt design and quick validation**.  
> For production you’ll likely wrap the same HTTPS calls in a queue / async worker.

---

## Table of Contents
1. [High Level Overview](#1-architecture)
2. [Prerequisites](#2-prerequisites)
3. [Installation (Two Options)](#3-installation)
4. [Configuration](#4-configuration)
5. [Running the App](#5-running-the-app)
6. [Using the App](#6-using-the-app)
7. [Troubleshooting](#8-troubleshooting)
8. [FAQ](#9-faq)
9. [Contributing](#11-contributing)
10. [Contact](#14-contact)

---

## 1. High Level Application Overview <a id="1-architecture"></a>

```text
┌────────────────┐        HTTPS POST            ┌──────────────────────────┐
│ Streamlit App  │  ——►  /tools/activity_recognition  ——►  │ Landing AI API (SaaS) │
│  (Python 3.9+) │        JSON response         └──────────────────────────┘
└────────────────┘
         ▲
         │ temp files / RTSP chunks
         ▼
┌────────────────┐
│ Local Storage  │  (deleted on exit)
└────────────────┘
````

*All computer‑vision heavy lifting—decoding, frame sampling, multimodal reasoning—
occurs behind the scenes for you on Landing AI server side. You only need to take care of sending bytes + prompts and you receive the JSON.*

---

## 2. Prerequisites <a id="2-prerequisites"></a>

| Requirement               | Version                 | Why                                                |
| ------------------------- | ----------------------- | -------------------------------------------------- |
| **Python**                |  3.9 – 3.12             | Tested on 3.11.                                    |
| **Streamlit**             |  1.34+                  | UI layer.                                          |
| **ffmpeg**                | *latest* **(optional)** | Enables webcam / RTSP ingestion.                   |
| **Landing AI account**    | API key (`VA_KEY`)      | Auth header for all requests.                      |
| **macOS, Linux, or WSL2** | —                       | Windows native should work; not officially tested. |

---

## 3. Installation <a id="3-installation"></a>

### Option A · Virtual Environment (recommended)

```bash
git clone https://github.com/your‑org/activity‑rec‑demo.git
cd activity‑rec‑demo/streamlit

python -m venv .venv
source .venv/bin/activate

# Upgrade pip first
pip install --upgrade pip

# Install Python deps
pip install -r requirements.txt
```

### Option B · Docker Compose

```bash
git clone https://github.com/your‑org/activity‑rec‑demo.git
cd activity‑rec‑demo

# Build and run
docker compose up --build
```

*The Dockerfile uses python:3.11‑slim, installs streamlit + dependencies, and exposes port 8501.*

---

## 4. Configuration <a id="4-configuration"></a>

Set your Landing AI key **once per shell**:

```bash
export VA_KEY="sk‑your‑key‑here"
```

> **Never** commit API keys to Git. Use a secrets‑manager (AWS Secrets Manager, HashiCorp Vault, 1Password CLI) in production.

---

## 5. Running the App <a id="5-running-the-app"></a>

```bash
# If using virtualenv
streamlit run app.py
```

Navigate to **[http://localhost:8501](http://localhost:8501)**. The app autorefreshes on code edits.

---

## 6. Using the App <a id="6-using-the-app"></a>

| UI Element             | Detailed Behavior                                                                                                       |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **Upload Video**       | Accepts MP4, MOV, AVI. Max length 30 min. Files saved to OS temp dir and deleted when the session ends.                 |
| **Prompt Input**       | Plain English. Separate multiple activities/entities with `;`. Example: `ball crosses net; ace serve; double fault`.    |
| **Process Audio**      | Checked = fuse sound cues. Helpful to separate visually similar scenes.                                                 |
| **Specificity Slider** | `low` (high recall) → `max` (high precision). Maps 1‑to‑1 with the API’s `specificity` field—no client‑side heuristics. |
| **Run Analysis**       | Calls `process_video()` → uploads file → displays spinner until JSON arrives.                                           |
| **Results Table**      | Timestamp (`start_time`, `end_time`), `location`, `description`, `label` fields displayed via `st.dataframe()`.         |
| **Prev / Next**        | Updates session state and seeks the embedded video to the exact boundary of the selected event.                         |
| **Raw JSON**           | Always visible for copy/paste or downstream scripting.                                                                  |

---

## 7. Troubleshooting <a id="8-troubleshooting"></a>

| Symptom                     | Likely Cause                             | Fix                                                                |
| --------------------------- | ---------------------------------------- | ------------------------------------------------------------------ |
| **`429 Too Many Requests`** | Hitting concurrency limit                | Exponential back‑off; respect `Retry‑After`.                       |
| **File upload hangs**       | File > 5 GB at 1080p                     | Trim file or lower resolution; API hard‑limit at 30 min.           |
| **Blank event list**        | Too strict `specificity` OR vague prompt | Lower specificity or refine prompt (e.g., “orange vest forklift”). |
| **`401 Unauthorized`**      | Missing / wrong key                      | `echo $VA_KEY` and compare with Landing AI console.                |
| **Webcam not visible**      | Browser permission                       | Grant camera access; ensure HTTPS if deploying remotely.           |

---

## 8. FAQ <a id="9-faq"></a>

1. **Does this store video on Landing AI’s servers?**
   Clips are retained only long enough for inference; no long‑term storage.

2. **Is there a size limit?**
   30 min per call; \~5 GB at 1080p. Chunk longer videos client‑side.

3. **Can I run this offline?**
   No. The model is proprietary and hosted; local inference is not supported.

4. **What codecs work?**
   Anything ffmpeg can convert to H.264 inside MP4/MOV/AVI.

---

## 9. Contributing <a id="11-contributing"></a>

```text
Fork ➜ Feature Branch ➜ PR ➜ Code Review ➜ Merge
```

* Run `pre-commit install` to auto‑format with black + isort.
* Add unit tests in `tests/` for new utility functions.


---

## 10. Contact <a id="14-contact"></a>

| Channel       | Handle / URL                                                                                                 |
| ------------- | ------------------------------------------------------------------------------------------------------------ |
| GitHub Issues | [https://github.com/your‑org/activity‑rec‑demo/issues](https://github.com/your‑org/activity‑rec‑demo/issues) |
| Support Email         | [support@landing.ai](mailto:support@landing.ai)                                                      |

---
