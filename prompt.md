# MoneyPrinter — Time-travel dinosaur warning meme

영어권 wojak-vs-chad 짤("타임머신을 탄 평범한 사람들 / 타임머신을 탄 나")의 영상화.
한국 짤이 영감, 결과물은 100% 영어 internet meme deadpan.

---

## 폼에 넣을 값

| 필드                  | 값                                                    |
| ------------------- | ---------------------------------------------------- |
| `videoSubject`      | 아래 **VIDEO SUBJECT** 한 줄 통째                          |
| `customPrompt`      | 아래 **CUSTOM PROMPT** 코드블록 통째                         |
| `voice`             | `en_male_narration` (Effects → Narrator. 무조건 이거)     |
| `paragraphNumber`   | `1` — 절대 변경 금지. 5문장 한 덩어리로 잠겨 있음                     |
| `useMusic`          | `true` — `Songs/vastness_andrew_ev.mp3` 사용           |
| `aiBrollToggle`     | `true` — Mac M-series 전용. "Laramidia" 등 Pexels 빵꾸 메움 |
| `subtitlesPosition` | `center,bottom`                                      |
| `color`             | `#FFFF00`                                            |
| `threads`           | `2` — Mac은 VideoToolbox 자동, 이 값 무시됨                  |

---

## VIDEO SUBJECT

While ordinary people use time travel to meet a lost grandmother or hug a loved one, one man treats it as an extinction-event response protocol — arriving in southern Laramidia to brief the dinosaurs on the incoming Chicxulub asteroid, the coming ice age, and the small mammals that will soon raid their nests

---

## CUSTOM PROMPT

```
You are writing a YouTube Shorts narration script in PLAIN MODERN ENGLISH
(American / neutral, NOT British), delivered by the TikTok "Narrator"
text-to-speech voice. The voice is calm, flat, slightly bored — the exact
deadpan TTS used in countless internet memes where a robotic voice
describes something absurd as if reading a grocery list. Treat the absurd
premise with complete sincerity, but flat. NOT BBC Earth, NOT Attenborough,
NOT documentary gravitas.

# OUTPUT FORMAT (STRICT — Ollama violates these unless ENFORCED)
- Output ONLY the narration text. Nothing else.
- NO preamble. Forbidden openers include but are not limited to:
  "Here is the script", "Here is the new version", "Here is your script",
  "Sure, here's", "Below is", "I've written", "Let me give you".
- NO closing remark, summary, commentary, or "Hope this helps" after the script.
- NO markdown, NO code fences, NO headings, NO quotation marks wrapping
  the whole thing.
- The very first character of your output is the first letter of sentence 1.
  The very last character is the full stop closing sentence 5. Nothing else
  before or after.

# Premise (THIS IS THE WHOLE JOKE — read carefully)
This is a side-by-side meme. The format is:
   Top half: ordinary people use time travel for emotional reasons —
             meeting a long-dead grandmother, hugging a lost loved one.
   Bottom half: this one man uses time travel as an extinction-event
                response protocol, briefing the dinosaurs about the
                Chicxulub asteroid.

The contrast — sentimental tourism vs. apocalyptic project management —
IS the joke. The man briefs the dinosaurs like a senior project manager
reading off a risk register. The dinosaur replies like a calm neighbor
who already knows.

# Tone
Deadpan. Plain words. Short sentences. Never wink at the camera. Never
lampshade the joke. The comedy lives in the contrast and the dinosaur's
calm — NOT in narrator delivery. Absolutely no humour in delivery. No
ironic adjectives. No exclamation marks.

# Structure (write exactly 5 sentences, in this order)
1. EMOTIONAL SETUP — ONE sentence covering what ordinary people do with
   time travel: meet a grandmother for the first time, or hug a loved
   one they lost too soon. Warm, sentimental, plainly worded.
2. PIVOT — the THESIS. Direct, bureaucratic. State that one man treats
   time travel as an extinction-event response protocol. This sentence
   IS the punchline of the contrast.
3. BRIEFING 1 — Roughly 66 million years ago, he arrives in southern
   LARAMIDIA and explains that an asteroid will strike the NORTHEAST
   of the YUCATÁN PENINSULA. Name both place names verbatim.
4. BRIEFING 2 — He will personally attempt to deflect it, but warns
   that the ICE AGE will collapse PLANT YIELDS, and SMALL MAMMALS will
   raid TYRANNOSAUR NESTS for eggs. Clinical, like a project risk register.
5. DINOSAUR REACTION — One sentence. A nearby tyrannosaur listens, then
   replies with ONE short quoted line that contains both a thank-you AND
   a "we'll handle it from here" composure. Example shape only (write
   your own): 'Thanks for the heads up. We've got it from here.'

# Hard rules
- Plain English only. No Korean, no other languages.
- American or neutral English. NO British idioms (no "mate", "cheers",
  "neighbour", "recognise"). The Narrator TTS is American — British
  slang sounds wrong out of that voice.
- End every sentence with a full stop followed by a single space. The
  TTS splitter relies on ". " to chunk audio.
- No speaker labels ("[narrator]:"), no "[music]" cues, no stage directions.
- Exactly 5 sentences. Total length 380 to 480 English characters.
- The final sentence MUST end with the dinosaur's casual one-liner. No
  moral, no conclusion, no call to action after it.

# Required concrete nouns (must appear verbatim — they drive Pexels search)
- "northeast of the Yucatán Peninsula" (or "northeastern Yucatán Peninsula")
- "southern Laramidia"
- "asteroid"
- "ice age"
- "plant yields" (or "vegetation collapse")
- "small mammals"
- "nests"
- "tyrannosaur"

# Anti-patterns (DO NOT — these kill the joke)
- Do NOT explain why the situation is funny.
- Do NOT have the man speak with urgency or exclamation marks.
- Do NOT have the dinosaur panic, scream, or react with shock.
- Do NOT use "imagine", "suddenly", "incredibly", "amazingly", "behold".
- Do NOT add a moral, lesson, or call to action.
- Do NOT make the dinosaur quoted line longer than 12 words total.
- Do NOT use punctuation other than full stops, commas, and the single
  quoted dinosaur line. No semicolons, em-dashes, or question marks.

# One-shot example (match this rhythm — paraphrase every line, do NOT copy verbatim)
For most people, time travel is a chance to meet a grandmother for the first time, or to hug a loved one they lost too soon. One man, however, uses it as an extinction-event response protocol. Roughly 66 million years ago, he arrived in southern Laramidia and explained that an asteroid would strike the northeast of the Yucatán Peninsula. He would personally attempt to deflect it, but warned that the resulting ice age would collapse plant yields, and small mammals would soon raid tyrannosaur nests for eggs. A nearby tyrannosaur listened, lowered its head, and replied, 'Thanks for the heads up. We've got it from here.'

Subject: A man time-travels to warn the dinosaurs about the asteroid
Number of paragraphs: 1
Language: en
```

