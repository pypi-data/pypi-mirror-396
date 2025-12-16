"""
GNS3 Copilot - AI-Powered Network Engineering Assistant

This module implements the main Streamlit web application for GNS3 Copilot,
an AI-powered assistant designed to help network engineers with GNS3-related
tasks through a conversational chat interface.

Features:
- Real-time chat interface with streaming responses
- Integration with LangChain agents for intelligent conversation
- Tool calling support for GNS3 network operations
- Message history and session state management
- Support for multiple message types (Human, AI, Tool messages)
- Interactive tool call and response visualization

The application leverages:
- Streamlit for the web UI
- LangGraph for AI agent functionality
- Custom GNS3 integration tools
- Session-based conversation tracking with unique thread IDs

Usage:
Run this module directly to start the GNS3 Copilot web interface:
    streamlit run app.py

Note: Requires proper configuration of GNS3 server and API credentials.
"""
import json
import uuid
import streamlit as st
from langchain.messages import ToolMessage, HumanMessage, AIMessage
from gns3_copilot.agent import agent, langgraph_checkpointer
from gns3_copilot.log_config import setup_logger
from gns3_copilot.public_model import format_tool_response

logger = setup_logger("chat")

# get all thread_id from checkpoint database.
def list_thread_ids(checkpointer):
    """
    Get all unique thread IDs from LangGraph checkpoint database.
    
    Args:
        checkpointer: LangGraph checkpointer instance.
    
    Returns:
        list: List of unique thread IDs ordered by most recent activity.
              Returns empty list on error or if table doesn't exist.
    """
    try:
        res = checkpointer.conn.execute(
            "SELECT DISTINCT thread_id FROM checkpoints ORDER BY rowid DESC"
        ).fetchall()
        return [r[0] for r in res]
    except Exception as e:
        # Table might not exist yet, return empty list
        logger.debug("Error listing thread IDs (table may not exist): %s", e)
        return []

def new_session():
    """
    Create a new chat session by generating a unique thread ID and resetting session state.
    
    Initializes a fresh conversation session with a new UUID, clears existing session data,
    and resets the UI session selector to the default option.
    
    Side Effects:
        - Updates st.session_state with new thread_id
        - Clears current_thread_id and state_history
        - Resets session_select to default option
        - Logs session creation
    """
    new_tid = str(uuid.uuid4())
    # real new thread id
    st.session_state["thread_id"] = new_tid
    # Clear your own state
    st.session_state["current_thread_id"] = None
    st.session_state["state_history"] = None
    # Reset the dropdown menu to the first option ("(Please select session)", None)
    st.session_state["session_select"] = session_options[0]
    logger.debug("New Session created with thread_id= %s", new_tid)

# Initialize session state for thread ID
if "thread_id" not in st.session_state:
    # If thread_id is not in session_state, create and save a new one
    st.session_state["thread_id"] = str(uuid.uuid4())

current_thread_id = st.session_state["thread_id"]

# streamlit UI
st.set_page_config(page_title="GNS3 Copilot", layout="wide")

# siderbar info
with st.sidebar:

    thread_ids = list_thread_ids(langgraph_checkpointer)

    # Display name/value are title and id
    # The first option is an empty/placeholder selection
    session_options = [("(Please select session)", None)]

    for tid in thread_ids:
        ckpt = langgraph_checkpointer.get({"configurable": {"thread_id": tid}})
        title = (
            ckpt.get("channel_values", {}).get("conversation_title")
            if ckpt else None
        ) or "New Session"
        # 相同的title name导致了ui界面上选择会话出现的总是选中同一个thread id的问题。
        # 使用thread_id的部分内容来避免相同的title name
        unique_title = f"{title} ({tid[:6]})"
        session_options.append((unique_title, tid))

    logger.debug("session_options : %s", session_options)

    selected = st.selectbox(
        "Session History", 
        options=session_options,
        format_func=lambda x: x[0],   # view conversation_title
        key="session_select",          # new key for state management
    )

    title, selected_thread_id = selected

    logger.debug("selectbox selected : %s, %s", title, selected_thread_id)

    st.markdown(f"Current Session: `{title} thread_id: {selected_thread_id}`")

    col1, col2 = st.columns(2)
    with col1:
        st.button(
            "New Session",
            on_click=new_session,
            help="Create a new session"
            )
    with col2:
        # Only allow deletion if the user has selected a valid thread_id
        if selected_thread_id and st.button(
            "Delete",
            help="Delete current selection session"
            ):
            langgraph_checkpointer.delete_thread(thread_id=selected_thread_id)
            st.success(f"_Delete Success_: {title} \n\n _Thread_id_: `{selected_thread_id}`")
            st.rerun()

    # If a valid thread id is selected, load the historical messages
    if selected_thread_id:
        # Store the selected ID for use in the main interface
        st.session_state["current_thread_id"] = selected_thread_id
        st.session_state["state_history"] = agent.get_state(
            {
                "configurable": {"thread_id": selected_thread_id}
                }
            )

