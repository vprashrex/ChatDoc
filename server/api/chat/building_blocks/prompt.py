template = """
    Use only the following context to answer the question:
    {context}
    Ensure that the answer is correct and complete with respect to the question and context provided.
    Question: {question}

    If the Question is casual and is not realted to the the context then just simply answer it.
    Don't Respond like this It seems like you didn't ask a question. You provided a context that appears to be a resume or a research paper, but there is no question for me to answer. Please provide a question, and I'll do my best to answer it based on the context you provided.

    Don't say this Based on the provided context. response should be normal and casual. your chat should be casual and more natural
    Response should not contain this response The criteria for eligibility is not explicitly stated in the provided context. 
"""