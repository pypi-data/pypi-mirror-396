"""
DeepSeek-safe LLM wrapper for CrewAI.

This module provides a wrapper around CrewAI's LLM class that sanitizes message
histories to prevent the "Invalid consecutive assistant/user message" error that
DeepSeek's API returns when consecutive messages have the same role.

The wrapper ensures messages alternate between user and assistant roles by:
1. Merging consecutive messages of the same role into a single message
2. Ensuring the first message is always from the user
3. Preserving all semantic content while maintaining API compatibility
4. Recursively fixing any consecutive messages that slip through

Usage:
    from traia_tools import DeepSeekSafeLLM
    
    llm = DeepSeekSafeLLM(
        model="deepseek/deepseek-reasoner",
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        temperature=1.0
    )
"""

import logging
from typing import Any, Dict, List

from crewai import LLM


class DeepSeekSafeLLM(LLM):
    """
    A wrapper around CrewAI's LLM that sanitizes message histories for DeepSeek.
    
    DeepSeek's API does not support consecutive messages from the same role
    (e.g., two assistant messages in a row). This wrapper automatically handles
    message sanitization to prevent API errors while preserving conversation context.
    
    This class overrides _format_messages_for_provider() which is called internally
    by CrewAI before sending messages to litellm.completion().
    
    Attributes:
        merge_consecutive_messages: If True, merges consecutive same-role messages.
                                   If False, only keeps the last message of each
                                   consecutive block.
        ultra_verbose: If True, logs full message contents for debugging
    """
    
    def __init__(
        self,
        *args,
        merge_consecutive_messages: bool = True,
        ultra_verbose: bool = False,
        **kwargs
    ):
        """
        Initialize DeepSeekSafeLLM with message sanitization enabled.
        
        Args:
            *args: Positional arguments passed to parent LLM class
            merge_consecutive_messages: Whether to merge consecutive messages (True)
                                       or keep only the last one (False)
            ultra_verbose: Whether to log full message contents for debugging
            **kwargs: Keyword arguments passed to parent LLM class
        """
        super().__init__(*args, **kwargs)
        self.merge_consecutive_messages = merge_consecutive_messages
        self.ultra_verbose = ultra_verbose
        
        logging.info(
            f"Initialized DeepSeekSafeLLM with model={self.model}, "
            f"merge_consecutive_messages={merge_consecutive_messages}, "
            f"ultra_verbose={ultra_verbose}"
        )
    
    def _log_messages(self, messages: List[Dict[str, Any]], stage: str):
        """
        Log messages at various stages with optional full content.
        
        Args:
            messages: List of message dictionaries
            stage: Description of the current stage (e.g., "INPUT", "SANITIZED")
        """
        logging.info(f"=== {stage} === ({len(messages)} messages)")
        
        for i, msg in enumerate(messages):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            
            # Show first 100 chars by default, full content if ultra_verbose
            if self.ultra_verbose:
                content_preview = content
            else:
                content_preview = (content[:100] + "...") if len(str(content)) > 100 else content
            
            logging.info(f"  [{i}] role={role}, content_len={len(str(content))}")
            if self.ultra_verbose:
                logging.debug(f"      content: {content_preview}")
    
    def _fix_consecutive_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Recursively fix any consecutive same-role messages that remain.
        
        This is a safety net that runs after the main sanitization to catch
        any edge cases that slip through.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            List with no consecutive same-role messages
        """
        if len(messages) <= 1:
            return messages
        
        # Keep fixing until no consecutive messages remain
        max_iterations = len(messages)  # Prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            has_consecutive = False
            fixed_messages = []
            i = 0
            
            while i < len(messages):
                current_msg = messages[i]
                
                # Look ahead to find all consecutive same-role messages
                j = i + 1
                while j < len(messages) and messages[j]["role"] == current_msg["role"]:
                    j += 1
                
                # If we found consecutive messages, merge them
                if j > i + 1:
                    has_consecutive = True
                    consecutive_count = j - i
                    
                    if self.merge_consecutive_messages:
                        # Merge all consecutive messages
                        merged_content = "\n\n---\n\n".join([
                            str(messages[k].get("content", "")) 
                            for k in range(i, j)
                        ])
                        fixed_messages.append({
                            "role": current_msg["role"],
                            "content": merged_content
                        })
                        logging.warning(
                            f"FIXED: Merged {consecutive_count} consecutive "
                            f"{current_msg['role']} messages at index {i}"
                        )
                    else:
                        # Keep only the last message
                        fixed_messages.append(messages[j - 1])
                        logging.warning(
                            f"FIXED: Kept last of {consecutive_count} consecutive "
                            f"{current_msg['role']} messages at index {i}"
                        )
                    
                    i = j  # Skip past all the consecutive messages
                else:
                    # No consecutive messages, keep as-is
                    fixed_messages.append(current_msg)
                    i += 1
            
            messages = fixed_messages
            
            if not has_consecutive:
                break
            
            iteration += 1
            logging.debug(f"Fix iteration {iteration}: {len(messages)} messages remain")
        
        return messages
    
    def sanitize_messages(
        self,
        messages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Sanitize message list to ensure no consecutive messages have the same role.
        
        This method:
        1. Ensures the first message is from 'user' (DeepSeek requirement)
        2. Merges or filters consecutive messages of the same role
        3. Preserves all message content and context
        4. Recursively fixes any remaining consecutive messages
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            
        Returns:
            Sanitized list of messages with alternating roles
        """
        if not messages:
            logging.warning("sanitize_messages called with empty message list")
            return messages
        
        # Log input for debugging
        logging.info(
            f"🔍 Sanitizing {len(messages)} messages. "
            f"First role: {messages[0].get('role')}, "
            f"Last role: {messages[-1].get('role')}"
        )
        
        sanitized = []
        assistant_buffer = []
        user_buffer = []
        
        # Ensure first message is from user (DeepSeek requirement)
        first_message = messages[0].copy()
        if first_message.get("role") not in ["user"]:
            logging.info(
                f"Converting first message from '{first_message.get('role')}' "
                f"to 'user' (DeepSeek requirement)"
            )
            first_message["role"] = "user"
        
        # Initialize prev_role based on first message (after conversion)
        prev_role = "user"  # First message is always user after conversion
        
        def flush_assistant_buffer():
            """Merge buffered assistant messages into one message."""
            if assistant_buffer:
                if self.merge_consecutive_messages:
                    # Merge all assistant messages with clear separation
                    combined = "\n\n---\n\n".join(assistant_buffer)
                    sanitized.append({"role": "assistant", "content": combined})
                    logging.debug(
                        f"Merged {len(assistant_buffer)} assistant messages "
                        f"into one ({len(combined)} chars)"
                    )
                else:
                    # Keep only the last assistant message
                    sanitized.append({
                        "role": "assistant",
                        "content": assistant_buffer[-1]
                    })
                    logging.debug(
                        f"Kept last of {len(assistant_buffer)} assistant messages"
                    )
                assistant_buffer.clear()
        
        def flush_user_buffer():
            """Merge buffered user messages into one message."""
            if user_buffer:
                if self.merge_consecutive_messages:
                    # Merge all user messages with clear separation
                    combined = "\n\n---\n\n".join(user_buffer)
                    sanitized.append({"role": "user", "content": combined})
                    logging.debug(
                        f"Merged {len(user_buffer)} user messages "
                        f"into one ({len(combined)} chars)"
                    )
                else:
                    # Keep only the last user message
                    sanitized.append({"role": "user", "content": user_buffer[-1]})
                    logging.debug(
                        f"Kept last of {len(user_buffer)} user messages"
                    )
                user_buffer.clear()
        
        # Process all messages (first message already converted to user)
        for i, msg in enumerate([first_message] + messages[1:]):
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            # Handle system messages by converting to user
            if role == "system":
                role = "user"
                logging.debug(
                    f"Converted system message at index {i} to user message"
                )
            
            # Skip empty content messages
            if not content or (isinstance(content, str) and not content.strip()):
                logging.debug(
                    f"Skipping empty message at index {i} with role '{role}'"
                )
                continue
            
            # Convert content to string if it's a list (some models use list format)
            if isinstance(content, list):
                # Extract text from content list
                text_parts = []
                for item in content:
                    if isinstance(item, dict) and "text" in item:
                        text_parts.append(item["text"])
                    elif isinstance(item, str):
                        text_parts.append(item)
                content = " ".join(text_parts)
                logging.debug(f"Converted list content to string at index {i}")
            
            # Buffer messages by role
            if role == "assistant":
                # Flush user buffer when switching from user to assistant
                if prev_role == "user":
                    flush_user_buffer()
                assistant_buffer.append(content)
                prev_role = "assistant"
            elif role == "user":
                # Flush assistant buffer when switching from assistant to user
                if prev_role == "assistant":
                    flush_assistant_buffer()
                user_buffer.append(content)
                prev_role = "user"
            else:
                # Handle any other roles as user messages
                logging.warning(
                    f"Unknown role '{role}' at index {i}, treating as user message"
                )
                if prev_role == "assistant":
                    flush_assistant_buffer()
                user_buffer.append(content)
                prev_role = "user"
        
        # Flush remaining buffers
        flush_assistant_buffer()
        flush_user_buffer()
        
        # Ensure we have at least one message
        if not sanitized:
            logging.warning(
                "Sanitization resulted in empty message list, "
                "adding default user message"
            )
            sanitized.append({"role": "user", "content": "Please provide a response."})
        
        # CRITICAL: DeepSeek requires the last message to be from user
        # If conversation ends with assistant message, add a user continuation prompt
        if sanitized and sanitized[-1]["role"] == "assistant":
            logging.info(
                "Last message is assistant - adding user continuation prompt "
                "(DeepSeek requirement)"
            )
            sanitized.append({
                "role": "user",
                "content": "Please continue based on the above context."
            })
        
        # Apply recursive fix to catch any edge cases
        sanitized = self._fix_consecutive_messages(sanitized)
        
        # Log output for debugging
        logging.info(
            f"✅ Sanitization complete: {len(messages)} -> {len(sanitized)} messages. "
            f"First role: {sanitized[0].get('role')}, "
            f"Last role: {sanitized[-1].get('role')}"
        )
        
        # Final verification - this should never trigger now
        for i in range(len(sanitized) - 1):
            if sanitized[i]["role"] == sanitized[i + 1]["role"]:
                logging.error(
                    f"❌ CRITICAL: Consecutive {sanitized[i]['role']} messages "
                    f"remain at indices {i} and {i+1} after all fixes!"
                )
                # This indicates a bug in the sanitization logic
                raise RuntimeError(
                    f"Failed to sanitize messages: consecutive {sanitized[i]['role']} "
                    f"messages at indices {i} and {i+1}"
                )
        
        return sanitized
    
    def _format_messages_for_provider(
        self,
        messages: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        Override CrewAI's _format_messages_for_provider to sanitize DeepSeek messages.
        
        This is the critical method that gets called by _prepare_completion_params()
        before messages are sent to litellm.completion(). By overriding this method,
        we ensure sanitization happens at the right point in the call chain.
        
        Strategy: Double sanitization
        1. Sanitize input messages first
        2. Apply parent class formatting (may add/modify messages)
        3. Sanitize again to catch any issues from parent formatting
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            
        Returns:
            Sanitized list of messages with alternating roles
        """
        logging.info("=" * 80)
        logging.info("🚀 _format_messages_for_provider called")
        
        # Log original input
        self._log_messages(messages, "INPUT (original)")
        
        # First sanitization: clean input before parent processing
        pre_sanitized = self.sanitize_messages(messages)
        self._log_messages(pre_sanitized, "PRE-SANITIZED (before parent)")
        
        # Apply parent class formatting (handles Anthropic, O1, etc.)
        formatted_messages = super()._format_messages_for_provider(pre_sanitized)
        self._log_messages(formatted_messages, "PARENT FORMATTED")
        
        # Second sanitization: clean up anything the parent may have changed
        final_sanitized = self.sanitize_messages(formatted_messages)
        self._log_messages(final_sanitized, "FINAL SANITIZED")
        
        logging.info(
            f"📊 Summary: {len(messages)} input -> {len(pre_sanitized)} pre-sanitized -> "
            f"{len(formatted_messages)} parent-formatted -> {len(final_sanitized)} final"
        )
        logging.info("=" * 80)
        
        return final_sanitized
