from sqlmodel import Session, select
from datetime import datetime
from typing import List
import logging
from ..models.conversation import Conversation, Message
from ..models.mcp_models import ConversationRequest, MessageRequest

logger = logging.getLogger(__name__)


async def create_conversation(session: Session, user_id: int, title: str) -> Conversation:
    """
    Create a new conversation for a user.

    Args:
        session: Database session
        user_id: ID of the user creating the conversation
        title: Title of the conversation

    Returns:
        Created conversation
    """
    conversation = Conversation(
        user_id=user_id,
        title=title
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    logger.info(f"Created conversation {conversation.id} for user {user_id}")
    return conversation


async def get_conversations(session: Session, user_id: int) -> List[Conversation]:
    """
    Get all conversations for a user, ordered by creation date (newest first).

    Args:
        session: Database session
        user_id: ID of the user

    Returns:
        List of conversations
    """
    statement = select(Conversation).where(Conversation.user_id == user_id).order_by(Conversation.created_at.desc())
    conversations = session.exec(statement).all()
    logger.info(f"Retrieved {len(conversations)} conversations for user {user_id}")
    return list(conversations)


async def create_message(session: Session, conversation_id: int, role: str, content: str) -> Message:
    """
    Add a message to a conversation.

    Args:
        session: Database session
        conversation_id: ID of the conversation
        role: Role of the message sender (user, assistant, system)
        content: Content of the message

    Returns:
        Created message
    """
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content
    )
    session.add(message)
    session.commit()
    session.refresh(message)
    logger.info(f"Added message {message.id} to conversation {conversation_id}")
    return message


async def get_messages(session: Session, conversation_id: int) -> List[Message]:
    """
    Get all messages for a conversation, ordered by timestamp (oldest first).

    Args:
        session: Database session
        conversation_id: ID of the conversation

    Returns:
        List of messages
    """
    statement = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.timestamp.asc())
    messages = session.exec(statement).all()
    logger.info(f"Retrieved {len(messages)} messages for conversation {conversation_id}")
    return list(messages)