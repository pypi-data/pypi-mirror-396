"""Chat component for the Gradio UI."""
from __future__ import annotations

import importlib.util
from typing import Callable

from hayagriva.exceptions import MissingDependencyError


def chat_box(on_submit: Callable):
    if importlib.util.find_spec("gradio") is None:
        raise MissingDependencyError(
            "gradio is required for the UI. Install with `pip install gradio`."
        )
    import gradio as gr

    chatbot = gr.Chatbot(label="Hayagriva Chat")
    msg = gr.Textbox(label="Ask a question", placeholder="Type your question...")

    def stream_chat(message, history):
        history = history or []

        # Append user message in new ChatMessage dict format
        history.append({"role": "user", "content": message})

        # Prepare assistant message placeholder
        assistant_msg = {"role": "assistant", "content": ""}
        history.append(assistant_msg)

        # Stream tokens
        for token in on_submit(message):
            assistant_msg["content"] += token
            yield history

    # Submit handler with streaming enabled
    msg.submit(
        stream_chat,
        inputs=[msg, chatbot],
        outputs=[chatbot],
    )

    return chatbot, msg