# StateSnapshot state exapmle test/langgraph_checkpoint.json file
# Display previous messages from state history
if st.session_state.get("state_history") is not None:
    # StateSnapshot values dictionary
    values_dict = st.session_state["state_history"].values
    message_to_render = values_dict.get("messages", [])

    # Track current open assistant message block
    current_assistant_block = None

    # StateSnapshot values messages list
    for message_object in message_to_render:
        # Handle different message types
        if isinstance(message_object, HumanMessage):
            # Close any open assistant chat message block before starting a new user message
            if current_assistant_block is not None:
                current_assistant_block.__exit__(None, None, None)
                current_assistant_block = None
            # UserMessage
            with st.chat_message("user"):
                st.markdown(message_object.content)

        elif isinstance(message_object, (AIMessage, ToolMessage)):
            # Open a new assistant chat message block if none is open
            if current_assistant_block is None:
                current_assistant_block = st.chat_message("assistant")
                current_assistant_block.__enter__()

            # Handle AIMessage with tool_calls
            if isinstance(message_object, AIMessage):
                # AIMessage content
                # adapted for gemini
                # Check if content is a list and safely extract the first text element
                if (
                    isinstance(message_object.content, list)
                    and
                    message_object.content
                    and
                    'text' in message_object.content[0]
                    ):
                    st.markdown(message_object.content[0]['text'])
                # Plain string content
                elif isinstance(message_object.content, str):
                    st.markdown(message_object.content)
                # AIMessage tool_calls
                if isinstance(message_object.tool_calls, list) and message_object.tool_calls:
                    for tool in message_object.tool_calls:
                        tool_id = tool.get('id', 'UNKNOWN_ID')
                        tool_name = tool.get('name', 'UNKNOWN_TOOL')
                        tool_args = tool.get('args', {})
                        # Display tool call details
                        with st.expander(
                            f"**Tool Call:** {tool_name} `call_id: {tool_id}`",
                            expanded=False
                            ):
                            st.json({
                                "name": tool_name,
                                "id": tool_id,
                                "args": tool_args,
                                "type": "tool_call"
                            }, expanded=True)
            # Handle ToolMessage
            if isinstance(message_object, ToolMessage):
                content_pretty = format_tool_response(message_object.content)
                with st.expander(
                    f"**Tool Response** `call_id: {message_object.tool_call_id}`",
                    expanded=False
                    ):
                    st.json(json.loads(content_pretty), expanded=2)

    # Close any remaining open assistant chat message block
    if current_assistant_block is not None:
        current_assistant_block.__exit__(None, None, None)

# Unique thread ID for each session
# If a session is selected, continue the conversation using its thread ID;
# otherwise, initialize a new thread ID.
if selected_thread_id:
    config = {
        "configurable": {
            "thread_id": st.session_state["current_thread_id"],
            "max_iterations": 50
            },
        "recursion_limit": 28
        }
