
import os

from fake_db import DB_PATH, seed_db

MODEL = "openai/gpt-oss-20b"


def build_chain(db):
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.runnables import RunnableLambda, RunnablePassthrough
    from langchain_groq import ChatGroq

    llm = ChatGroq(model=MODEL, temperature=0)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert {dialect} developer. Given the schema below, "
                "write ONE syntactically correct SQL statement that fulfils the "
                "user's request. Any statement type is allowed (SELECT, INSERT, "
                "UPDATE, DELETE, CREATE, DROP, ...). Use only tables/columns in "
                "the schema unless the user explicitly asks to create new ones. "
                "Select ONLY the columns the user asks for. For example, 'show all "
                "data in column quantity' means SELECT quantity FROM orders, never "
                "SELECT *. Use SELECT * only when the user asks for all columns or "
                "the whole table. Do not add a LIMIT unless the user asks for one. "
                "Return ONLY the SQL, no explanation, no markdown fences.\n\n"
                "Schema:\n{table_info}",
            ),
            ("human", "{question}"),
        ]
    )
 

    def clean_sql(text: str) -> str:
        return text.replace("```sql", "").replace("```", "").strip()

    return (
        RunnablePassthrough.assign(
            table_info=lambda _: db.get_table_info(),
            dialect=lambda _: db.dialect,
        )
        | prompt
        | llm
        | StrOutputParser()
        | RunnableLambda(clean_sql)
    )


def main() -> None:
    from langchain_community.utilities import SQLDatabase

    if not os.getenv("GROQ_API_KEY"):
        raise SystemExit("Set GROQ_API_KEY first:  export GROQ_API_KEY=...")

    if not os.path.exists(DB_PATH):
        seed_db()
        print(f"Created fake database: {DB_PATH}")

    db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")
    chain = build_chain(db)

    print("\nText-to-SQL chat (Groq). Tables: customers, products, orders")
    print("Commands: schema | reset | exit\n")

    while True:
        try:
            question = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not question:
            continue
        if question.lower() in {"exit", "quit", "q"}:
            print("Bye!")
            break
        if question.lower() == "schema":
            print(db.get_table_info())
            continue
        if question.lower() == "reset":
            seed_db()
            db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")
            chain = build_chain(db)
            print("Database reset.")
            continue

        try:
            sql = chain.invoke({"question": question})
            print(f"\nSQL> {sql}\n")
            result = db.run(sql)
            print(f"Result:\n{result if result else '(OK, no rows returned)'}\n")
        except Exception as e:  # show errors but keep the chat alive
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()
