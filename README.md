# AI Study Coach — Project Idea

## What It Is
An AI-powered study companion that turns a course syllabus into a personalized learning journey. It helps students understand topics, practice with flashcards and quizzes, and continuously tracks mastery to focus effort where it matters most.

## Why It Matters
- Students often have dense syllabi but lack a clear plan.
- Explanations, practice, and spaced repetition are fragmented across tools.
- This coach unifies ingestion, planning, practice, and progress tracking into a single workflow.

## Core Idea
1. Ingest the syllabus PDF and extract structured topics automatically.
2. Build a lightweight knowledge graph per student that tracks mastery, attempts, and review scheduling.
3. Use an LLM to explain concepts, generate flashcards and MCQs, and propose a study plan that prioritizes weak areas.
4. Close the loop: practicing updates mastery, which shapes future plans and recommendations.

## How It Works
- Syllabus parsing: The app cleans raw PDF text and detects units/chapters and numbered sections to produce a topic list.
- Knowledge graph: For each student, a local JSON graph stores topics with `mastery`, `attempts`, `correct/wrong`, and next review time based on a simple forgetting curve.
- LLM assistance: Prompts generate
  - plain-language explanations,
  - concise flashcards,
  - MCQs with answers and rationale,
  - multi-day study plans tailored to current mastery.
- UI flow: Upload syllabus → view extracted topics → generate a plan → review topics (explain/flashcards/MCQs) → see progress and weakest topics.

## Key Features
- Topic extraction from real syllabi with heuristics and regex.
- Personalized plans that focus on weaker topics and include spaced repetition.
- Immediate practice via flashcards and auto-graded MCQs.
- Mastery tracking with decay and scheduling of next reviews.
- Local-first storage; student data saved in the project under `students/{student_id}`.

## Design Principles
- Simple, transparent data model (JSON per student).
- Prompt-driven LLM features that are easy to tweak.
- Streamlined UI—everything important in a few tabs.
- Extensible tool registry for adding new capabilities.

## Typical User Journey
- Upload the course syllabus PDF.
- Review extracted topics; adjust if needed.
- Generate a study plan for 7–30 days.
- Study a topic: read explanation, practice flashcards, take a short MCQ quiz.
- See mastery progress and weakest topics; repeat with spaced reviews.

## Extensibility
- Swap or configure LLM models and prompts.
- Add new practice modes (e.g., coding exercises, open-ended questions).
- Enhance topic extraction rules for specific departments or formats.

## Privacy & Data
- Student data and mastery are stored locally in JSON.
- No cloud dependencies are required for core functionality.

