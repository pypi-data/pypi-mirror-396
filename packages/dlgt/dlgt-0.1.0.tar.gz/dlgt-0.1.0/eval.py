


import pytest
# from delegate.testing import Evalator, mark_success

agent = Agent(
    tools=[...]
)

def test_friendly_greeting():
    evaluator = Evalator(
        test_criteria="Check the agent greets the user in a friendly manner to a generic message."
    )

    initial_message = "Hello, how are you?"
    conversations = [{'role': 'user', 'content': initial_message}]

    response = agent.run(initial_message)
    conversations.append({'role': 'assistant', 'content': response})

    # Assert via pytest that mark_success was called as a function
    assert mark_success.called

    return conversations, evaluator.get_result()

def test_friendly_greeting():
    evaluator = Evalator(
        test_criteria="Check the agent calls the data retriever, and runs a query on the cleaned_customers table"
    )

    with mocked_async_get(url="http://localhost:8000/private/123/datasets/", json=[]) as mock_get:

        initial_message = ""
        conversations = [{'role': 'user', 'content': initial_message}]

        response = agent.run(initial_message)
        conversations.append({'role': 'assistant', 'content': response})

        # Assert via pytest that mark_success was called as a function
        assert mark_success.called

        return conversations, evaluator.get_result()






  
















