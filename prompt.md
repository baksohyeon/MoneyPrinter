# MoneyPrinter Input — A man time-travels to warn the dinosaurs

이 파일은 MoneyPrinter `/api/generate` 폼의 두 칸을 채우기 위한 원본입니다.

- `videoSubject` 칸 → 아래 **VIDEO SUBJECT** 한 줄 그대로
- `customPrompt` 칸 → 아래 **CUSTOM PROMPT** 코드블록 통째 그대로

타깃은 영어권 internet meme 영상입니다 — wojak-vs-chad 포맷의 deadpan 나레이션.
TikTok에서 보는 그 무미건조 narrator 보이스가 영국식 영어로 absurd premise를
완전히 진지하게 읽는 형식. 한국 짤 이미지가 영감 소스지만 결과물은 100% 영어권
internet meme 톤이고, 한국어 텍스트가 들어간 원본 짤 PNG는 인트로로 박지
않습니다(영어 컨텍스트가 깨지므로).

스크립트 톤은 `customPrompt`가, 영상 클립은 스크립트에서 자동 추출되는 1~3단어
영문 키워드(`get_search_terms()`)가 결정합니다. customPrompt 안의 구체 명사
(Yucatán Peninsula, asteroid, mammals 등)가 그대로 Pexels 검색어로 번역되어
영상 클립이 뽑힙니다. 영어 wojak-vs-chad 분위기 인트로를 박고 싶으면 본인이
영어 컨텍스트 이미지를 만들어 `assets/intro.png`에 두면 됩니다(아래 `assets/`
섹션 참조 — 메커니즘은 있지만 한국 원본 짤은 자동 사용 안 함).

권장 폼 값:

- `voice`: **`en_male_narration`** (TikTok "Narrator" 보이스 — 영어권 deadpan meme의 시그니처. 무조건 이거)
- `paragraphNumber`: **1** (절대 변경 금지 — customPrompt가 5문장 한 덩어리로 잠겨 있음)
- `threads`: **2** (Mac M-series는 VideoToolbox 자동 사용, 이 값은 무시됨)
- `useMusic`: **true** — `Songs/vastness_andrew_ev.mp3` 사용
- `aiBrollToggle`: **true** (M-series 전용. "Laramidia" 등 Pexels 빵꾸 메움)
- `subtitlesPosition`: `bottom`, `color`: `#FFFF00`

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

# Premise (THIS IS THE WHOLE JOKE — read carefully)
This is a side-by-side meme. The format is:
   Top half: ordinary people use time travel for emotional reasons —
             meeting a long-dead grandmother, hugging a lost loved one.
   Bottom half: this one man uses time travel as an extinction-event
                response protocol, briefing the dinosaurs about the
                Chicxulub asteroid.

The contrast — sentimental tourism vs. apocalyptic project management —
IS the joke. The man briefs the dinosaurs like a senior project
manager reading off a risk register. The dinosaur replies like a calm
British neighbour who already knows.

# Tone
Deadpan. Plain words. Short sentences. Never wink at the camera. Never
lampshade the joke. Treat the absurd premise with complete sincerity,
but flat. The comedy lives in the contrast and the dinosaur's calm —
NOT in narrator delivery. Absolutely no humour in delivery. No ironic
adjectives. No exclamation marks.

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
   your own): 'Thanks. We've got it from here.'

# Hard rules
- Output is plain English text only. No Korean, no other languages.
- American or neutral English. NO British idioms (no "mate", "cheers",
  "neighbour", "recognise"). The TikTok Narrator TTS is American — using
  British slang sounds wrong out of that voice.
- No markdown, no emojis, no bold, no headings, no bracketed stage directions.
- End every sentence with a full stop followed by a single space. The TTS
  splitter relies on ". " to chunk audio.
- No housekeeping intros ("In this video…", "Hello everyone").
- No speaker labels, no "[narrator]:", no "[music]" cues.
- Exactly 5 sentences. Total length 380 to 480 English characters.
- Keep word choice plain (Shorts viewers).
- The final sentence MUST end with the dinosaur's casual one-liner. No
  moral, no conclusion, no call to action after it.

