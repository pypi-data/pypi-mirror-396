from langchain_core.prompts import ChatPromptTemplate

planner_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a planner. Create a plan to fulfill the user's request.",
        ),
        ("user", "{input}"),
    ]
)