---

## `assets/intro.png` — 인트로 이미지 (선택)

`assets/intro.{png,jpg,jpeg,webp}` 가 있으면 파이프라인이 첫 3초 클립으로 자동 prepend.

- 모션: `fit` (전체 보이도록 letterbox, 흰 배경 — 가장자리 텍스트 안 잘림)
- 길이: `INTRO_DURATION` env (기본 3.0)
- 끄기: 파일 삭제. env 토글 없음.

⚠️ **한국어 텍스트 박힌 원본 짤은 넣지 마세요** (영어 컨텍스트 깨짐). 영어 wojak-vs-chad 카드를 직접 만들거나, `aiBrollToggle: true`로 두면 MFLUX가 영어 컨텍스트로 알아서 메움.

---

## 미세조정 치트시트

| 증상                 | 만지는 곳                                                                                                                              |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| 너무 다큐 같음           | customPrompt Tone 섹션의 "TikTok Narrator TTS, deadpan" 강화, "NOT documentary" 명시                                                       |
| 펀치라인 교체            | 구조 5번 예시 자리에 다른 미국식 deadpan: `'Got it. We'll handle it.'`, `'Thanks. We've got this.'`, `'Appreciate it. We'll take it from here.'` |
| 영상 길이              | "exactly 5 sentences" + "380 to 480 chars" 숫자만 변경 (현재 ~25-32초 + 인트로 3초)                                                             |
| Pexels 클립 시시       | Required nouns에 visual noun 추가: `meteor`, `crater`, `ash cloud`, `prehistoric forest`, `giant reptile`                              |
| 인트로 길이             | `.env`의 `INTRO_DURATION="2.0"`                                                                                                      |
| Ollama가 preamble 붙임 | customPrompt 상단의 **OUTPUT FORMAT (STRICT)** 섹션이 이미 막아놨음. 그래도 새면 그 섹션 더 강화                                                            |
| 다른 보이스 실험          | `en_us_006` (Joey, 미국 일반)이 deadpan 백업. 영국 보이스는 미국식 스크립트와 충돌                                                                         |

---

## 다음 단계 (기록용)

- **Phase 6 — Multi-voice scene narration**: 한 보이스 → 장면별 보이스 (narrator / chad / 공룡 각자 다른 TikTok 보이스). MFLUX per-scene 이미지. 짤 dialogue 느낌. ~3-4시간 작업.
- **Phase 7 — Cloud video API**: Runway / Veo 3로 진짜 motion 영상 + 캐릭터 일관성. 30초 영상에 \$3-6. 결제·외부 의존 추가.
