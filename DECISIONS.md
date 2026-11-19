# Decisions

A running log of design choices for Vela, with the reason for each.
Format: what I chose, why, and what it costs.

## D1. Hand-rolled pipeline, no framework
- **Chose:** plain Python and asyncio instead of Pipecat or LiveKit Agents.
- **Why:** the job is about understanding STT, TTS and interruption handling. A framework hides exactly those parts.
- **Cost:** more code to write and more bugs. Porting one path to a framework later is a possible comparison.

## D2. Wrote the knowledge base myself (26 pages, fictional company)
- **Chose:** invented "Vela Visas" facts instead of copying a real company's site.
- **Why:** I need to know the true answer to catch a wrong one. It also avoids copying anyone's content.
- **Cost:** the facts are fake, so the agent is a demo, not a real visa service.

## D3. Deliberate traps in the knowledge base
- **Chose:** (a) kb-001 says the service fee is USD 25, but kb-019 says Singapore is USD 20 and replaces it. (b) No pages on visa extensions, visa validity, or Zambia.
- **Why:** (a) tests whether the agent picks the specific page over the general one. (b) tests whether it says "I don't have that information" instead of inventing an answer.
- **Cost:** none, but I must not "fix" the gaps later or the test stops working.

## D4. Retrieval: all-MiniLM-L6-v2 embeddings + ChromaDB, one piece per short page
- **Chose:** a small local embedding model and a local vector store.
- **Why:** free, runs on my 8 GB laptop, fast enough for the 50 ms retrieval budget.
- **Cost:** pure meaning-search can miss exact terms. Hybrid search (BM25 + embeddings) is a candidate fix in the failure analysis.
- **Note:** the collection is called `visa_kb` because ChromaDB needs names of 3+ characters.

## D5. Hosted LLM (Groq) instead of a local model
- **Chose:** Groq's hosted API.
- **Why:** voice needs low latency, and an 8 GB laptop would struggle to run a local LLM, Whisper and a voice together.
- **Cost:** needs internet, and free-tier limits apply. Free-tier latency is not representative of production.

## D6. LLM behind one adapter file (providers/llm.py)
- **Chose:** every LLM call goes through one function.
- **Why:** when Groq retired llama-3.3-70b-versatile for my account, I changed one line in .env and kept the code. It also lets me compare providers later.
- **Cost:** a small extra layer of code.

## D7. Switched model to openai/gpt-oss-20b
- **Chose:** a smaller, faster model.
- **Why:** my original model name returned "model not found". I listed the models my key can use and picked a current one that supports tool use. Smaller is faster, which matters for voice.
- **Cost:** may follow rules less reliably than a larger model. To be measured in the evals; openai/gpt-oss-120b is the fallback.

## D8. Throw away tool results from history after each turn
- **Chose:** keep only what was said (user text, agent reply), drop the retrieved notebook pages.
- **Why:** the free tier limits tokens per minute (8,000). Re-sending every old search result hit the limit at question 7.
- **Cost:** on a follow-up question the agent must search again instead of reusing old results. Slightly slower, but each answer stays grounded in fresh results.

## D9. Retry on rate-limit errors
- **Chose:** when Groq returns 429, wait the time it asks for and try again, up to 3 times.
- **Why:** a crash in the middle of a phone call is worse than a short pause.
- **Cost:** retries add to latency, so I must not read latency numbers from runs that retried.

## D10. Secrets only in .env, which is ignored by Git
- **Chose:** API key lives only in .env. .env, applications.db, logs/ and chroma_db/ are in .gitignore.
- **Why:** keys pushed to a public repo get stolen quickly.
- **Cost:** anyone cloning the repo must create their own .env.

## D11. Clean the application ID before lookup
- **Chose:** "vl 100007", "VL-100007" and "vl-100007" all become VL-100007.
- **Why:** a speech-to-text system will not always write the ID in the exact format.
- **Cost:** a wrong-but-valid ID could match someone else's application. The lookup returns only status, country and date, never names.

## D12. Logging every turn from day one
- **Chose:** every turn writes one JSON line (transcript, reply, tools, retrieved page IDs, timestamps).
- **Why:** every metric in the eval harness is computed from these logs. Adding logging later would cost a day.
- **Cost:** logs/ grows over time. It is ignored by Git.

## D13. System prompt has three explicit rules
- **Chose:** GROUNDING, VOICE STYLE, ESCALATION, kept short.
- **Why:** these are the three behaviours I measure later (hallucination, naturalness, escalation). A short prompt also keeps the first-token time low.
- **Cost:** short rules leave gaps. Failures found in the evals decide what to add.

## Still to decide (do not fill in until I have data)
- SILENCE_MS (end-of-turn silence): ____ ms, because ____ (table of false cutoffs vs added latency)
- BARGE_MS (interruption threshold): ____ ms, because ____
- Why cancelling on interruption truncates the history to what was actually heard
- Why the judge model differs from the agent model