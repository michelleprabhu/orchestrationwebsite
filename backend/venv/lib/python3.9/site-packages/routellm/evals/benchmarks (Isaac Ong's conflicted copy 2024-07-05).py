import abc
import os
from collections import Counter
from glob import glob

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from tqdm import tqdm

from routellm.routers.routers import Router

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

pd.options.mode.copy_on_write = True
tqdm.pandas()


class Benchmark(abc.ABC):
    """
    Benchmark class for evaluating models.

    Internally, class should handle init and manage own cache (if needed).
    """

    @abc.abstractmethod
    def evaluate(
        self, router: Router, threshold: float, overwrite_router_cache: bool
    ) -> tuple[str, dict[str, int], str]:
        """Takes in a router and threshold and returns a tuple of weighted accuracy, model counts, and number of requests."""
        pass

    @abc.abstractmethod
    def get_optimal_accuracy(self, strong_percent: float) -> float:
        """Takes in % strong model calls and returns the optimal score for the benchmark given these % of calls."""
        pass

    @abc.abstractmethod
    def get_model_accuracy(self, model: str) -> float:
        """Takes in a model name and returns the accuracy of that model on the benchmark."""
        pass


class MMLU(Benchmark):
    def __init__(self, domains, routed_pair, overwrite_cache):
        self.routed_pair = routed_pair
        self.overwrite_cache = overwrite_cache
        self.cache_path = f"{CURRENT_DIR}/mmlu/cache.npy"

        try:
            self.cache = np.load(self.cache_path, allow_pickle=True).item()
        except:
            self.cache = {}

        all_data = pd.DataFrame()
        for domain in tqdm(domains, desc="Loading domain data"):
            all_data = pd.concat(
                [
                    all_data,
                    pd.read_csv(f"{CURRENT_DIR}/mmlu/responses/mmlu_{domain}.csv"),
                ],
                ignore_index=True,
            )
        original_length = len(all_data)

        # Generated using contamination_check.py
        contaminated_prompts = pd.read_json(
            f"{CURRENT_DIR}/mmlu/contaminated_prompts.jsonl", lines=True
        )["eval_prompt"].tolist()
        self.all_data = all_data[~all_data["prompt"].isin(contaminated_prompts)]
        print(
            f"Remaining {len(self.all_data)}/{original_length} prompts for MMLU after decontamination"
        )

    def evaluate(self, router, num_results, overwrite_router_cache):
        router_name = str(router)

        if (
            router_name not in self.cache
            or router_name in self.overwrite_cache
            or overwrite_router_cache
        ):
            if router.NO_PARALLEL:
                strong_win_rates = self.all_data["prompt"].progress_apply(
                    router.calculate_strong_win_rate
                )
            else:
                strong_win_rates = self.all_data["prompt"].parallel_map(
                    router.calculate_strong_win_rate
                )
            self.cache[router_name] = strong_win_rates
            np.save(self.cache_path, self.cache)
        else:
            strong_win_rates = self.cache[router_name]

        # Choose thresholds split into 10 equally sized bins (including duplicates)
        _, thresholds = pd.qcut(strong_win_rates, num_results, retbins=True)
        self.all_data["strong_win_rates"] = strong_win_rates

        for i, threshold in enumerate(thresholds):
            selection = (
                self.all_data["strong_win_rates"] >= threshold
                if i != len(thresholds) - 1
                else self.all_data["strong_win_rates"] > threshold
            )
            results = np.where(
                selection,
                self.all_data[self.routed_pair.strong],
                self.all_data[self.routed_pair.weak],
            )
            models = np.where(
                selection,
                self.routed_pair.strong,
                self.routed_pair.weak,
            )
            model_counts = Counter(models)
            yield threshold, sum(results) / len(results) * 100, model_counts, len(
                results
            )

    def get_optimal_accuracy(self, strong_percent):
        df = self.all_data
        total = len(df)

        strong_calls = total * strong_percent
        weak_correct = len(df[df[self.routed_pair.weak] == True])

        df_sub = df[df[self.routed_pair.weak] == False]
        df_sub = df_sub[df_sub[self.routed_pair.strong] == True]

        strong_bonus = min(strong_calls, len(df_sub))
        opt_correct = weak_correct + strong_bonus
        opt_accuracy = opt_correct / total * 100

        return opt_accuracy

    def get_model_accuracy(self, model):
        df = self.all_data
        return len(df[df[model] == True]) / len(df) * 100


class MTBench(Benchmark):
    def __init__(self, routed_pair, overwrite_cache):
        self.routed_pair = routed_pair

        self.judgements = pd.read_json(
            f"{CURRENT_DIR}/mt_bench/judgements.jsonl", lines=True
        )
        self.questions = pd.read_json(
            f"{CURRENT_DIR}/mt_bench/question.jsonl", lines=True
        )
        contaminated_prompts = pd.read_json(
            f"{CURRENT_DIR}/mt_bench/contaminated_prompts.jsonl", lines=True
        )["eval_prompt"].tolist()

        self.questions["turn1"] = self.questions["turns"].apply(lambda x: x[0])
        self.questions["turn2"] = self.questions["turns"].apply(lambda x: x[1])
        self.questions = self.questions[
            ~(
                self.questions["turn1"].isin(contaminated_prompts)
                | self.questions["turn2"].isin(contaminated_prompts)
            )
        ]
        print(f"{len(self.questions)} questions for MT bench after decontamination.")

        self.overwrite_cache = overwrite_cache
        self.cache_path = f"{CURRENT_DIR}/mt_bench/cache.npy"

        try:
            self.cache = np.load(self.cache_path, allow_pickle=True).item()
        except:
            print("Error loading MT Bench cache, starting fresh.")
            self.cache = {}

    def evaluate(self, router, num_results, overwrite_router_cache):
        router_name = str(router)

        if (
            router_name not in self.cache
            or router_name in self.overwrite_cache
            or overwrite_router_cache
        ):
            if router.NO_PARALLEL:
                strong_win_rates = self.questions["turns"].progress_apply(
                    # Only use first turn for routing
                    lambda turn: router.calculate_strong_win_rate(turn[0])
                )
            else:
                strong_win_rates = self.questions["turns"].parallel_apply(
                    lambda turn: router.calculate_strong_win_rate(turn[0])
                )
            self.cache[router_name] = strong_win_rates
            np.save(self.cache_path, self.cache)
        else:
            strong_win_rates = self.cache[router_name]

        _, thresholds = pd.qcut(strong_win_rates, num_results, retbins=True)
        questions = self.questions[["question_id", "turns"]]
        questions["strong_win_rates"] = strong_win_rates

        for i, threshold in enumerate(thresholds):
            questions["routed_model"] = np.where(
                (
                    questions["strong_win_rates"] >= threshold
                    if i != len(thresholds) - 1
                    else questions["strong_win_rates"] > threshold
                ),
                self.routed_pair.strong,
                self.routed_pair.weak,
            )

            results = questions.merge(
                self.judgements,
                left_on=["question_id", "routed_model"],
                right_on=["question_id", "model"],
                how="left",
            )[["question_id", "model", "score"]]

            score = results["score"].mean()

            model_counts = results["model"].value_counts().to_dict()
            if self.routed_pair.weak not in model_counts:
                model_counts[self.routed_pair.weak] = 0
            if self.routed_pair.strong not in model_counts:
                model_counts[self.routed_pair.strong] = 0

            total = len(results)

            assert total == sum(model_counts.values()) == len(self.questions) * 2

            yield threshold, score, model_counts, total

    def get_model_accuracy(self, model):
        questions = self.questions[["question_id"]]
        questions["routed_model"] = model

        results = questions.merge(
            self.judgements,
            left_on=["question_id", "routed_model"],
            right_on=["question_id", "model"],
            how="left",
        )[["question_id", "model", "score"]]

        return results["score"].mean()

    def get_optimal_accuracy(self, strong_percent):
        max_strong_calls = int(len(self.questions) * strong_percent)

        strong_judgements = (
            self.judgements[self.judgements["model"] == self.routed_pair.strong][
                ["question_id", "model", "score"]
            ]
            .groupby(by=["model", "question_id"], as_index=False)
            .mean()
        )

        weak_judgements = (
            self.judgements[self.judgements["model"] == self.routed_pair.weak][
                [
                    "question_id",
                    "model",
                    "score",
                ]
            ]
            .groupby(by=["model", "question_id"], as_index=False)
            .mean()
        )

        combined_judgements = strong_judgements.merge(
            weak_judgements,
            on=["question_id"],
            how="left",
            suffixes=("_strong", "_weak"),
        )
        combined_judgements["diff"] = (
            combined_judgements["score_strong"] - combined_judgements["score_weak"]
        )
        combined_judgements = combined_judgements.sort_values(
            by=["diff"], ascending=False
        ).reset_index(drop=True)

        if len(combined_judgements[combined_judgements["diff"] > 0]) > max_strong_calls:
            combined_judgements.loc[:max_strong_calls, "score_optimal"] = (
                combined_judgements.loc[:max_strong_calls, "score_strong"]
            )
            combined_judgements.loc[max_strong_calls:, "score_optimal"] = (
                combined_judgements.loc[max_strong_calls:, "score_weak"]
            )
        else:
            combined_judgements["score_optimal"] = combined_judgements[
                "score_strong"
            ].where(combined_judgements["diff"] > 0, combined_judgements["score_weak"])

        assert (
            len(strong_judgements) == len(weak_judgements) == len(combined_judgements)
        )

        return combined_judgements["score_optimal"].mean()


class GSM8K(Benchmark):
    def __init__(self, routed_pair, overwrite_cache):
        self.routed_pair = routed_pair
        self.overwrite_cache = overwrite_cache
        self.cache_path = f"{CURRENT_DIR}/gsm8k/cache.npy"

        try:
            self.cache = np.load(self.cache_path, allow_pickle=True).item()
        except:
            self.cache = {}

        all_data = pd.read_csv(f"{CURRENT_DIR}/gsm8k/gsm8k_responses.csv")
        original_len = len(all_data)

        contaminated_prompts = pd.read_json(
            f"{CURRENT_DIR}/gsm8k/contaminated_prompts.jsonl", lines=True
        )["eval_prompt"].tolist()
        self.all_data = all_data[~all_data["prompt"].isin(contaminated_prompts)]
        print(
            f"{len(self.all_data)}/{original_len} questions for GSM8K after decontamination."
        )

    def evaluate(self, router, num_results, overwrite_router_cache):
        router_name = str(router)

        if (
            router_name not in self.cache
            or router_name in self.overwrite_cache
            or overwrite_router_cache
        ):
            if router.NO_PARALLEL:
                strong_win_rates = self.all_data["prompt"].progress_apply(
                    router.calculate_strong_win_rate
                )
            else:
                strong_win_rates = self.all_data["prompt"].parallel_map(
                    router.calculate_strong_win_rate
                )
            self.cache[router_name] = strong_win_rates
            np.save(self.cache_path, self.cache)
        else:
            strong_win_rates = self.cache[router_name]

        # Choose thresholds split into 10 equally sized bins (including duplicates)
        _, thresholds = pd.qcut(strong_win_rates, num_results, retbins=True)
        self.all_data["strong_win_rates"] = strong_win_rates

        for i, threshold in enumerate(thresholds):
            selection = (
                self.all_data["strong_win_rates"] >= threshold
                if i != len(thresholds) - 1
                else self.all_data["strong_win_rates"] > threshold
            )
            results = np.where(
                selection,
                self.all_data[self.routed_pair.strong],
                self.all_data[self.routed_pair.weak],
            )
            models = np.where(selection, self.routed_pair.strong, self.routed_pair.weak)
            model_counts = Counter(models)
            yield threshold, sum(results) / len(results) * 100, model_counts, len(
                results
            )

    def get_model_accuracy(self, model):
        df = self.all_data
        return len(df[df[model] == True]) / len(df) * 100

    def get_optimal_accuracy(self, strong_percent):
        df = self.all_data
        total = len(df)

        strong_calls = total * strong_percent
        weak_correct = len(df[df[self.routed_pair.weak] == True])

        df_sub = df[df[self.routed_pair.weak] == False]
        df_sub = df_sub[df_sub[self.routed_pair.strong] == True]

        strong_bonus = min(strong_calls, len(df_sub))
        opt_correct = weak_correct + strong_bonus
        opt_accuracy = opt_correct / total * 100

        return opt_accuracy


class ArenaHard(Benchmark):
    # Methods based on https://github.com/lm-sys/arena-hard/blob/main/show_result.py
    def __init__(self, overwrite_cache):
        self.overwrite_cache = overwrite_cache
        self.questions = pd.read_json(
            f"{CURRENT_DIR}/arena_hard/question.jsonl", lines=True
        )

        self.judgement_dfs = {}

        directory = f"{CURRENT_DIR}/arena_hard/model_judgment/gpt-4-1106-preview"
        assert os.path.exists(directory)
        for file in tqdm(glob(f"{directory}/*jsonl"), desc="Loading Arena Hard data"):
            filename = os.path.basename(file)
            self.judgement_dfs[filename] = pd.read_json(file, lines=True)

        # NOTE: Here, we replace gpt-4-1106-preview with gpt-4-0125 because the former is used as a judge.
        self.gpt4_judgements = self.judgement_dfs["gpt-4-0125-preview.jsonl"]
        self.mixtral_judgements = self.judgement_dfs["Mixtral-8x7B-Instruct-v0.1.jsonl"]

        # To make it easier to merge them, we sort them by question_id
        self.questions = self.questions.sort_values("question_id").reset_index(
            drop=True
        )
        self.gpt4_judgements = self.gpt4_judgements.sort_values(
            "question_id"
        ).reset_index(drop=True)
        self.mixtral_judgements = self.mixtral_judgements.sort_values(
            "question_id"
        ).reset_index(drop=True)

        self.gpt4_accuracy = None
        self.mixtral_accuracy = None

        try:
            self.cache = np.load(
                "cache/eval/arena_hard/thresholds_cache.npy", allow_pickle=True
            ).item()
        except:
            print("Error loading Arena Hard cache, starting fresh.")
            self.cache = {}

    # We use gpt-4-0314 as anchor.
    def compute_mle_elo(self, df, SCALE=400, BASE=10, INIT_RATING=1000):
        models = pd.concat([df["model_a"], df["model_b"]]).unique()
        models = pd.Series(np.arange(len(models)), index=models)

        # duplicate battles
        df = pd.concat([df, df], ignore_index=True)
        p = len(models.index)
        n = df.shape[0]

        X = np.zeros([n, p])
        X[np.arange(n), models[df["model_a"]]] = +math.log(BASE)
        X[np.arange(n), models[df["model_b"]]] = -math.log(BASE)

        # one A win => two A win
        Y = np.zeros(n)
        Y[df["winner"] == "model_a"] = 1.0

        # one tie => one A win + one B win
        # find tie + tie (both bad) index
        tie_idx = (df["winner"] == "tie") | (df["winner"] == "tie (bothbad)")
        tie_idx[len(tie_idx) // 2 :] = False
        Y[tie_idx] = 1.0

        lr = LogisticRegression(fit_intercept=False, penalty=None, tol=1e-8)
        lr.fit(X, Y)

        elo_scores = SCALE * lr.coef_[0] + INIT_RATING

        # set anchor as gpt-4-0314 = 1000
        if "gpt-4-0314" in models.index:
            elo_scores += 1000 - elo_scores[models["gpt-4-0314"]]
        return pd.Series(elo_scores, index=models.index).sort_values(ascending=False)

    def get_bootstrap_result(self, battles, func_compute_elo, num_round):
        rows = []
        for i in tqdm(range(num_round), desc="bootstrap"):
            rows.append(func_compute_elo(battles.sample(frac=1.0, replace=True)))
        df = pd.DataFrame(rows)
        return df[df.median().sort_values(ascending=False).index]

    def get_battles_from_judgment(self, judgement_dfs, first_game_only=False, WEIGHT=3):
        arena_hard_battles = pd.DataFrame()

        for df in judgement_dfs:
            for _, row in df.iterrows():
                # game 1
                output = {
                    "question_id": row["question_id"],
                    "model_a": "gpt-4-0314",
                    "model_b": row["model"],
                }

                game = row["games"][0]

                weight = 1
                if game["score"] == "A=B":
                    output["winner"] = "tie"
                elif game["score"] == "A>B":
                    output["winner"] = "model_a"
                elif game["score"] == "A>>B":
                    output["winner"] = "model_a"
                    weight = WEIGHT
                elif game["score"] == "B>A":
                    output["winner"] = "model_b"
                elif game["score"] == "B>>A":
                    output["winner"] = "model_b"
                    weight = WEIGHT
                else:
                    weight = 0

                if weight:
                    arena_hard_battles = pd.concat(
                        [arena_hard_battles, pd.DataFrame([output] * weight)]
                    )

                if not first_game_only:
                    # game 2
                    output = {
                        "question_id": row["question_id"],
                        "model_a": "gpt-4-0314",
                        "model_b": row["model"],
                    }

                    game = row["games"][1]

                    weight = 1
                    if game["score"] == "A=B":
                        output["winner"] = "tie"
                    elif game["score"] == "A>B":
                        output["winner"] = "model_b"
                    elif game["score"] == "A>>B":
                        output["winner"] = "model_b"
                        weight = WEIGHT
                    elif game["score"] == "B>A":
                        output["winner"] = "model_a"
                    elif game["score"] == "B>>A":
                        output["winner"] = "model_a"
                        weight = WEIGHT
                    else:
                        weight = 0

                    if weight:
                        arena_hard_battles = pd.concat(
                            [arena_hard_battles, pd.DataFrame([output] * weight)]
                        )
        return arena_hard_battles

    def calculate_stats_for_judgement(self, judgement, num_rounds):
        battles = self.get_battles_from_judgment(
            list(self.judgement_dfs.values()) + [judgement]
        )
        bootstrap_online_elo = self.compute_mle_elo(battles)

        np.random.seed(42)
        bootstrap_elo_lu = self.get_bootstrap_result(
            battles, self.compute_mle_elo, num_rounds
        )

        stats = pd.DataFrame()
        stats["results"] = None
        stats["results"] = stats["results"].astype("object")

        for i, model in enumerate(bootstrap_online_elo.index):
            assert model in bootstrap_elo_lu.columns

            stats.at[i, "model"] = model
            stats.at[i, "score"] = bootstrap_online_elo[model]
            stats.at[i, "lower"] = np.percentile(bootstrap_elo_lu[model], 2.5)
            stats.at[i, "upper"] = np.percentile(bootstrap_elo_lu[model], 97.5)
            stats.at[i, "results"] = bootstrap_elo_lu[model].tolist()

        decimal = 0
        stats = stats.astype({"score": int, "lower": int, "upper": int})

        stats.sort_values(by="score", ascending=False, inplace=True)
        for _, row in stats.iterrows():
            interval = str(
                (
                    round(row["lower"] - row["score"], decimal),
                    round(row["upper"] - row["score"], decimal),
                )
            )

        return stats

    def evaluate(self, router, num_results):
        router_name = str(router)
        num_rounds = 100

        if router_name not in self.cache or router_name in self.overwrite_cache:
            if router.NO_PARALLEL:
                thresholds = self.questions["turns"].progress_apply(
                    # Only use first turn for routing
                    lambda turn: router.calculate_threshold(turn[0]["content"])
                )
            else:
                thresholds = self.questions["turns"].parallel_apply(
                    lambda turn: router.calculate_threshold(turn[0]["content"])
                )
            self.cache[router_name] = thresholds
            np.save(f"cache/eval/arena_hard/thresholds_cache.npy", self.cache)
        else:
            thresholds = self.cache[router_name]

        _, cutoffs = pd.qcut(thresholds, num_results, retbins=True)
        print(f"Calculated cutoffs for {router_name}: {cutoffs}")
        questions = self.questions[["question_id", "turns"]]
        questions["threshold"] = thresholds

        for i, cutoff in enumerate(cutoffs):
            questions["routed_model"] = np.where(
                (
                    questions["threshold"] >= cutoff
                    if i != len(cutoffs) - 1
                    else questions["threshold"] > cutoff
                ),
                MODEL_LIST[1],
                MODEL_LIST[0],
            )
            model_counts = questions["routed_model"].value_counts().to_dict()
            if MODEL_LIST[0] not in model_counts:
                model_counts[MODEL_LIST[0]] = 0
            if MODEL_LIST[1] not in model_counts:
                model_counts[MODEL_LIST[1]] = 0

            assert questions["question_id"].equals(
                self.gpt4_judgements["question_id"]
            ) and questions["question_id"].equals(
                self.mixtral_judgements["question_id"]
            )

            router_judgements = self.gpt4_judgements.where(
                questions["routed_model"] == MODEL_LIST[1], self.mixtral_judgements
            )
            router_judgements["model"] = "router"

            assert (
                len(router_judgements)
                == len(questions)
                == len(self.mixtral_judgements)
                == len(self.gpt4_judgements)
            )

            stats = self.calculate_stats_for_judgement(router_judgements, num_rounds)
            stats = stats.set_index("model")

            # To simplify things, store results for model_accuracy here
            # assumption: this is called before get_model_accuracy, which is true.
            if self.gpt4_accuracy is None:
                self.gpt4_accuracy = stats.loc["gpt-4-0125-preview"]["score"]
            if self.mixtral_accuracy is None:
                self.mixtral_accuracy = stats.loc["Mixtral-8x7B-Instruct-v0.1"]["score"]

            yield cutoff, stats.loc["router"]["score"], model_counts, len(questions)

    def get_model_accuracy(self, model: str) -> float:
        if model == MODEL_LIST[1]:
            return self.gpt4_accuracy
        elif model == MODEL_LIST[0]:
            return self.mixtral_accuracy
        else:
            raise ValueError(f"Model {model} not found")

    def get_optimal_accuracy(self, gpt4_percent: float) -> float:
        max_gpt4_calls = int(len(self.questions) * gpt4_percent)

        def get_games_score(games):
            # Lower is better for the model
            score_map = {"B>>A": -3, "B>A": -1, "A=B": 0, "A>B": 1, "A>>B": 3}

            total = 0

            game1_score = games[0]["score"]
            if game1_score in score_map:
                total += score_map[game1_score]
            else:
                # Treat None as tie
                total += 0

            game2_score = games[1]["score"]
            if game2_score in score_map:
                # game2 is reversed
                total += score_map[game2_score] * -1
            else:
                total += 0

            return total

        combined_judgements = self.gpt4_judgements.merge(
            self.mixtral_judgements,
            on=["question_id"],
            how="left",
            suffixes=("_gpt4", "_mixtral"),
        )
        combined_judgements["score_gpt4"] = combined_judgements["games_gpt4"].apply(
            get_games_score
        )
        combined_judgements["score_mixtral"] = combined_judgements[
            "games_mixtral"
        ].apply(get_games_score)
        combined_judgements["diff"] = (
            combined_judgements["score_gpt4"] - combined_judgements["score_mixtral"]
        )

        combined_judgements = combined_judgements.sort_values(
            by=["diff"], ascending=True
        ).reset_index(drop=True)

        # If diff < 0, means GPT-4 is better
        if len(combined_judgements[combined_judgements["diff"] < 0]) > max_gpt4_calls:
            combined_judgements.loc[:max_gpt4_calls, "games"] = combined_judgements.loc[
                :max_gpt4_calls, "games_gpt4"
            ]
            combined_judgements.loc[max_gpt4_calls:, "games"] = combined_judgements.loc[
                max_gpt4_calls:, "games_mixtral"
            ]
        else:
            combined_judgements["games"] = combined_judgements["games_gpt4"].where(
                combined_judgements["diff"] < 0, combined_judgements["games_mixtral"]
            )
        combined_judgements = combined_judgements[["question_id", "games"]]
        combined_judgements["model"] = "optimal"

        assert (
            len(self.gpt4_judgements)
            == len(self.mixtral_judgements)
            == len(combined_judgements)
        )

        stats = self.calculate_stats_for_judgement(combined_judgements, num_rounds=100)
        return stats[stats["model"] == "optimal"]["score"].values[0]

    def exit(self):
        pass
