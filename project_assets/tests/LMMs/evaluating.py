from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from tqdm import tqdm
import sys
import os
from scipy.stats import ttest_rel, wilcoxon, shapiro, skew

model_names = {
    "bge-large-en-v1.5": "BAAI/bge-large-en-v1.5",
    "MiniLM-L6-v2": "sentence-transformers/all-MiniLM-L6-v2",
    "gte-large": "thenlper/gte-large",
    "e5-large-v2": "intfloat/e5-large-v2"
}

column_names = [
    "description_llava-v1.5-7b",
    "description_llava-v1.5-13b",
    "description_llava-v1.6-vicuna-7b",
    "description_llava-v1.6-vicuna-13b",
    "description_llava-v1.6-mistral-7b",
    "description_Llama-3.2-11B-Vision-Instruct",
    "description_Qwen2.5-VL-3B-Instruct_262144",
    "description_Qwen2.5-VL-7B-Instruct_262144"
]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(SCRIPT_DIR)

QWEN_RESULTS = os.path.join(PROJECT_ROOT,  "qwen", "qwen_output.csv")
LLAVA_RESULTS = os.path.join(PROJECT_ROOT, "llava", "llava_output.csv")
LLAMA_RESULTS = os.path.join(PROJECT_ROOT, "llama", "llama_output.csv")

RESULTS_COS_SIM = os.path.join(PROJECT_ROOT, "results_cos_sim.csv")
RESULTS_STATS = os.path.join(PROJECT_ROOT, "results_stats.csv")

def create_embeddings_and_file():
    df_llama = pd.read_csv(LLAMA_RESULTS)
    df_llava = pd.read_csv(LLAVA_RESULTS)
    df_qwen = pd.read_csv(QWEN_RESULTS)

    df_merged = df_llama.merge(df_llava, on='IMAGE_FILE', how='outer').merge(df_qwen, on='IMAGE_FILE', how='outer')

    df_merged = df_merged.drop(columns=[
        'DESCRIPTION_x', 'AUTHOR_x', 'TITLE_x', 'TECHNIQUE_x', 'DATE_x', 'TYPE_x', 'SCHOOL_x', 'TIMEFRAME_x',
        'DESCRIPTION_y', 'AUTHOR_y', 'TITLE_y', 'TECHNIQUE_y', 'DATE_y', 'TYPE_y', 'SCHOOL_y', 'TIMEFRAME_y'
    ])
    
    results = []
    for model_label, model_path in model_names.items():
        print(f"\n Loading model: {model_label}")
        model = SentenceTransformer(model_path)

        for idx, row in tqdm(df_merged.iterrows(), total=len(df_merged), desc=f"Processing with {model_label}"):
            original_description = row["DESCRIPTION"]
            generated_descriptions = [row[col] for col in column_names]

            original_emb = model.encode(original_description, convert_to_tensor=True)
            generated_embs = model.encode(generated_descriptions, convert_to_tensor=True)

            scores = cosine_similarity(
                original_emb.unsqueeze(0).cpu(), 
                generated_embs.cpu()
            ).flatten().tolist()


            item = {
                "model": model_label,
                "original_description": original_description
            }

            for column_name, score in zip(column_names, scores):
                dict_index = column_name.replace("description_", "score_")
                item[dict_index] = float(score)

            results.append(item)

    df_new = pd.DataFrame(results)
    df_new.to_csv(RESULTS_COS_SIM, index=False)
    print(f"✅ Results saved to results_cos_sim.csv")

def evaluate_model(model_name=None, file_name=RESULTS_COS_SIM):
    df = pd.read_csv(file_name)
    
    score_columns = [col for col in df.columns if col.startswith("score_")]

    if model_name is not None:
        # Filter to one model only
        df = df[df["model"] == model_name]

        # Calculate stats for that model
        stats = {
            "mean": df[score_columns].mean(),
            "std": df[score_columns].std(),
            "min": df[score_columns].min(),
            "max": df[score_columns].max(),
            "median": df[score_columns].median()
        }

        stats_df = pd.DataFrame(stats)
        stats_df = stats_df.reset_index().rename(columns={"index": "Generated_Description_Model"})
        stats_df["model"] = model_name

        return stats_df

    else:
        # Group by model, calculate stats for each group
        all_stats = []

        for name, group in df.groupby("model"):
            stats = {
                "Generated_Description_Model": score_columns,
                "mean": group[score_columns].mean().values,
                "std": group[score_columns].std().values,
                "min": group[score_columns].min().values,
                "max": group[score_columns].max().values,
                "median": group[score_columns].median().values,
                "model": name
            }
            stats_df = pd.DataFrame(stats)
            all_stats.append(stats_df)

        return pd.concat(all_stats, ignore_index=True)