# Required concrete nouns and phrases (must appear verbatim in the script)
- "northeast of the Yucatán Peninsula" (or "northeastern Yucatán Peninsula")
- "southern Laramidia"
- "asteroid"
- "ice age"
- "plant yields" (or "vegetation collapse")
- "small mammals"
- "nests"
- "tyrannosaur"

These drive the auto-extracted Pexels search terms (yucatan, asteroid,
mammal, ice age, jungle, t rex, nest), which decide the actual clips on
screen. "Laramidia" won't return Pexels footage but it lands as audio —
it's the nerd-bait that makes the briefing feel real.

# Anti-patterns (DO NOT DO ANY OF THESE — this kills the joke)
- Do NOT explain why the situation is funny or ironic.
- Do NOT have the man speak emotionally, urgently, or with exclamation marks.
- Do NOT have the dinosaur panic, run, scream, or react with shock.
- Do NOT use the words "imagine", "suddenly", "incredibly", "amazingly", "behold".
- Do NOT add a moral, lesson, or call to action at the end.
- Do NOT make the dinosaur quoted line longer than 12 words total.
- Do NOT use punctuation other than full stops, commas, and the single
  quoted dinosaur line. No semicolons, em-dashes, or question marks.
- Do NOT skip any of the required concrete nouns.

# The four load-bearing comedy beats (these MUST survive)
1. USE-CASE MISMATCH (the spine of the meme) — sentimental tourism vs.
   extinction-event response protocol. The contrast must be loud.
2. SERIOUSNESS GAP — gentle setup, then ice-cold clinical briefing.
   The narrator's voice never flinches.
3. OVER-ENGINEERED NERD DETAIL — compass directions ("northeast"),
   paleocontinent names ("Laramidia"), ecological consequences
   ("nests", "plant yields"). The more boringly specific, the funnier.
4. CASUALLY COMPETENT DINOSAUR — the tyrannosaur is calm, slightly
   amused this human came all this way. They thank him AND say they'll
   handle it from here.

# One-shot example (match this exact rhythm — write your OWN phrasing)
"For most people, time travel is a chance to meet a grandmother for the
 first time, or to hug a loved one they lost too soon.
 One man, however, uses it as an extinction-event response protocol.
 Roughly 66 million years ago, he arrived in southern Laramidia and
 explained that an asteroid would strike the northeast of the Yucatán
 Peninsula.
 He would personally attempt to deflect it, but warned that the
 resulting ice age would collapse plant yields, and small mammals
 would soon raid tyrannosaur nests for eggs.
 A nearby tyrannosaur listened, lowered its head, and replied,
 'Thanks for the heads up. We've got it from here.'"

Now write your OWN version. Same 5-sentence rhythm, same comedy structure,
different phrasing. Do NOT copy the example sentences verbatim — paraphrase
every line. The contrast in sentence 2 (ordinary use vs. extinction
mitigation) must hit hardest.

