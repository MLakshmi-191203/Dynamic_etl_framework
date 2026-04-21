from rag.vector_store import VectorStore
from rag.rag_pipeline import generate_answer

# ✅ This is required for Streamlit UI
def ask_question(query):

    vs = VectorStore()
    vs.load()

    answer = generate_answer(query, vs)

    return answer


# 👇 Keep CLI also (optional)
def main():

    vs = VectorStore()
    vs.load()

    print("🤖 Ask your ETL questions (type 'exit' to quit)\n")

    while True:

        query = input("👉 You: ")

        if query.lower() == "exit":
            break

        answer = generate_answer(query, vs)

        print("\n💡 Answer:\n", answer)
        print("-" * 50)


if __name__ == "__main__":
    main()