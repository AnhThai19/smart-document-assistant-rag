import json
import time
from pathlib import Path
from typing import Dict, List

from app.services.embedder import embed_text
from app.services.vector_store import search_similar_chunks


TEST_FILE = Path(__file__).parent / "test_questions.json"


def load_test_questions() -> List[Dict]:
    with open(TEST_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def contains_expected_keyword(text: str, expected_keywords: List[str]) -> bool:
    text_lower = text.lower()

    for keyword in expected_keywords:
        if keyword.lower() in text_lower:
            return True

    return False


def evaluate_question(
    question: str,
    expected_keywords: List[str],
    document_id: str,
    user_id: str,
    top_k: int = 3,
) -> Dict:
    start_time = time.perf_counter()

    query_embedding = embed_text(question)

    results = search_similar_chunks(
        query_embedding=query_embedding,
        top_k=top_k,
        document_id=document_id,
        user_id=user_id,
    )

    latency = time.perf_counter() - start_time

    retrieved_text = "\n".join(
        [result.get("text", "") for result in results]
    )

    hit = contains_expected_keyword(
        text=retrieved_text,
        expected_keywords=expected_keywords,
    )

    top_score = results[0]["score"] if results else 0.0

    return {
        "question": question,
        "hit": hit,
        "latency_seconds": round(latency, 4),
        "top_score": top_score,
        "results": results,
    }


def main():
    print("RAG Retrieval Evaluation")
    print("=" * 60)

    document_id = input("Enter document_id to evaluate: ").strip()
    user_id = input("Enter user_id [default: demo_user]: ").strip() or "demo_user"

    if not document_id:
        print("document_id is required.")
        return

    test_questions = load_test_questions()

    total = len(test_questions)
    hits = 0
    latencies = []

    detailed_results = []

    for index, item in enumerate(test_questions, start=1):
        question = item["question"]
        expected_keywords = item.get("expected_keywords", [])

        print(f"\n[{index}/{total}] Question: {question}")

        result = evaluate_question(
            question=question,
            expected_keywords=expected_keywords,
            document_id=document_id,
            user_id=user_id,
            top_k=3,
        )

        detailed_results.append(result)

        if result["hit"]:
            hits += 1
            status = "PASS"
        else:
            status = "FAIL"

        latencies.append(result["latency_seconds"])

        print(f"Status: {status}")
        print(f"Latency: {result['latency_seconds']}s")
        print(f"Top score: {result['top_score']}")

        if result["results"]:
            print("Top retrieved text:")
            print(result["results"][0].get("text", "")[:300])
        else:
            print("No results retrieved.")

    accuracy = hits / total if total > 0 else 0
    avg_latency = sum(latencies) / len(latencies) if latencies else 0

    print("\n" + "=" * 60)
    print("Evaluation Summary")
    print("=" * 60)
    print(f"Total questions: {total}")
    print(f"Hits: {hits}")
    print(f"Retrieval accuracy: {accuracy:.2%}")
    print(f"Average latency: {avg_latency:.4f}s")

    output_path = Path(__file__).parent / "retrieval_eval_results.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            {
                "document_id": document_id,
                "user_id": user_id,
                "total_questions": total,
                "hits": hits,
                "retrieval_accuracy": accuracy,
                "average_latency_seconds": avg_latency,
                "details": detailed_results,
            },
            file,
            ensure_ascii=False,
            indent=2,
        )

    print(f"\nSaved detailed results to: {output_path}")


if __name__ == "__main__":
    main()