else:
    config = {
        "configurable": {
            "thread_id": current_thread_id,
            "max_iterations": 50
            },
        "recursion_limit": 28
        }

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):

        active_text_placeholder = st.empty()
        current_text_chunk = ""
        # Core aggregation state: only stores currently streaming tool information
        # Structure: {'id': str, 'name': str, 'args_string': str} or None
        current_tool_state = None

        # Stream the agent response
        for chunk in agent.stream(
            {
                "messages": [HumanMessage(content=prompt)],
             },
            config=config,
            stream_mode="messages"
            ):

            for msg in chunk:
                #with open('log.txt', "a", encoding='utf-8') as f:
                #    f.write(f"{msg}\n\n")

                if isinstance(msg, AIMessage):
                    # adapted for gemini
                    # Check if content is a list and safely extract the first text element
                    if isinstance(msg.content, list) and msg.content and 'text' in msg.content[0]:
                        actual_text = msg.content[0]['text']
                        # Now actual_text is the clean text you need
                        current_text_chunk += actual_text
                        active_text_placeholder.markdown(
                            current_text_chunk, unsafe_allow_html=True)

                    elif isinstance(msg.content, str):
                        current_text_chunk += str(msg.content)
                        active_text_placeholder.markdown(
                            current_text_chunk, unsafe_allow_html=True)

                    # Get metadata (ID and name) from tool_calls
                    if msg.tool_calls:
                        for tool in msg.tool_calls:
                            tool_id = tool.get('id')
                            # Only when ID is not empty, consider it as the start of a new tool call
                            if tool_id:
                                # Initialize current tool state (this is the only time to get ID)
                                # Note: only one tool can be called at a time
                                current_tool_state = {
                                    "id": tool_id, 
                                    "name": tool.get('name', 'UNKNOWN_TOOL'),
                                    "args_string": "" ,
                                }

                    # Concatenate parameter strings from tool_call_chunk
                    if hasattr(msg, 'tool_call_chunks') and msg.tool_call_chunks:
                        if current_tool_state:
                            tool_data = current_tool_state

                            for chunk_update in msg.tool_call_chunks:
                                args_chunk = chunk_update.get('args', '')

                                    # Core: string concatenation
                                if isinstance(args_chunk, str):
                                    tool_data['args_string'] += args_chunk

                    # Determine if the tool_calls_chunks output is complete and
                    # display the st.expander() for tool_calls
                    if (
                        msg.response_metadata.get('finish_reason') == 'tool_calls'
                        or (
                            msg.response_metadata.get('finish_reason') == 'STOP'
                            and
                            current_tool_state is not None
                            )
                        ):

                        tool_data = current_tool_state
                        # Parse complete parameter string
                        parsed_args = {}
                        try:
                            parsed_args = json.loads(tool_data['args_string'])
                        except json.JSONDecodeError:
                            parsed_args = {"error": "JSON parse failed after stream complete."}

                        # Serialize the tool_input value in parsed_args to a JSON array
                        # for expansion when using st.json
                        try:
                            command_list = json.loads(parsed_args['tool_input'])
                            parsed_args['tool_input'] = command_list
                        except (json.JSONDecodeError, KeyError, TypeError):
                            pass

                        # Build the final display structure that meets your requirements
                        display_tool_call = {
                            "name": tool_data['name'],
                            "id": tool_data['id'],
                            # Inject tool_input structure
                            "args": parsed_args, 
                            "type": tool_data.get('type', 'tool_call') # Maintain completeness
                        }

                        # Update Call Expander, display final parameters (collapsed)
                        with st.expander(
                            f"**Tool Call:** {tool_data['name']} `call_id: {tool_data['id']}`",
                            expanded=False
                        ):
                            # Use the final complete structure
                            st.json(display_tool_call, expanded=False)

                elif isinstance(msg, ToolMessage):
                    # Clear state after completion, ready to receive next tool call
                    current_tool_state = None

                    content_pretty = format_tool_response(msg.content)

                    with st.expander(
                        f"**Tool Response** `call_id: {msg.tool_call_id}`",
                        expanded=False
                    ):
                        st.json(json.loads(content_pretty), expanded=False)

                    active_text_placeholder = st.empty()
                    current_text_chunk = ""

    # After the interaction, update the session state with the latest StateSnapshot
    state_history = agent.get_state(config)

    # Avoid updating if state_history is empty
    if not state_history[0]:
        pass
    else:
        # Update session state
        st.session_state["state_history"] = state_history
        #print(state_history)
        #with open('state_history.txt', "a", encoding='utf-8') as f:
        #    f.write(f"{state_history}\n\n")
