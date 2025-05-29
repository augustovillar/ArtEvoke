import time
from transformers import AutoModelForCausalLM, AutoTokenizer
import re, sys, os
import pandas as pd

models = [
    "Qwen/Qwen3-1.7B",
    "Qwen/Qwen3-4B",
    "microsoft/Phi-4-mini-instruct"
]

art_descriptions = [
    "The painting presents a serene garden scene, rich with lush greenery and vibrant blooms. In the foreground, a variety of roses in shades of pink and white dominate the composition, their petals delicately detailed and arranged in clusters. The foliage is dense, with leaves of varying shades of green, creating a sense of depth and texture. A wooden fence runs horizontally across the lower part of the image, partially obscuring the view of the garden beyond.  In the mid-ground, a small figure, possibly a woman, is seated on a bench, her back turned to the viewer. She appears to be gazing into the distance, adding a contemplative element to the scene. The bench is positioned under a canopy of leaves, which filters the sunlight, casting dappled shadows on the ground. The background is filled with more greenery and hints of additional flowers, suggesting a continuation of the garden's beauty.  The overall atmosphere is tranquil and idyllic, evoking a sense of peace and natural beauty. The artist's attention to detail in the flora and the subtle presence of the human figure create a harmonious blend of nature and humanity within this picturesque setting.",
    "The painting depicts a vibrant and fantastical scene filled with an abundance of birds and cherubs. At the center, a figure dressed in flowing red robes, possibly representing a deity or a mythological character, is surrounded by numerous birds, including parrots, doves, and swans. The sky above is a dynamic blend of blue and white, dotted with clouds and populated by more birds in flight. Cherubs, some holding musical instruments like a lute, are scattered throughout the scene, adding to the sense of liveliness and harmony. The lower part of the painting features a lush landscape with trees and bushes, where additional birds and a group of swans are gathered. The overall atmosphere is one of joy and celebration, with the figures and creatures interacting in a whimsical and dreamlike manner.",
    "The painting depicts a vibrant and bustling scene on the Grand Canal in Venice, likely during a significant ceremonial event. In the foreground, numerous gondolas and other boats are crowded together, each carrying people dressed in elaborate costumes. Some individuals appear to be rowing, while others stand or sit, engaging in conversation or observing the surroundings. The gondolas are adorned with rich fabrics and decorations, suggesting a festive or celebratory occasion.  In the background, the iconic Doge's Palace stands prominently, its grand architecture and ornate details clearly visible. To the left, the Campanile of St. Mark's Basilica rises into the sky, adding to the sense of grandeur and historical significance. The sky above is filled with soft clouds, casting a gentle light over the scene, which enhances the overall atmosphere of festivity and opulence.  The composition is dynamic, with the movement of the boats and the activity of the people creating a sense of energy and excitement. The colors are vivid, with reds, golds, and blues dominating the palette, reflecting the luxurious and ceremonial nature of the event being depicted. The overall atmosphere is one of celebration and pageantry, capturing the essence of Venice's rich cultural heritage and its connection to the sea.",
]

base_prompt = (
    "Descriptions:\n"
    + "\n".join(f"- {desc}" for desc in art_descriptions)
    + "\n\n"
    "Write a story that takes inspiration on these scenes. Use 2–3 short paragraphs (approximately). "
    "Tell it like a simple, flowing story with a start, middle and an end. The paragraphs have to be conneced and follow a sequence of events."
)

messages = [{"role": "user", "content": base_prompt}]
REPEAT = 10

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RUN_INFO = os.path.join(SCRIPT_DIR, "llm_stories.csv")
EVALUATION_INFO = os.path.join(SCRIPT_DIR, "llm_evaluation.csv")

def is_successful_story(text):
    sentences = re.split(r'(?<=[.!?]) +', text.strip())
    return len(sentences) >= 2 and any(" and " in s or "then" in s or "," in s for s in sentences)

def run_models():
    rows = []

    for model_name in models:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name, torch_dtype="auto", device_map="cuda:0"
        )

        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True, enable_thinking=False
        )
        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

        for i in range(REPEAT):
            start = time.time()
            generated_ids = model.generate(
                **model_inputs,
                max_new_tokens=1024,
                do_sample=True,
                temperature=0.9,
            )
            end = time.time()
            output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
            content = tokenizer.decode(output_ids, skip_special_tokens=True).strip()
            duration = end - start
            success = is_successful_story(content)
            rows.append({
                "model": model_name,
                "run": i + 1,
                "generation_time": duration,
                "success": success,
                "story": content
            })

    df = pd.DataFrame(rows)
    df.to_csv(RUN_INFO, index=False)

def evaluate():
    df = pd.read_csv(RUN_INFO)
    evaluation_summary = []

    for model_name, group in df.groupby("model"):
        print(f"\n=== Evaluating {model_name} ===")
        avg_time = group["generation_time"].mean()
        manual_successes = 0
        manual_quality_scores = []

        for _, row in group.iterrows():
            print(f"\n[Run {row['run']}]")
            print(row["story"])
            valid_success = False
            while not valid_success:
                success_input = input("Is this a successful story? (y/n): ").strip().lower()
                if success_input in ("y", "n"):
                    valid_success = True
                    if success_input == "y":
                        manual_successes += 1
                        valid_score = False
                        while not valid_score:
                            try:
                                quality = int(input("Quality score (1–5): ").strip())
                                if 1 <= quality <= 5:
                                    manual_quality_scores.append(quality)
                                    valid_score = True
                            except ValueError:
                                continue

        success_rate = manual_successes / len(group)
        avg_quality = (
            sum(manual_quality_scores) / len(manual_quality_scores)
            if manual_quality_scores else 0
        )

        evaluation_summary.append({
            "Model": model_name,
            "Avg Time (s)": round(avg_time, 2),
            "Manual Success Rate (%)": round(success_rate * 100, 1),
            "Avg Quality Score (1–5)": round(avg_quality, 2)
        })

    summary_df = pd.DataFrame(evaluation_summary)
    print("\n=== Evaluation Summary ===")
    print(summary_df.to_string(index=False))
    summary_df.to_csv("llm_manual_evaluation_summary.csv", index=False)

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "run":
        run_models()
    elif mode == "evaluate":
        evaluate()        