def runtime_info():
    df_llama = pd.read_csv(LLAMA_RESULTS)
    df_llava = pd.read_csv(LLAVA_RESULTS)
    df_qwen = pd.read_csv(QWEN_RESULTS)

    df_merged = df_llama.merge(df_llava, on='IMAGE_FILE', how='outer').merge(df_qwen, on='IMAGE_FILE', how='outer')

    df_merged = df_merged.drop(columns=[
        'DESCRIPTION_x', 'AUTHOR_x', 'TITLE_x', 'TECHNIQUE_x', 'DATE_x', 'TYPE_x', 'SCHOOL_x', 'TIMEFRAME_x',
        'DESCRIPTION_y', 'AUTHOR_y', 'TITLE_y', 'TECHNIQUE_y', 'DATE_y', 'TYPE_y', 'SCHOOL_y', 'TIMEFRAME_y'
    ])

    time_columns = [col for col in df_merged.columns if col.startswith("time_")]
    allocated_columns = [col for col in df_merged.columns if col.startswith("allocated_")]
    reserved_columns = [col for col in df_merged.columns if col.startswith("reserved_")]

    average_times = {col: df_merged[col].mean() for col in time_columns}
    average_allocated = {col: df_merged[col].mean() for col in allocated_columns}
    average_reserved = {col: df_merged[col].mean() for col in reserved_columns}

    return {**average_times, **average_allocated, **average_reserved}

def do_all_t_tests(file_name=RESULTS_COS_SIM):
    df = pd.read_csv(file_name)

    for emb_model in model_names.keys():
        print(f"\n=== Embedding model: {model_names[emb_model]} ===")
        
        sub_df = df[df['model'] == emb_model]
        score_cols = [col for col in sub_df.columns if col.startswith("score_")]

        # Compute mean scores for each model
        mean_scores = sub_df[score_cols].mean().sort_values(ascending=False)
        top_model = mean_scores.index[0]

        print(f"Top model: {top_model}")
        
        for other_model in mean_scores.index[1:]:
            print(f"\nComparing {top_model} vs {other_model}")
            
            clean_df = sub_df[[top_model, other_model]].dropna()
            diffs = clean_df[top_model] - clean_df[other_model]

            observed_diff = diffs.mean()
            print(f"Mean difference: {observed_diff:.4f} ({top_model} - {other_model})")


            # Shapiro–Wilk test
            shapiro_stat, shapiro_p = shapiro(diffs)
            diff_skew = skew(diffs)
            print(f"Shapiro–Wilk test: W = {shapiro_stat:.4f}, p = {shapiro_p:.4e}")
            print(f"Skewness: {diff_skew:.4f}")

            if shapiro_p > 0.05:
                print("✅ Differences are normally distributed → t-test is valid.")
            elif abs(diff_skew) < 0.5:
                print("🟡 Differences are not normal but roughly symmetric → Wilcoxon is valid.")

            # Paired t-test
            t_stat, p_val = ttest_rel(clean_df[top_model], clean_df[other_model])
            print(f"Paired t-test: t = {t_stat:.4f}, p = {p_val:.4e}")

            # Wilcoxon test
            try:
                w_stat, p_wil = wilcoxon(clean_df[top_model], clean_df[other_model])
                print(f"Wilcoxon test: W = {w_stat:.4f}, p = {p_wil:.4e}")
            except ValueError as e:
                print(f"Wilcoxon test failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("   Please specify a mode: 'create' or 'evaluate'. Example:")
        print("   python evaluating.py create")
        print("   python evaluating.py evaluate bge-large-en-v1.5")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "create":
        create_embeddings_and_file()
        print("✅ Embeddings and cosine similarity scores have been created and saved.")
    elif mode == "evaluate":
        if len(sys.argv) < 3:
            print("   Evaluating all models")
            df_model = evaluate_model()
            df_model.to_csv(RESULTS_STATS, index=False, sep="\t", encoding="utf-8")
        else:
            model_name = sys.argv[2]
            print(f"   Evaluating model: {model_name}")
            df_model = evaluate_model(model_name)
        print(df_model)
    elif mode == "runtime_info":
        information = runtime_info()
        print(information)
    elif mode == "t-test":
        do_all_t_tests()
