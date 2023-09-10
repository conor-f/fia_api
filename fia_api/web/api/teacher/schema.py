from typing import List, Optional, Union

from pydantic import BaseModel, Field


# OpenAI Related Response Models:
class Mistake(BaseModel):
    """A single Mistake a user made in their message."""

    incorrect_section: str = Field(
        description=(
            "The section of the sentence of the user message the grammar "
            "mistake is in"
        ),
    )
    corrected_section: str = Field(
        description="The corrected section of the sentence in German",
    )
    explanation: str = Field(
        description=(
            "The English language explanation of why this section of the "
            "sentence is incorrect. Give details such as if it is using the "
            "wrong gender/suffix, if the verb conjugation is wrong, etc. If "
            "the sentence is correct, but there is a better way to phrase it, "
            "explain this too."
        ),
    )


class Translation(BaseModel):
    """A word or phrase the user wants translated."""

    phrase: str = Field(
        description=(
            'The word or phrase the user wants translated. e.g. "Book", '
            "'gerne', \"lesen\""
        ),
    )
    translated_phrase: str = Field(
        description=(
            "The translation of the word or phrase in context of the "
            "sentence. If it is a noun, include the correct gender. "
            "e.g. Das Buch, Die Hande, etc"
        ),
    )


class LearningMoment(BaseModel):
    """A moment in a conversation a user can learn from."""

    moment: Union[Mistake, Translation] = Field(
        description=(
            "A single language learning mistake found in a section of the "
            "users message"
        ),
    )


# This is returned by the model looking for mistakes in the user sentence.
class LearningMoments(BaseModel):
    """A list of individual LearningMoment objects."""

    learning_moments: List[LearningMoment] = Field(
        description=(
            "A list of language learning mistakes in the users message. "
            "There should be one LearningMoment per individual mistake in "
            "the sentence."
        ),
    )


# This is returned by the model trying to continue on the conversation with the
# user in an educational way.
class ConversationContinuation(BaseModel):
    """Basic wrapper to supply description data to OpenAI."""

    message: str = Field(
        description=(
            "This is the response to to users message. You should always "
            "try respond in German. If the user doesn't understand, then try "
            "to use even more simple German in your response until you can "
            "only use English. Responding in English is a last resort."
        ),
    )


class TeacherResponse(BaseModel):
    """Represents the entire response from the "Teacher"."""

    learning_moments: LearningMoments
    conversation_response: ConversationContinuation


class TeacherConverseRequest(BaseModel):
    """Request object for calls to the Teacher to continue a conversation."""

    # If conversation_id is "new", then start a new conversation.
    conversation_id: str
    message: str


class ConversationSnippet(BaseModel):
    """A simple preview of a conversation."""

    conversation_id: str
    conversation_intro: str


class UserConversationList(BaseModel):
    """A list of a user's conversations with the conversation ID and details."""

    conversations: List[ConversationSnippet]


class ConversationElement(BaseModel):
    """A single part of a conversation. Either from the user or system."""

    role: str
    message: str
    learning_moments: Optional[LearningMoments] = None


class ConversationResponse(BaseModel):
    """A conversation a user had."""

    conversation_id: str
    conversation: List[ConversationElement]
