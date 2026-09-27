# Gemini TTS on PR0TA

Read this when the resolved `dialogue_model` is a Gemini TTS route
(`google/gemini-3.8-flash-tts`, `google/gemini-3.8-flash-lite-tts`,
`fal-ai/gemini-3.1-flash-tts`, `gemini-3.1-flash-tts-preview`,
`gemini-2.5-flash-preview-tts`, `gemini-2.5-pro-preview-tts`). Prompt order for
the family is in `pr0ta-prompting` → `reference/model-modality-guides.md` →
"Gemini TTS Models"; this file covers PR0TA's request fields and how to use
them. Confirm current fields with `models_get_defaults(model_id)`.

## Request fields

On `generation_submit` with `generator: "audio"`, `mode: "txt_to_speech"`,
Gemini routes accept, besides `text`:

| Field | Use |
|---|---|
| `voice` | A Gemini prebuilt voice name. From `voices_list(provider: "google")`, copy `selection.voice_settings.voice`. |
| `style_instructions` | Tone, pace, accent, emotion, mic feel, audience. Keep direction here, not in the transcript. |
| `speakers` | Multi-speaker configuration; each speaker's name must exactly match the labels used in the text. The Google-direct routes take at most two speakers. |
| `language_code` | Locale such as `en-US` or `fr-FR`. Only on the Fal Gemini 3.1 Flash TTS route (`fal-ai/gemini-3.1-flash-tts`). |
| `temperature` | Variation between takes. Only on the Fal Gemini 3.1 Flash TTS route. |
| `output_format` | Audio format. Only on the Fal Gemini 3.1 Flash TTS route. |

The fields other Gemini TTS versions take can differ; set `language_code`,
`temperature` or `output_format` only when the resolved model's
`models_get_defaults` lists them.

## Gemini 3.8 Flash and Flash Lite TTS

The 3.8 routes (`google/gemini-3.8-flash-tts`, `google/gemini-3.8-flash-lite-tts`)
take a smaller field set:

- Single speaker: `text` plus `voice`.
- Dialogue: `speakers` with exactly two entries, each `{speaker_id, voice}`
  with distinct aliases. Write each line of `text` as `speaker_id: line`;
  PR0TA turns those lines into ordered turns. Any other speaker count is
  rejected, so split larger scenes into two-person passes.
- `style_instructions` works as above. Inline vocal events such as `<laugh>`
  and `<sigh>` go in the transcript where they happen.
- No `language_code`, `temperature` or `output_format`: write the transcript in
  the target language. Output is WAV.
- Input is limited to 8,192 tokens; billing counts the spoken text only, so
  direction in `style_instructions` costs nothing extra.

## Writing the text

Separate direction from the words. A narration request:

```json
{
  "project_id": "<project>",
  "request": {
    "generator": "audio",
    "mode": "txt_to_speech",
    "model": "<model_id from models_preferred>",
    "text": "AUDIO PROFILE\nWarm documentary narrator, close-mic studio recording, natural conversational delivery, no music, no sound effects.\n\nSCENE\nA 45-second voiceover explaining a scientific idea to a curious general audience.\n\nDIRECTOR'S NOTES\nPace around 145 words per minute. Authority without sounding like an announcer. Pause briefly after the first sentence. Lightly emphasize the named concepts.\n\nTRANSCRIPT\nThe city had changed since I last saw it, but then again, so had I.",
    "voice": "<selection.voice_settings.voice>",
    "style_instructions": "Warm, reflective, measured, never announcer-like.",
    "language_code": "en-US"
  }
}
```

- Give narration an audio profile and scene before the transcript; punctuation
  alone does not set pacing.
- For dialogue, label every line with a speaker name that matches `speakers`.
- For long narration, split on paragraph or scene boundaries and reuse the same
  profile, notes, voice and `style_instructions` in every part.
- Write the transcript in the target language; on the Fal Gemini 3.1 Flash
  TTS route also set `language_code`. The example above targets that route;
  drop `language_code` for routes that do not list it.
- Choose a voice whose natural character fits the performance; direction
  shifts a voice, it does not replace it.
- Listen to the take and read its transcript. Regenerate when names, acronyms,
  years or emphasis land wrong.
