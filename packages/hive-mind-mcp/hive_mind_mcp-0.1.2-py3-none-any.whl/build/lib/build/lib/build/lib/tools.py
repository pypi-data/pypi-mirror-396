import asyncio
import os
from typing import List, Dict, Optional, Any
from .providers.openai import OpenAIProvider
from .providers.anthropic import AnthropicProvider
from .providers.deepseek import DeepSeekProvider
from .providers.deepseek import DeepSeekProvider
from .providers.openai_compatible import OpenAICompatibleProvider
from .providers.gemini import GeminiProvider
from .providers.openrouter import OpenRouterProvider
from .providers.openrouter import OpenRouterProvider
from .providers.groq import GroqProvider
from .providers.mistral import MistralProvider
from .providers.base import LLMProvider
from src.config import settings

class LLMManager:
    """
    Manages LLM providers and orchestrates complex interactions.
    """
    def __init__(self):
        self.providers: Dict[str, LLMProvider] = {}
        # Simple factory/registry
        self.provider_classes = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            "deepseek": DeepSeekProvider,
            "generic": OpenAICompatibleProvider,
            "gemini": GeminiProvider,
            "openrouter": OpenRouterProvider,
            "groq": GroqProvider,
            "mistral": MistralProvider
        }
        self.semaphore = asyncio.Semaphore(settings.concurrency_limit)
        
        from src.logger import get_logger
        self.logger = get_logger("llm_manager")
        
    def _get_provider(self, provider_name: str) -> LLMProvider:
        if provider_name not in self.providers:
            if provider_name == "openai":
                self.providers[provider_name] = OpenAIProvider()
            elif provider_name == "anthropic":
                self.providers[provider_name] = AnthropicProvider()
            elif provider_name == "deepseek":
                self.providers[provider_name] = DeepSeekProvider()
            elif provider_name == "generic":
                self.providers[provider_name] = OpenAICompatibleProvider()
            elif provider_name == "gemini":
                self.providers[provider_name] = GeminiProvider()
            elif provider_name == "openrouter":
                self.providers[provider_name] = OpenRouterProvider()
            elif provider_name == "groq":
                self.providers[provider_name] = GroqProvider()
            elif provider_name == "mistral":
                self.providers[provider_name] = MistralProvider()
            else:
                raise ValueError(f"Unknown provider: {provider_name}")
        return self.providers[provider_name]

    async def chat_completion(
        self, 
        provider: str, 
        model: str, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None
    ) -> str:
        llm = self._get_provider(provider)
        return await llm.generate_response(model, messages, system_prompt)

    def list_models(self) -> Dict[str, List[str]]:
        models = {}
        # Try to initialize all providers to list their models
        # In a real app we might handle missing keys gracefully here
        try:
            openai = self._get_provider("openai")
            models["openai"] = openai.list_models()
        except Exception as e:
            self.logger.error("provider_init_error", provider="openai", error=str(e))
            models["openai"] = ["(Error initializing OpenAI provider)"]
            
        try:
            anthropic = self._get_provider("anthropic")
            models["anthropic"] = anthropic.list_models()
        except Exception as e:
            self.logger.error("provider_init_error", provider="anthropic", error=str(e))
            models["anthropic"] = ["(Error initializing Anthropic provider)"]

        try:
            deepseek = self._get_provider("deepseek")
            models["deepseek"] = deepseek.list_models()
        except Exception as e:
            self.logger.error("provider_init_error", provider="deepseek", error=str(e))
            models["deepseek"] = ["(Error initializing DeepSeek provider)"]

        try:
            generic = self._get_provider("generic")
            models["generic"] = generic.list_models()
        except Exception as e:
            # Don't log error for generic if it's just not configured, 
            # but here we initialize it with defaults so it should pass.
            models["generic"] = ["(Generic Provider - Check GENERIC_BASE_URL)"]
            
        try:
            gemini = self._get_provider("gemini")
            models["gemini"] = gemini.list_models()
        except Exception as e:
            self.logger.error("provider_init_error", provider="gemini", error=str(e))
            models["gemini"] = ["(Error initializing Gemini provider)"]

        try:
            op = self._get_provider("openrouter")
            models["openrouter"] = op.list_models()
        except Exception:
            models["openrouter"] = ["(Error initializing OpenRouter)"]
            
        try:
            groq = self._get_provider("groq")
            models["groq"] = groq.list_models()
        except Exception:
            models["groq"] = ["(Error initializing Groq)"]
            
        try:
            mistral = self._get_provider("mistral")
            models["mistral"] = mistral.list_models()
        except Exception:
            models["mistral"] = ["(Error initializing Mistral)"]

        return models

    async def collaborative_refine(
        self,
        prompt: str,
        drafter_model: Optional[str] = None,
        reviewers: Optional[List[Dict[str, str]]] = None,
        max_turns: int = 3,
        drafter_provider: Optional[str] = None,
        context: Optional[str] = None,
    ) -> str:
        """
        Orchestrates a debate/refinement loop with a Council of Reviewers.
        """
        import asyncio
        import os
        import json
        
        # 1. Load Defaults from Env if not provided
        if not drafter_provider:
            drafter_provider = os.getenv("DEFAULT_DRAFTER_PROVIDER", "openai")
        
        if not drafter_model:
            drafter_model = os.getenv("DEFAULT_DRAFTER_MODEL", "gpt-4o")

        if not reviewers:
            # Parse default reviewers from env
            # Supports JSON: '[{"provider":"anthropic","model":"..."}]'
            # OR Simple format: 'anthropic:claude-3-5-sonnet, deepseek:deepseek-coder'
            default_revs_str = os.getenv("DEFAULT_REVIEWERS")
            if default_revs_str:
                default_revs_str = default_revs_str.strip()
                try:
                    reviewers = json.loads(default_revs_str)
                except json.JSONDecodeError:
                    # Parse simple format
                    reviewers = []
                    for item in default_revs_str.split(','):
                        if ':' in item:
                            p, m = item.split(':', 1)
                            reviewers.append({"provider": p.strip(), "model": m.strip()})
            
            if not reviewers:
                 # Hard fallback
                 reviewers = [{"provider": "anthropic", "model": "claude-3-5-sonnet-20240620"}]

        drafter = self._get_provider(drafter_provider)
        
        # Initialize reviewers
        reviewer_instances = []
        for r in reviewers:
            prov = self._get_provider(r["provider"])
            reviewer_instances.append((prov, r["model"]))
        
        
        # Init Recorder
        from src.persistence import SessionRecorder
        recorder = SessionRecorder()
        session_dir = recorder.create_session_dir("debate", prompt)
        self.logger.info("session_created", dir=session_dir)
        print(f"\n📁 Session Artifacts will be saved to: {session_dir}")

        recorder.save_metadata(session_dir, {
            "topic": prompt,
            "drafter": f"{drafter_provider}:{drafter_model}",
            "reviewers": [f"{p['provider']}:{p['model']}" for p in reviews] if reviewers else [],
            "max_turns": max_turns
        })

        initial_user_msg = prompt
        if context:
            initial_user_msg += f"\n\n--- ADDITIONAL CONTEXT ---\n{context}\n--------------------------"

        current_response = await drafter.generate_response(
            model=drafter_model,
            messages=[{"role": "user", "content": initial_user_msg}],
            system_prompt="You are an expert assistant. Draft the best possible response."
        )
        
        # Save Initial Draft
        recorder.save_artifact(session_dir, "00_initial_draft.md", current_response)
        
        history = [
            {"role": "user", "content": f"Original Request: {prompt}\n\nCurrent Draft:\n{current_response}"}
        ]
        
        for turn in range(max_turns):
             # Council Review Step (Parallel)
            review_prompt = """
            You are a member of the Expert Council. Analyze the draft provided.
            You MUST return your response in strictly VALID JSON format with these fields:
            {
                "status": "APPROVED" or "REVISE",
                "score": (integer 0-10),
                "feedback": "string explanation"
            }
            Do not add markdown code blocks around the JSON. Just the raw JSON string.
            """
            
            async def get_review(prov, mod, hist):
                try:
                    raw = await prov.generate_response(model=mod, messages=hist, system_prompt=review_prompt)
                    clean = raw.replace("```json", "").replace("```", "").strip()
                    import json
                    return json.loads(clean)
                except Exception as e:
                    self.logger.error("reviewer_failed", provider=prov.__class__.__name__, error=str(e))
                    return {"status": "REVISE", "score": 0, "feedback": f"Reviewer Error ({prov.__class__.__name__}): {e}"}

            # Gather reviews from all council members
            reviews = await asyncio.gather(*[
                get_review(prov, mod, history) for prov, mod in reviewer_instances
            ])
            
            # Save Reviews
            review_text = ""
            for i, r in enumerate(reviews):
                review_text += f"Reviewer {i+1}:\n{json.dumps(r, indent=2)}\n\n"
            recorder.save_artifact(session_dir, f"0{turn+1}_reviews.json", review_text)

            # Aggregate Feedback
            total_score = sum(r.get("score", 0) for r in reviews)
            avg_score = total_score / len(reviews)
            all_approved = all(r.get("status") == "APPROVED" for r in reviews)
            
            aggregated_feedback = "Council Feedback:\n"
            for i, r in enumerate(reviews):
                aggregated_feedback += f"- Reviewer {i+1}: {r.get('feedback')}\n"

            if all_approved or avg_score >= 9:
                final = f"Final Answer (Approved by Council):\n\n{current_response}"
                recorder.save_artifact(session_dir, "99_final_approved.md", final)
                return final
            
            # Drafter Refine Step
            refine_instruction = f"{aggregated_feedback}\n\nPlease parse this feedback and rewrite the draft to address ALL concerns."
            
            # Update history
            history.append({"role": "assistant", "content": aggregated_feedback})
            history.append({"role": "user", "content": refine_instruction})
            
            current_response = await drafter.generate_response(
                model=drafter_model,
                messages=history,
                system_prompt="You are an expert assistant. Synthesize the feedback and refine your work."
            )
            
            recorder.save_artifact(session_dir, f"0{turn+1}_refined_draft.md", current_response)
            
            history.append({"role": "assistant", "content": f"Updated Draft:\n{current_response}"})
            history.append({"role": "user", "content": "Please review this updated draft."})
        
        final_max = f"Result (Max turns reached):\n\n{current_response}"
        recorder.save_artifact(session_dir, "99_final_max_turns.md", final_max)
        return final_max

    async def evaluate_content(
        self,
        content: str,
        reviewers: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """
        Submits content to the Council for peer review only (no modification by server).
        """
        import asyncio
        import os
        import json
        
        # Load Defaults
        if not reviewers:
            default_revs_str = os.getenv("DEFAULT_REVIEWERS")
            if default_revs_str:
                default_revs_str = default_revs_str.strip()
                try:
                    reviewers = json.loads(default_revs_str)
                except json.JSONDecodeError:
                    reviewers = []
                    for item in default_revs_str.split(','):
                        if ':' in item:
                            p, m = item.split(':', 1)
                            reviewers.append({"provider": p.strip(), "model": m.strip()})
            
            if not reviewers:
                 reviewers = [{"provider": "anthropic", "model": "claude-3-5-sonnet-20240620"}]

        # Init Recorder
        from src.persistence import SessionRecorder
        recorder = SessionRecorder()
        session_dir = recorder.create_session_dir("review", "peer_review_content")
        self.logger.info("session_created", dir=session_dir)
        print(f"\n📁 Session Artifacts will be saved to: {session_dir}")

        recorder.save_metadata(session_dir, {
            "type": "peer_review",
            "reviewers": [f"{p['provider']}:{p['model']}" for p in reviewers],
            "content_length": len(content)
        })
        
        # Save Subject Content
        recorder.save_artifact(session_dir, "00_subject_content.txt", content)

        # Prepare prompt
        review_prompt = """
        You are a member of the Expert Council. Analyze the content provided.
        You MUST return your response in strictly VALID JSON format with these fields:
        {
            "status": "APPROVED" or "REVISE",
            "score": (integer 0-10),
            "feedback": "string explanation"
        }
        Do not add markdown code blocks around the JSON. Just the raw JSON string.
        """
        
        async def get_review(prov_name, mod, text):
            try:
                prov = self._get_provider(prov_name)
                # Ensure the input isn't too large for context window
                messages = [{"role": "user", "content": f"Please review this content:\n\n{text}"}]
                raw = await prov.generate_response(model=mod, messages=messages, system_prompt=review_prompt)
                clean = raw.replace("```json", "").replace("```", "").strip()
                return {"provider": prov_name, "model": mod, "json": json.loads(clean)}
            except Exception as e:
                self.logger.error("reviewer_failed", provider=prov_name, error=str(e))
                return {"provider": prov_name, "model": mod, "error": str(e), "status": "ERROR", "score": 0, "feedback": f"Reviewer Error ({prov_name}): {e}"}

        # Gather reviews
        tasks = [get_review(r["provider"], r["model"], content) for r in reviewers]
        results = await asyncio.gather(*tasks)
        
        # Save Reviews
        for r in results:
            if "json" in r:
                filename = f"01_review_{r['provider']}.json"
                recorder.save_artifact(session_dir, filename, json.dumps(r['json'], indent=2))
            else:
                recorder.save_artifact(session_dir, f"error_{r['provider']}.txt", r.get('error', 'Unknown error'))

        # Aggregate
        aggregated_feedback = "## Council Feedback\n"
        aggregated_feedback += f"\n*(Detailed artifacts saved to {session_dir})*\n"
        
        for i, r in enumerate(results):
            reviewer_name = f"{r['provider']}/{r['model']}"
            if "json" in r:
                data = r["json"]
                icon = "✅" if data.get('status') == 'APPROVED' else "⚠️"
                aggregated_feedback += f"\n### {icon} Reviewer {i+1} ({reviewer_name})\n"
                aggregated_feedback += f"**Score:** {data.get('score', 0)}/10\n"
                aggregated_feedback += f"**Status:** {data.get('status')}\n"
                aggregated_feedback += f"**Feedback:** {data.get('feedback')}\n"
            else:
                aggregated_feedback += f"\n### ❌ Reviewer {i+1} ({reviewer_name})\n"
                aggregated_feedback += f"**Error:** {r.get('feedback')}\n"

        recorder.save_artifact(session_dir, "02_summary.md", aggregated_feedback)
        
        return aggregated_feedback

    async def round_table_debate(
        self,
        prompt: str,
        panelists: Optional[List[Dict[str, str]]] = None,
        moderator_provider: str = "openai",
        moderator_model: str = "gpt-4o",
        context: Optional[str] = None
    ) -> str:
        """
        Conducts a full Round Table debate:
        1. All panelists generate independent answers.
        2. Panelists critique each other's answers.
        3. Moderator synthesizes a final Consensus Answer.
        """
        import asyncio
        import os
        import json
        
        # 1. Load Defaults
        if not panelists:
            default_revs_str = os.getenv("DEFAULT_REVIEWERS")
            if default_revs_str:
                try:
                    # Try simplified "p:m, p:m" format first as it's common now
                    panelists = []
                    if "{" not in default_revs_str:
                         for item in default_revs_str.split(','):
                            if ':' in item:
                                p, m = item.split(':', 1)
                                panelists.append({"provider": p.strip(), "model": m.strip()})
                    else:
                        panelists = json.loads(default_revs_str)
                except Exception:
                    pass
            
            if not panelists:
                 # Default Council
                 panelists = [
                     {"provider": "openai", "model": "gpt-4o"},
                     {"provider": "anthropic", "model": "claude-3-5-sonnet-20240620"},
                     {"provider": "deepseek", "model": "deepseek-coder"}
                 ]
        
        # Ensure unique list and moderator availability
        moderator = self._get_provider(moderator_provider)

        # Step 1: Independent Generation
        self.logger.info("round_table_phase_1", prompt=prompt[:100])
        
        initial_user_msg = prompt
        if context:
            initial_user_msg += f"\n\n--- ADDITIONAL CONTEXT ---\n{context}\n--------------------------"

        async def generate_draft(p_conf):
            try:
                prov = self._get_provider(p_conf["provider"])
                resp = await prov.generate_response(model=p_conf["model"], messages=[{"role": "user", "content": initial_user_msg}])
                return {"provider": p_conf["provider"], "model": p_conf["model"], "content": resp}
            except Exception as e:
                return {"provider": p_conf["provider"], "error": str(e)}

        # Init Recorder
        from src.persistence import SessionRecorder
        recorder = SessionRecorder()
        session_dir = recorder.create_session_dir("round_table", prompt)
        self.logger.info("session_created", dir=session_dir)
        
        # Save Metadata
        recorder.save_metadata(session_dir, {
            "topic": prompt,
            "panelists": [f"{p['provider']}:{p['model']}" for p in panelists],
            "moderator": f"{moderator_provider}:{moderator_model}",
            "context_length": len(initial_user_msg)
        })

        drafts = await asyncio.gather(*[generate_draft(p) for p in panelists])
        valid_drafts = [d for d in drafts if "content" in d]
        failed_drafts = [d for d in drafts if "error" in d]

        print(f"\n📁 Session Artifacts will be saved to: {session_dir}")

        print("\n--- PHASE 1 RESULTS ---")
        if valid_drafts:
            for i, d in enumerate(valid_drafts):
                print(f"\n[Draft by {d['provider']}/{d['model']}]\n{d['content']}\n")
                # Save Draft
                filename = f"01_draft_{d['provider']}_{d['model']}.md"
                recorder.save_artifact(session_dir, filename, d['content'])
        
        if failed_drafts:
            print(f"\n[⚠️ ERRORS DETECTED]")
            for d in failed_drafts:
                error_msg = f"Provider {d['provider']} failed: {d['error']}"
                print(error_msg)
                self.logger.error("draft_generation_failed", provider=d['provider'], error=d['error'])
                recorder.save_artifact(session_dir, f"error_{d['provider']}.txt", d['error'])

        print("-----------------------\n")
        
        if not valid_drafts:
             return f"❌ CRITICAL ERROR: No panelists successfully generated a draft.\nFailures: {', '.join([d['provider'] + ': ' + d['error'] for d in failed_drafts])}"

        self.logger.info("phase_1_results", successful_drafts=len(valid_drafts), failed=len(failed_drafts))

        # Step 2: Cross-Critique
        self.logger.info("round_table_phase_2")
        print("Round Table: Phase 2 - Cross Critique")
        critiques = []
        
        async def critique_others(critic_conf, all_drafts):
            # Critic reviews all drafts EXCEPT their own (or reviews all if simplified)
            context = "Here are proposed solutions from other experts:\n"
            for i, d in enumerate(all_drafts):
                if d["provider"] == critic_conf["provider"] and d["model"] == critic_conf["model"]:
                    continue # Skip self ?? Actually self-reflection is good too. Let's review ALL.
                context += f"--- Solution {i+1} ({d['provider']}) ---\n{d['content'][:2000]}...\n\n" # Truncate for tokens

            sys_prompt = "You are a critical expert. Compare these solutions. Identify the strongest points of each and fatal flaws."
            msg = [{"role": "user", "content": f"Original Problem: {prompt}\n\n{context}"}]
            
            try:
                prov = self._get_provider(critic_conf["provider"])
                resp = await prov.generate_response(model=critic_conf["model"], messages=msg, system_prompt=sys_prompt)
                return {"provider": critic_conf["provider"], "content": resp}
            except Exception as e:
                self.logger.error("critique_failed", provider=critic_conf["provider"], error=str(e))
                return {"provider": critic_conf["provider"], "error": str(e)}

        critique_results_raw = await asyncio.gather(*[critique_others(p, valid_drafts) for p in panelists])
        
        # Save Critiques
        critique_results = []
        for cr in critique_results_raw:
            if "content" in cr:
                critique_results.append(f"Critique by {cr['provider']}:\n{cr['content']}")
                recorder.save_artifact(session_dir, f"02_critique_{cr['provider']}.md", cr['content'])
            else:
                critique_results.append(f"Critique Error ({cr['provider']}): {cr['error']}")


        # Step 3: Synthesis
        self.logger.info("round_table_phase_3")
        print("Round Table: Phase 3 - Synthesis")
        full_context = f"Original Request: {prompt}\n\n"
        
        full_context += "=== PHASE 1: PROPOSED SOLUTIONS ===\n"
        for i, d in enumerate(valid_drafts):
            full_context += f"--- Solution {i+1} by {d['provider']} ---\n{d['content']}\n\n"
            
        full_context += "=== PHASE 2: EXPERT CRITIQUES ===\n"
        for c in critique_results:
            full_context += f"{c}\n\n"
            
        if failed_drafts:
            full_context += "\nNOTE TO MODERATOR: Some panelists failed to respond. Transparency is key. Mention this in your report.\n"
            
        final_system_prompt = """
        You are the Moderator of the Expert Council.
        Your goal is to synthesize the FINAL CONSENSUS.
        
        STRUCTURE YOUR RESPONSE AS FOLLOWS:
        
        ## 1. Executive Summary
        The final unified answer.
        
        ## 2. Key Agreements
        Points where all models aligned.
        
        ## 3. Areas of Disagreement (IMPORTANT)
        Explicitly list where the models disagreed or conflicted. Explain WHY they disagreed.
        
        ## 4. Final Solution / Code
        The synthesized best-of-breed solution.
        
        ## 5. Recommendations for Improvement
        (Optional) Only if valid improvements were suggested.
        """
        
        final_answer = await moderator.generate_response(
            model=moderator_model,
            messages=[{"role": "user", "content": full_context}],
            system_prompt=final_system_prompt
        )
        
        recorder.save_artifact(session_dir, "03_consensus.md", final_answer)
        print(f"✅ Session saved to: {session_dir}")
        
        return f"# Round Table Consensus\n\n{final_answer}\n\n---\n*Based on inputs from: {', '.join([d['provider'] for d in valid_drafts])}*\n\n*(Full artifacts saved to {session_dir})*"

    async def summarize_file(self, file_path: str, content: str, provider_name: str = "openai", model: str = "gpt-4o") -> str:
        """
        Map Phase: Generates a dense technical summary of a single file.
        """
        prompt = f"""
        You are a Technical Architech. Summarize this code file ({file_path}).
        Focus on:
        1. Key Classes and Functions (signatures).
        2. Responsibilities and Design Patterns used.
        3. Dependencies and Exports.
        4. Any complex logic, potential issues, OR AREAS FOR IMPROVEMENT.
        
        Keep the summary concise but technically dense. (Max 150 words). Use bullet points.
        Include a specific bullet point for "Improvements" if applicable.
        ----------------
        File Content:
        {content[:15000]} 
        ----------------
        """
        try:
            async with self.semaphore:
                prov = self._get_provider(provider_name)
                # Use system prompt for conciseness
                summary = await prov.generate_response(
                    model=model, 
                    messages=[{"role": "user", "content": prompt}],
                    system_prompt="You are a code summarizer. Output only the summary."
                )
                return f"### Summary of {file_path}\n{summary}"
        except Exception as e:
            return f"### Summary of {file_path}\n(Error generating summary: {e})"

    async def map_reduce_context(
        self,
        file_paths: List[str],
        summarizer_provider: str = "openai",
        summarizer_model: str = "gpt-4o"
    ) -> str:
        """
        Performs the Map phase: Summarizes multiple files in parallel.
        Returns a single string containing all summaries.
        """
        import asyncio
        
        # 1. Read Files
        file_contents = {}
        for path in file_paths:
            try:
                # If path is already content (not file), handle? No, assume paths.
                # Actually, if we want to share logic with CLI's collection, 
                # we might need to handle reading there. 
                # But for now, let's keep it compatible with existing analyze_project signature.
                if os.path.exists(path):
                    with open(path, 'r', errors='ignore') as f:
                        file_contents[path] = f.read()
            except Exception as e:
                self.logger.warning("map_read_error", path=path, error=str(e))
        
        if not file_contents:
            return ""

        self.logger.info("starting_map_phase", file_count=len(file_contents))
        
        # 2. Map Phase (Parallel Summarization)
        summary_tasks = [
            self.summarize_file(path, content, summarizer_provider, summarizer_model)
            for path, content in file_contents.items()
        ]
        summaries = await asyncio.gather(*summary_tasks)
        
        return "\n\n".join(summaries)

    async def analyze_project(
        self,
        file_paths: List[str],
        prompt: str,
        panelists: Optional[List[Dict[str, str]]] = None,
        summarizer_provider: str = "openai",
        summarizer_model: str = "gpt-4o"
    ) -> str:
        """
        Orchestrates the Map-Reduce analysis:
        1. Map: Summarize all files in parallel.
        2. Reduce: Feed summaries to Round Table Debate.
        """
        
        project_knowledge = await self.map_reduce_context(
            file_paths, 
            summarizer_provider, 
            summarizer_model
        )
        
        if not project_knowledge:
             return "Error: No valid files found or empty context."

        self.logger.info("context_reduced", size_chars=len(project_knowledge))
        
        # 3. Reduce Phase (Round Table)
        self.logger.info("starting_reduce_phase")
        
        full_prompt = (
            f"Based on the following TECHNICAL SUMMARIES of a codebase, please address the user's request.\n\n"
            f"--- PROJECT KNOWLEDGE BASE ---\n{project_knowledge}\n--- END KNOWLEDGE ---\n\n"
            f"USER REQUEST: {prompt}"
        )
        
        return await self.round_table_debate(
            prompt=full_prompt,
            panelists=panelists
        )
