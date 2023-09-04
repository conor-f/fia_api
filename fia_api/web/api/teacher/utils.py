import uuid

import openai

from fia_api.settings import settings
from fia_api.web.api.teacher.schema import TeacherConverseResponse, TeacherResponse

openai.api_key = settings.openai_api_key

PROMPTS = {
    "p1": {
        "role": "system",
        "content": """You are an expert German language teacher. You hold basic conversations in German with users. You actively engage with the conversation and keep a pleasant tone. You use a simple vocabulary that the user can understand. If they don't understand you, use simpler words. If they understand you easily, use more complex words. Your response is in the following JSON object:

{
    "mistakes": A list of JSON objects. There is one object for each mistake
    made in the users message. Each object has an English language explanation
    and shows the part of the sentence the mistake was in. If there were no grammar mistakes, the list is empty.
    "fluency": A score from 0-100 of how natural sounding the users message was.
    "conversation_response": A string in the German language to continue the conversation with the user.
}

You must respond to every message in this exact structure. You must not respond in any other way.""",
    },
    "p2": {
        "role": "system",
        "content": """You are a German language teacher analyzing sentences.  You always respond in a JSON object. The JSON object has the following members: mistakes, response. mistakes is a list of every grammer/spelling/vocabulary mistake the user made. response is the German language response to the users message.""",
    },
    # BEST SO FAR!
    "p3": {
        "role": "system",
        "content": """You are a German language teacher. You correct any English words in a users message. You also explain any spelling or grammar mistakes they make in English. You are having a conversation with them. Don't translate every word, only the words that the user typed in English.""",
    },
}


def get_response(conversation_id: str, message: str) -> TeacherConverseResponse:
    """
    Given the conversation ID, and a new message to add to it, store the
    message, get the response, store that, and return it.

    :param conversation_id: String ID representing the conversation.
    :param message: String message the user wants to send.
    :return: TeacherResponse
    """
    # Get previous messages in conversation_id
    message_context = []
    message_context.append(
        {
            "role": "user",
            "content": message,
        },
    )

    chat_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=message_context,
        functions=[
            {
                "name": "get_answer_for_user_query",
                "description": "Get user language learning mistakes and a sentence to continue the conversation",
                "parameters": TeacherResponse.schema(),
            },
        ],
        function_call={"name": "get_answer_for_user_query"},
    )

    # Store the chat response in the DB...
    teacher_response = chat_response.choices[0].message.function_call.arguments
    # Store the token usage in the DB...
    # for key in chat_completion.usage.keys():
    #     token_usage[key] += chat_completion.usage[key]

    return TeacherConverseResponse(
        conversation_id=conversation_id,
        response=teacher_response,
    )


def initialize_conversation(message: str) -> TeacherConverseResponse:
    """
    Set up the DB with the initial conversation prompt and return the new
    conversation ID, along with the first response from the model.

    :param message: The message to start the conversation with.
    """
    conversation_id = str(uuid.uuid4())
    # TODO: Add the prompt and store it in a new conversation for the user in
    # the DB.
    # context.append(PROMPTS["p3"])
    return get_response(conversation_id, message)
