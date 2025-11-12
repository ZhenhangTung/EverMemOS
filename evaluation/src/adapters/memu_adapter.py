"""
Memu Adapter - adapt Memu online API for evaluation framework.
Uses HTTP RESTful API instead of Python SDK to avoid dependency conflicts.
Reference: https://memu.so/
"""
import json
import time
import requests
from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console

from evaluation.src.adapters.online_base import OnlineAPIAdapter
from evaluation.src.adapters.registry import register_adapter
from evaluation.src.core.data_models import Conversation, SearchResult


@register_adapter("memu")
class MemuAdapter(OnlineAPIAdapter):
    """
    Memu online API adapter.
    
    Uses HTTP RESTful API directly to avoid Python SDK dependency conflicts.
    
    Supports:
    - Memory ingestion (based on conversation context)
    - Async task status monitoring
    - Memory retrieval
    
    Config example:
    ```yaml
    adapter: "memu"
    api_key: "${MEMU_API_KEY}"
    base_url: "https://api.memu.so"  # Optional, defaults to official API
    agent_id: "default_agent"  # Optional, default agent ID
    agent_name: "Assistant"  # Optional, default agent name
    task_check_interval: 3  # Optional, task status check interval (seconds)
    task_timeout: 90  # Optional, task timeout (seconds)
    ```
    """
    
    def __init__(self, config: dict, output_dir: Path = None):
        super().__init__(config, output_dir)
        
        # Get configuration
        api_key = config.get("api_key", "")
        if not api_key:
            raise ValueError("Memu API key is required. Set 'api_key' in config.")
        
        self.base_url = config.get("base_url", "https://api.memu.so").rstrip('/')
        self.agent_id = config.get("agent_id", "default_agent")
        self.agent_name = config.get("agent_name", "Assistant")
        self.task_check_interval = config.get("task_check_interval", 3)
        self.task_timeout = config.get("task_timeout", 90)
        self.max_retries = config.get("max_retries", 5)
        
        # HTTP headers
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        self.console = Console()
        self.console.print(f"   Base URL: {self.base_url}", style="dim")
        self.console.print(f"   Agent: {self.agent_name} ({self.agent_id})", style="dim")
    
    async def add(
        self, 
        conversations: List[Conversation],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Ingest conversations into Memu.
        
        Memu API specifics:
        - Uses HTTP RESTful API to submit memories
        - Returns async task ID, needs polling for status
        - Search only available after task completion
        - Supports dual perspective handling (stores memories separately for two speakers)
        """
        self.console.print(f"\n{'='*60}", style="bold cyan")
        self.console.print(f"Stage 1: Adding to Memu", style="bold cyan")
        self.console.print(f"{'='*60}", style="bold cyan")
        
        conversation_ids = []
        task_ids = []
        
        for conv in conversations:
            conv_id = conv.conversation_id
            conversation_ids.append(conv_id)
            
            # Get dual perspective information
            speaker_a = conv.metadata.get("speaker_a", "User")
            speaker_b = conv.metadata.get("speaker_b", "Assistant")
            speaker_a_user_id = self._extract_user_id(conv, speaker="speaker_a")
            speaker_b_user_id = self._extract_user_id(conv, speaker="speaker_b")
            
            # Determine if dual perspective is needed
            need_dual_perspective = self._need_dual_perspective(speaker_a, speaker_b)
            
            self.console.print(f"\n📥 Adding conversation: {conv_id}", style="cyan")
            self.console.print(f"   Speaker A: {speaker_a} ({speaker_a_user_id})", style="dim")
            self.console.print(f"   Speaker B: {speaker_b} ({speaker_b_user_id})", style="dim")
            self.console.print(f"   Dual Perspective: {need_dual_perspective}", style="dim")
            
            # Get session_date (ISO format date)
            session_date = None
            if conv.messages and conv.messages[0].timestamp:
                session_date = conv.messages[0].timestamp.strftime("%Y-%m-%d")
            else:
                from datetime import datetime
                session_date = datetime.now().strftime("%Y-%m-%d")
            
            # Add memories based on perspective needs
            if need_dual_perspective:
                # Dual perspective: add memories separately for speaker_a and speaker_b
                task_id_a = await self._add_single_user(
                    conv, speaker_a_user_id, speaker_a, session_date, perspective="speaker_a"
                )
                task_id_b = await self._add_single_user(
                    conv, speaker_b_user_id, speaker_b, session_date, perspective="speaker_b"
                )
                if task_id_a:
                    task_ids.append(task_id_a)
                if task_id_b:
                    task_ids.append(task_id_b)
            else:
                # Single perspective: only add memories for speaker_a
                task_id = await self._add_single_user(
                    conv, speaker_a_user_id, speaker_a, session_date, perspective="speaker_a"
                )
                if task_id:
                    task_ids.append(task_id)
        
        # Wait for all tasks to complete
        if task_ids:
            self.console.print(f"\n⏳ Waiting for {len(task_ids)} task(s) to complete...", style="bold yellow")
            self._wait_for_all_tasks(task_ids)
        
        self.console.print(f"\n✅ All conversations added to Memu", style="bold green")
        
        # Return metadata
        return {
            "type": "online_api",
            "system": "memu",
            "conversation_ids": conversation_ids,
            "task_ids": task_ids,
        }
    
    def _need_dual_perspective(self, speaker_a: str, speaker_b: str) -> bool:
        """
        Determine if dual perspective handling is needed.
        
        Single perspective (no dual perspective needed):
        - Standard roles: "user"/"assistant"
        - Case variants: "User"/"Assistant"
        - With suffix: "user_123"/"assistant_456"
        
        Dual perspective (dual perspective needed):
        - Custom names: "Caroline"/"Manu"
        """
        def is_standard_role(speaker: str) -> bool:
            speaker = speaker.lower()
            # Exact match
            if speaker in ["user", "assistant"]:
                return True
            # Starts with user or assistant
            if speaker.startswith("user") or speaker.startswith("assistant"):
                return True
            return False
        
        return not (is_standard_role(speaker_a) and is_standard_role(speaker_b))
    
    async def _add_single_user(
        self,
        conv: Conversation,
        user_id: str,
        user_name: str,
        session_date: str,
        perspective: str
    ) -> str:
        """
        Add memories for a single user.
        
        Args:
            conv: Conversation object
            user_id: User ID
            user_name: User name
            session_date: Session date
            perspective: Perspective (speaker_a or speaker_b)
        
        Returns:
            task_id: Task ID (if successful)
        """
        # Convert to Memu API format (with specified perspective)
        base_messages = self._conversation_to_messages(conv, format_type="basic", perspective=perspective)
        
        # Add extra fields required by Memu API
        conversation_messages = []
        for i, msg in enumerate(conv.messages):
            # Construct message time (ISO format)
            msg_time = msg.timestamp.isoformat() + "Z" if msg.timestamp else None
            
            conversation_messages.append({
                "role": base_messages[i]["role"],
                "name": msg.speaker_name or user_name,
                "time": msg_time,
                "content": base_messages[i]["content"]
            })
        
        self.console.print(f"   📤 Adding for {user_name} ({user_id}): {len(conversation_messages)} messages", style="dim")
        
        # Construct request payload
        payload = {
            "conversation": conversation_messages,
            "user_id": user_id,
            "user_name": user_name,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "session_date": session_date
        }
        
        # Submit task (with retry)
        task_id = None
        for attempt in range(self.max_retries):
            try:
                url = f"{self.base_url}/api/v1/memory/memorize"
                response = requests.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                
                result = response.json()
                task_id = result.get("task_id")
                status = result.get("status")
                
                self.console.print(f"      ✅ Task created: {task_id} (status: {status})", style="green")
                break
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    self.console.print(
                        f"      ⚠️  Retry {attempt + 1}/{self.max_retries}: {e}", 
                        style="yellow"
                    )
                    time.sleep(2 ** attempt)
                else:
                    self.console.print(
                        f"      ❌ Failed after {self.max_retries} retries: {e}", 
                        style="red"
                    )
                    raise e
        
        return task_id
    
    def _wait_for_all_tasks(self, task_ids: List[str]) -> bool:
        """
        Wait for all tasks to complete.
        
        Args:
            task_ids: Task ID list
        
        Returns:
            Whether all tasks completed successfully
        """
        if not task_ids:
            return True
        
        start_time = time.time()
        pending_tasks = set(task_ids)
        
        # Show progress
        total_tasks = len(task_ids)
        
        while time.time() - start_time < self.task_timeout:
            completed_in_round = []
            failed_in_round = []
            
            for task_id in list(pending_tasks):
                try:
                    url = f"{self.base_url}/api/v1/memory/memorize/status/{task_id}"
                    response = requests.get(url, headers=self.headers)
                    response.raise_for_status()
                    result = response.json()
                    status = result.get("status")
                    
                    # Memu API returns uppercase status: PENDING/PROCESSING/SUCCESS/FAILED
                    if status in ["SUCCESS", "COMPLETED"]:
                        completed_in_round.append(task_id)
                    elif status in ["FAILED", "FAILURE"]:
                        failed_in_round.append(task_id)
                        self.console.print(
                            f"   ❌ Task {task_id} failed: {result.get('detail_info', 'Unknown error')}", 
                            style="red"
                        )
                    
                except Exception as e:
                    self.console.print(
                        f"   ⚠️  Error checking task {task_id}: {e}", 
                        style="yellow"
                    )
            
            # Remove completed/failed tasks
            for task_id in completed_in_round + failed_in_round:
                pending_tasks.remove(task_id)
            
            # Update progress
            completed_count = total_tasks - len(pending_tasks)
            if completed_in_round or failed_in_round:
                self.console.print(
                    f"   📊 Progress: {completed_count}/{total_tasks} tasks completed",
                    style="cyan"
                )
            
            # If all tasks completed
            if not pending_tasks:
                self.console.print(
                    f"   ✅ All {total_tasks} tasks completed!",
                    style="bold green"
                )
                return len(failed_in_round) == 0
            
            # Wait before retry
            if pending_tasks:
                elapsed = time.time() - start_time
                self.console.print(
                    f"   ⏳ {len(pending_tasks)} task(s) still processing... ({elapsed:.0f}s elapsed)",
                    style="dim"
                )
                time.sleep(self.task_check_interval)
        
        # Timeout
        self.console.print(
            f"   ⚠️  Timeout: {len(pending_tasks)} task(s) not completed within {self.task_timeout}s",
            style="yellow"
        )
        return False
    
    async def search(
        self, 
        query: str,
        conversation_id: str,
        index: Any,
        **kwargs
    ) -> SearchResult:
        """
        Retrieve relevant memories from Memu.
        
        Uses HTTP RESTful API to call search interface directly.
        Supports dual perspective search.
        """
        # Get conversation information
        conversation = kwargs.get("conversation")
        if conversation:
            speaker_a = conversation.metadata.get("speaker_a", "")
            speaker_b = conversation.metadata.get("speaker_b", "")
            speaker_a_user_id = self._extract_user_id(conversation, speaker="speaker_a")
            speaker_b_user_id = self._extract_user_id(conversation, speaker="speaker_b")
            need_dual = self._need_dual_perspective(speaker_a, speaker_b)
        else:
            # Fallback: use default user_id
            speaker_a_user_id = f"{conversation_id}_speaker_a"
            speaker_b_user_id = f"{conversation_id}_speaker_b"
            speaker_a = "speaker_a"
            speaker_b = "speaker_b"
            need_dual = False
        
        top_k = kwargs.get("top_k", 10)
        min_similarity = kwargs.get("min_similarity", 0.3)
        
        if need_dual:
            # Dual perspective search
            return await self._search_dual_perspective(
                query, conversation_id, speaker_a, speaker_b, 
                speaker_a_user_id, speaker_b_user_id, top_k, min_similarity
            )
        else:
            # Single perspective search
            return await self._search_single_perspective(
                query, conversation_id, speaker_a_user_id, top_k, min_similarity
            )
    
    async def _search_single_perspective(
        self,
        query: str,
        conversation_id: str,
        user_id: str,
        top_k: int,
        min_similarity: float
    ) -> SearchResult:
        """Single perspective search."""
        try:
            url = f"{self.base_url}/api/v1/memory/retrieve/related-memory-items"
            payload = {
                "user_id": user_id,
                "agent_id": self.agent_id,
                "query": query,
                "top_k": top_k,
                "min_similarity": min_similarity
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            result = response.json()
            
        except Exception as e:
            self.console.print(f"❌ Memu search error: {e}", style="red")
            return SearchResult(
                query=query,
                conversation_id=conversation_id,
                results=[],
                retrieval_metadata={
                    "error": str(e),
                    "user_ids": [user_id]
                }
            )
        
        # Convert to standard format
        search_results = []
        related_memories = result.get("related_memories", [])
        
        for item in related_memories:
            memory = item.get("memory", {})
            content = memory.get("content", "")
            score = item.get("similarity_score", 0.0)
            
            search_results.append({
                "content": content,
                "score": score,
                "user_id": user_id,
                "metadata": {
                    "id": memory.get("memory_id", ""),
                    "category": memory.get("category", ""),
                    "created_at": memory.get("created_at", ""),
                    "happened_at": memory.get("happened_at", ""),
                }
            })
        
        # Build custom context
        formatted_context = self._build_memu_context(search_results)
        
        return SearchResult(
            query=query,
            conversation_id=conversation_id,
            results=search_results,
            retrieval_metadata={
                "system": "memu",
                "user_ids": [user_id],
                "top_k": top_k,
                "min_similarity": min_similarity,
                "total_found": result.get("total_found", len(search_results)),
                "formatted_context": formatted_context,
            }
        )
    
    async def _search_dual_perspective(
        self,
        query: str,
        conversation_id: str,
        speaker_a: str,
        speaker_b: str,
        speaker_a_user_id: str,
        speaker_b_user_id: str,
        top_k: int,
        min_similarity: float
    ) -> SearchResult:
        """Dual perspective search."""
        # Search memories for both users separately
        result_a = await self._search_single_perspective(
            query, conversation_id, speaker_a_user_id, top_k, min_similarity
        )
        result_b = await self._search_single_perspective(
            query, conversation_id, speaker_b_user_id, top_k, min_similarity
        )
        
        # Merge results
        all_results = result_a.results + result_b.results
        
        # Sort by score
        all_results.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        # Keep only top_k
        all_results = all_results[:top_k]
        
        # Build dual perspective context
        formatted_context = self._build_dual_perspective_context(
            speaker_a, speaker_b, result_a.results, result_b.results
        )
        
        return SearchResult(
            query=query,
            conversation_id=conversation_id,
            results=all_results,
            retrieval_metadata={
                "system": "memu",
                "user_ids": [speaker_a_user_id, speaker_b_user_id],
                "top_k": top_k,
                "min_similarity": min_similarity,
                "total_found": len(all_results),
                "formatted_context": formatted_context,
                "dual_perspective": True,
            }
        )
    
    def _build_dual_perspective_context(
        self,
        speaker_a: str,
        speaker_b: str,
        results_a: List[Dict[str, Any]],
        results_b: List[Dict[str, Any]]
    ) -> str:
        """
        Build dual perspective context using default template.
        
        Steps:
        1. Build memory list with happened_at for each speaker
        2. Wrap in dual perspective format using online_api.templates.default
        """
        # Build Speaker A's memories (with happened_at and category)
        speaker_a_memories = []
        if results_a:
            for idx, result in enumerate(results_a[:5], 1):
                content = result.get("content", "")
                metadata = result.get("metadata", {})
                happened_at = metadata.get("happened_at", "")
                category = metadata.get("category", "")
                
                memory_text = f"{idx}. {content}"
                
                metadata_parts = []
                if happened_at:
                    date_str = happened_at.split("T")[0] if "T" in happened_at else happened_at
                    metadata_parts.append(f"Date: {date_str}")
                if category:
                    metadata_parts.append(f"Category: {category}")
                
                if metadata_parts:
                    memory_text += f" ({', '.join(metadata_parts)})"
                
                speaker_a_memories.append(memory_text)
        
        speaker_a_memories_text = "\n".join(speaker_a_memories) if speaker_a_memories else "(No memories found)"
        
        # Build Speaker B's memories (with happened_at and category)
        speaker_b_memories = []
        if results_b:
            for idx, result in enumerate(results_b[:5], 1):
                content = result.get("content", "")
                metadata = result.get("metadata", {})
                happened_at = metadata.get("happened_at", "")
                category = metadata.get("category", "")
                
                memory_text = f"{idx}. {content}"
                
                metadata_parts = []
                if happened_at:
                    date_str = happened_at.split("T")[0] if "T" in happened_at else happened_at
                    metadata_parts.append(f"Date: {date_str}")
                if category:
                    metadata_parts.append(f"Category: {category}")
                
                if metadata_parts:
                    memory_text += f" ({', '.join(metadata_parts)})"
                
                speaker_b_memories.append(memory_text)
        
        speaker_b_memories_text = "\n".join(speaker_b_memories) if speaker_b_memories else "(No memories found)"
        
        # Wrap using default template
        template = self._prompts["online_api"].get("templates", {}).get("default", "")
        return template.format(
            speaker_1=speaker_a,
            speaker_1_memories=speaker_a_memories_text,
            speaker_2=speaker_b,
            speaker_2_memories=speaker_b_memories_text,
        )
    
    def _build_memu_context(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Build custom context for Memu, using happened_at field to show event occurrence time.
        
        Args:
            search_results: Search results list
        
        Returns:
            Formatted context string
        """
        if not search_results:
            return ""
        
        context_parts = []
        
        for idx, result in enumerate(search_results[:10], 1):
            content = result.get("content", "")
            metadata = result.get("metadata", {})
            
            # Prioritize happened_at (event occurrence time), otherwise use created_at
            happened_at = metadata.get("happened_at", "")
            category = metadata.get("category", "")
            
            # Build format for each memory
            memory_text = f"{idx}. {content}"
            
            # Add time and category information (if available)
            metadata_parts = []
            if happened_at:
                # Only show date part (YYYY-MM-DD)
                date_str = happened_at.split("T")[0] if "T" in happened_at else happened_at
                metadata_parts.append(f"Date: {date_str}")
            if category:
                metadata_parts.append(f"Category: {category}")
            
            if metadata_parts:
                memory_text += f" ({', '.join(metadata_parts)})"
            
            context_parts.append(memory_text)
        
        return "\n\n".join(context_parts)
    
    def get_system_info(self) -> Dict[str, Any]:
        """Return system info."""
        return {
            "name": "Memu",
            "type": "online_api",
            "description": "Memu - Memory Management System (HTTP RESTful API)",
            "adapter": "MemuAdapter",
            "base_url": self.base_url,
            "agent_id": self.agent_id,
        }

