# MoneyPrinter — Time-travel dinosaur warning meme

영어권 wojak-vs-chad 짤("타임머신을 탄 평범한 사람들 / 타임머신을 탄 나")의 영상화.
한국 짤이 영감, 결과물은 100% 영어 internet meme. **Cast dialogue mode**로 5명의
캐릭터가 7비트 코미디 구조를 분담합니다 (손녀·할머니 감성 setup → 나레이터 피벗
→ chad 3-step 브리핑 → 공룡 응답).

---

## 폼에 넣을 값

| 필드                  | 값                                                                                |
| ------------------- | -------------------------------------------------------------------------------- |
| `videoSubject`      | 아래 **VIDEO SUBJECT** 한 줄 통째                                                      |
| `customPrompt`      | 아래 **CUSTOM PROMPT** 코드블록 통째                                                     |
| `cast`              | `wojak_chad` (Cast 드롭다운에서 선택)                                                    |
| `voice`             | `en_male_narration` — cast 사용 시 fallback / NARRATOR 라인용. cast 없으면 전체 단일 보이스      |
| `paragraphNumber`   | `1` — 절대 변경 금지                                                                   |
| `useMusic`          | `true` — `Songs/vastness_andrew_ev.mp3`                                          |
| `aiBrollToggle`     | `true` — Mac M-series. "Laramidia" 등 Pexels 빵꾸 메움                                 |
| `subtitlesPosition` | `center,bottom`                                                                  |
| `color`             | `#FFFF00`                                                                        |
| `threads`           | `2` — Mac VideoToolbox 자동, 무시됨                                                   |

---

## VIDEO SUBJECT

While ordinary people use time travel to meet a lost grandmother or hug a loved one, one man treats it as an extinction-event response protocol — arriving in southern Laramidia to brief the dinosaurs on the incoming Chicxulub asteroid, the coming ice age, and the small mammals that will soon raid their nests

---

## CUSTOM PROMPT

```
You are writing a YouTube Shorts dialogue script in PLAIN MODERN ENGLISH
(American / neutral, NOT British), to be voiced line-by-line by different
TikTok TTS voices (the cast header above tells you which character IDs to use).

# OUTPUT FORMAT (CRITICAL — read carefully, follow exactly)
- Output exactly 7 dialogue lines, one per "comedy beat" (see Structure).
- Each line MUST start with a [CHARACTER_ID] tag from the Cast above.
- Each line is exactly ONE sentence ending with a period.
- One line per row in the output. No blank lines, no numbering, no markdown.
- The very first character of your output is "[". Nothing before it.
- Do NOT prefix with "Here is the script", "Here's the dialogue", "Sure, here's",
  "Below is", "Let me give you", "I've written", or any introduction.
- Do NOT close with "Hope this helps", commentary, summary, or anything else.

# Tone
Deadpan. Plain words. Short sentences per line. Treat the absurd premise with
complete sincerity, but flat. Comedy lives in the contrast between sentimental
opening + clinical briefing + casually competent dinosaur — NOT in line delivery.
Absolutely no humour in delivery. No ironic adjectives. No exclamation marks.

# Premise (THIS IS THE WHOLE JOKE — read carefully)
Side-by-side meme:
   Top half: ordinary people use time travel for emotional reasons (meeting
             a long-dead grandmother, hugging a lost loved one).
   Bottom half: this one man uses time travel as an extinction-event response
                protocol, briefing the dinosaurs about the Chicxulub asteroid.

The contrast — sentimental tourism vs. apocalyptic project management — IS
the joke. The man briefs the dinosaurs like a senior project manager reading
off a risk register. The dinosaur replies like a calm neighbor who already knows.

# Structure (7 lines, 7 comedy beats — each line = one beat)
Line 1 [GRANDDAUGHTER] — beat 1: emotional setup A. Granddaughter speaks
        directly to grandmother, having time-traveled to meet her for the
        first time. Warm, sentimental, plainly worded.
Line 2 [GRANDMOTHER] — beat 2: emotional setup B. The grandmother responds
        with reconciliation / surprise / something about old regrets being
        healed. The viewer should feel a tiny lump.
Line 3 [NARRATOR] — beat 3: HARD PIVOT. The thesis sentence. Direct,
        bureaucratic. State that one man treats time travel as an
        extinction-event response protocol. THIS IS THE PUNCHLINE.
Line 4 [CHAD] — beat 4: briefing 1. He arrived in southern LARAMIDIA roughly
        66 million years ago. Name "Laramidia" verbatim.
Line 5 [CHAD] — beat 5: briefing 2. An asteroid will strike the NORTHEAST
        of the YUCATÁN PENINSULA, and he will personally attempt to deflect
        it but the dinosaurs should evacuate as a contingency.
Line 6 [CHAD] — beat 6: briefing 3. The resulting ICE AGE will collapse
        PLANT YIELDS, and SMALL MAMMALS will raid TYRANNOSAUR NESTS for eggs.
Line 7 [DINOSAUR] — beat 7: a calm thank-you and a "we'll handle it from
        here" composure. ONE short sentence, max 12 words.

# Hard rules
- Plain English only. No Korean, no other languages.
- American or neutral English. NO British idioms (no "mate", "cheers",
  "neighbour", "recognise"). The TTS voices are American.
- Exactly 7 lines. Exactly 7 character tags in [BRACKETS]. Use the IDs
  from the Cast above — do NOT invent new character IDs.
- Each line is ONE sentence. Period at the end of each line.
- No semicolons, em-dashes, or question marks.
- The very first line starts with [GRANDDAUGHTER]. The very last line
  starts with [DINOSAUR] and ends with a period.

# Required concrete nouns (must appear verbatim across the briefing lines)
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
- Do NOT have CHAD speak with urgency, exclamation marks, or emotional shifts.
- Do NOT have DINOSAUR panic, scream, or react with shock.
- Do NOT use "imagine", "suddenly", "incredibly", "amazingly", "behold".
- Do NOT add a moral, lesson, or call to action.
- Do NOT write more than 7 lines. Do NOT skip any of the 7 beats.

# One-shot example (match this rhythm — paraphrase every line, do NOT copy verbatim)
[GRANDDAUGHTER] Grandma, I traveled back in time just to meet you for the first time.
[GRANDMOTHER] Sweetheart, you came all this way to find me?
[NARRATOR] One man, however, uses time travel as an extinction-event response protocol.
[CHAD] Roughly sixty-six million years ago, he arrived in southern Laramidia with a full evacuation plan.
[CHAD] An asteroid will strike the northeast of the Yucatán Peninsula, and while he will personally attempt to deflect it, you should evacuate as a contingency.
[CHAD] The resulting ice age will collapse plant yields, and small mammals will soon raid tyrannosaur nests for eggs.
[DINOSAUR] Thanks for the heads up, friend, we have it from here.

Subject: A man time-travels to warn the dinosaurs about the asteroid
Number of paragraphs: 1
Language: en
```

