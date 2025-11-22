# Task

You are a grand art historian and a great novelist.

We are building a story based on different artworks selected by patients with dementia. Write a story that takes inspiration from these scenes. Use approximately 10 phrases. Tell it like a simple, flowing story with a clear start, middle, and end. The paragraphs must be connected and follow a logical sequence of events. The story needs to be in English.

# Output Format

After writing the story, you must provide:

1. **text**: The complete story text
2. **Events**: Exactly 4 events from the story, each as a short phrase (2-6 words), listed in chronological order as they occur in the story
3. **Distractor**: One short phrase (2-6 words) that describes something that is NOT an event from the story
4. **Environment**: The environment of the story. Choose one: Open, Urban, Closed, or Rural
5. **TimeOfDay**: The time of day in the story. Choose one: Morning, Afternoon, or Night
6. **Emotion**: The predominant emotion in the story. Choose one: Happiness, Sadness, Anger, Surprise, or Disgust

IMPORTANT: You MUST return a JSON object with the key "text" (NOT "story") containing the story.

Format your response as JSON with the following structure:
```json
{
  "text": "The complete story text here...",
  "events": [
    "First event phrase",
    "Second event phrase",
    "Third event phrase",
    "Fourth event phrase"
  ],
  "distractor": "A phrase that is not an event from the story",
  "environment": "Open",
  "timeOfDay": "Morning",
  "emotion": "Happiness"
}
```

Remember: Use "text" not "story" as the key for the story content.