Subject: A man time-travels to warn the dinosaurs about the asteroid
Number of paragraphs: 1
Language: en
```

---

## 파이프라인이 위 입력을 어떻게 쓰는지 (참고)

| 단계 | 코드                                          | 무엇을 함                                                                |
| -- | ------------------------------------------- | -------------------------------------------------------------------- |
| 0  | `pipeline.py` 인트로 자동 인서트                    | `assets/intro.png` 존재 시 첫 3초 Ken-Burns 클립으로 prepend (motion="fit") |
| 1  | `gpt.py:142` `generate_script()`            | 위 customPrompt 그대로 Ollama에 전달 → UK English 나레이션 5문장                  |
| 2  | `gpt.py:237` `get_search_terms()`           | 스크립트를 다시 Ollama에 넣고 1~3단어 영문 키워드 10개 뽑음                              |
| 3  | `providers/stock/*` 다중 소스 검색                | 키워드별로 Pexels/Pixabay/Coverr 병렬 검색, 3초 이상 클립 1개씩                       |
| 4  | `providers/imagegen/mflux.py` (옵션)          | 빵꾸난 키워드("Laramidia" 등)에 대해 MFLUX 이미지 생성 → KenBurnsAsset             |
| 5  | `pipeline.py:124` 문장 단위 분절                  | `". "`로 split → 문장당 TTS 1개                                            |
| 6  | `tiktokvoice.py` TTS                        | 선택된 voice로 문장별 mp3 생성 후 합침                                           |
| 7  | `video.py::combine_videos`                  | 인트로 + 스톡 + AI B-roll 혼합, 9:16 크롭                                      |
| 8  | `video.py::burn_and_mix`                    | libass 자막 burn-in + 오디오 mix + (선택) 음악 amix → h264_videotoolbox 1-pass |

`pipeline.py:66`에서 `voice[:2]`로 prefix를 잘라 자막 언어를 결정하므로
`en_uk_*` / `en_us_*` / `en_male_*` 어떤 영문 보이스를 골라도 영어 자막 트랙으로 처리됩니다.

## `assets/intro.png` — 인트로 이미지 직접 박기 (선택)

`assets/intro.png` (또는 `intro.jpg`/`intro.jpeg`/`intro.webp`)이 존재하면
파이프라인이 자동으로 영상 첫 클립으로 박아 넣습니다.

- 모션: `fit` (전체 이미지 보이도록 letterbox, 흰색 배경)
- 길이: `INTRO_DURATION` env (기본 3.0초)
- 끄려면: 파일을 지우면 됨. env 토글 같은 거 없음.

**중요** — 결과물은 영어권 internet meme이라 인트로 이미지도 영어 컨텍스트여야
합니다. 한국어 텍스트가 들어간 원본 짤은 박지 마세요(언어 충돌). 영어 인트로
옵션:

1. **MFLUX 자동 생성** — `aiBrollToggle: true` + customPrompt에 "wojak crying"
   같은 영문 명사를 끼워 넣으면 MFLUX가 영문 컨텍스트의 채드/와우작 풍 이미지를
   자동 생성해 끼움. 별도 인트로 필요 없음.
2. **본인이 영어 인트로 만들기** — Photoshop/Figma/Canva로 "Ordinary people
   time-traveling / Me time-traveling" 식의 영문 wojak-vs-chad 카드를 만들어
   `assets/intro.png`로 저장.
3. **인트로 없음** — `assets/`에 파일 안 두면 그냥 Pexels + MFLUX 클립으로 시작.

## 유머 포인트가 어디서 살아남는지

- **seriousness gap** → "deadpan internet narrator" + "absolutely no humour in delivery" 이중 강제
- **과잉 디테일** → "Required concrete nouns" 강제 + "clinical, like a project risk register" 지시
- **공룡의 침착함** → 구조 5번에서 단일 short quoted line 강제, 12단어 cap
- **cinematic 영상감** → 강제 명사들이 자동으로 cinematic 한 Pexels 키워드로
  번역되어 클립이 그쪽으로 쏠림 + 첫 3초는 짤 PNG 자체

## 깎고 싶을 때 만지는 곳

- 영상 길이 → Structure의 "exactly 5 sentences"와 Hard rules의 "380 to 480
  English characters" 숫자만 변경 (현재 예상 25~32초 + 인트로 3초)
- Pexels 클립이 시시함 → "Required concrete nouns"에 시각적 명사 추가
  (meteor, crater, ash cloud, giant reptile, prehistoric forest)
- 펀치라인 교체 → 구조 5번의 예시 대사("Thanks for the heads up. We've got it
  from here.")만 다른 것으로. 미국식 deadpan 유지: "Got it. We'll handle it.",
  "Appreciate it. We'll take it from here.", "Thanks. We've got this."
- 너무 다큐스럽게 나옴 → Tone 섹션의 "TikTok Narrator TTS" 강조,
  "NOT BBC Earth, NOT documentary" 명시
- 인트로 길이 조정 → `.env`에 `INTRO_DURATION="2.0"` 등으로 변경
- 보이스 변경 → 기본은 무조건 `en_male_narration`. 다른 deadpan TikTok 보이스로
  실험하려면 `en_us_006`(Joey, 미국 남성 일반)도 가능. 영국식 보이스는 영어 스크립트
  미국화 했기 때문에 부적합.