---

## `assets/intro.png` — 인트로 이미지 (선택)

`assets/intro.{png,jpg,jpeg,webp}`이 있으면 첫 3초 클립으로 자동 prepend.

- 모션: `fit` (전체 보이도록 letterbox, 흰 배경)
- 길이: `INTRO_DURATION` env (기본 3.0)
- 끄기: 파일 삭제

⚠️ 한국어 텍스트 박힌 원본 짤은 넣지 마세요 (영어 컨텍스트 깨짐). MFLUX가 영어 컨텍스트로 알아서 메워줍니다.

---

## Cast 시스템

`cast/<name>.json`에 정의된 캐릭터들이 한 번 만들어두면 여러 영상에 재사용됩니다.
이번 짤용은 `cast/wojak_chad.json` — 5명 (GRANDDAUGHTER, GRANDMOTHER, NARRATOR,
CHAD, DINOSAUR). 다른 짤 만들 때는 `cast/<your_name>.json` 새로 만들고 폼에서 그
이름 선택하면 됩니다. cast 비우면 단일 나레이터 모드로 폴백.

`/api/casts` 엔드포인트가 `cast/` 디렉터리를 스캔해 프론트 드롭다운을 채웁니다.

---

## 미세조정 치트시트

| 증상                      | 만지는 곳                                                                                                                                  |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| 감성 setup 약함             | Line 1·2 phrasing 강화 ("for the first time", "lost too soon", "old regrets healed")                                                     |
| 펀치라인 임팩트 약함             | Line 3 (NARRATOR) "extinction-event response protocol" 표현 그대로 유지. 동의어로 바꾸면 임팩트 죽음                                                        |
| CHAD 브리핑 길이             | Line 4·5·6 사이 정보 재분배. 7라인 구조는 유지                                                                                                         |
| DINOSAUR 응답이 너무 정중      | "Thanks for the heads up, friend." → "Got it. We've got this." / "Appreciate it. We'll take it from here."                              |
| 영상 길이 너무 김              | 7라인 → 5라인 압축 (Line 1+2 통합, 4+5 통합). 코미디 손상 가능, 시도해보고 결정                                                                                  |
| Pexels 클립 시시            | Required nouns에 visual noun 추가: `meteor`, `crater`, `ash cloud`, `prehistoric forest`                                                   |
| 인트로 길이                  | `.env`의 `INTRO_DURATION="2.0"`                                                                                                          |
| Ollama가 preamble 또는 라인 누락 | OUTPUT FORMAT 섹션 강화. "Output rule check: count your lines before responding. If not 7, regenerate." 추가                                   |
| 다른 cast 만들기             | `cast/<name>.json` 새로 만들고 캐릭터·voice 정의. 폼 Cast 드롭다운 새로고침                                                                                |

---

## 다음 단계 (기록용)

- **Phase 6b — Per-scene visuals**: 각 라인별로 MFLUX 이미지 생성 (캐릭터 → visual_seed). 짤의 4컷 구도 영상화. ~3시간 작업
- **Phase 7 — Cloud video API**: Runway / Veo 3로 진짜 motion 영상 + 캐릭터 일관성. 30초 영상 \$3-6. 결제·외부 의존
