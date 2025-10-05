# -*- coding: utf-8 -*-

# Author: Yury
# Data: 04/10/2025

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import ollama
import tiktoken
from business.handle_db import HandlerDatabase

from logs import config as save
log = save.setup_logs('orchestrator_debug.txt')


class BioInsightPipeline:
    def __init__(self):
        self.handle = HandlerDatabase()

    def run(self):
        docs = self.handle.call("get_documents", limit=5)
        log.info(f"🚀 Starting LLM interpretation pipeline for {len(docs)} documents")

        for doc in docs:
            log.info(f"🧩 Processing {doc.id} - {doc.title}")
            log.debug(f"Document length: {len(doc.text_extratect)} characters")

            # === Stage 1: Scientific interpretation (Qwen) ===
            qwen_id = self.handle.call(
                "insert_llm_pipeline",
                publication_id=doc.id,
                stage="qwen_analysis",
                status="running"
            )
            log.info(f"🧠 [Qwen] Stage started for publication {doc.id}")
            qwen_output = self.process_qwen(doc.text_extratect, qwen_id)
            log.info(f"✅ [Qwen] Analysis complete for {doc.title}")
            self.handle.call(
                "insert_llm_pipeline",
                publication_id=doc.id,
                stage="qwen_analysis",
                result_json=qwen_output,
                status="success"
            )

            # === Stage 2: Analytical insights(Llama) ===
            llama_id = self.handle.call(
                "insert_llm_pipeline",
                publication_id=doc.id,
                stage="llama_insight",
                status="running"
            )
            log.info(f"📊 [Llama] Generating high-level insights for {doc.title}")
            llama_output = self.process_llama(qwen_output, llama_id)
            log.info(f"✅ [Llama] Insight synthesis complete for {doc.title}")
            self.handle.call(
                "insert_llm_pipeline",
                publication_id=doc.id,
                stage="llama_insight",
                result_json=llama_output,
                status="success"
            )
            log.info("🏁 LLM pipeline completed for all documents.")

    def chunk_text(self, text: str, max_tokens: int = 700):
        """Divide the text into chunks with a token limit"""
        enc = tiktoken.get_encoding("cl100k_base")
        tokens = enc.encode(text)
        chunks = []
        for i in range(0, len(tokens), max_tokens):
            chunk_tokens = tokens[i:i + max_tokens]
            chunk_text = enc.decode(chunk_tokens)
            chunks.append(chunk_text)
        return chunks

    def process_qwen(self, text, pipeline_id):
        """Use Qwen as a space biologist"""
        # system = """
        # You are a senior space biologist with extensive expertise in the effects of space environments on biological systems. Your role is to deeply analyze scientific documents on space biology, 
        # identifying key themes without prior knowledge of the document's structure. 
        # Themes should emerge organically from the content, such as microgravity impacts on cellular processes,
        # cosmic radiation effects on DNA, sex-specific biological responses in space, regenerative potential of stem cells under altered gravity, 
        # or immunological changes during long-duration missions. For each theme, provide a rigorous, 
        # evidence-based interpretation focusing on scientific accuracy and implications for human space exploration.
        # Output must be scientifically rigorous and structured in JSON.
        # """

        # content_template = """
        # Analyze this chunk of the scientific document on space biology. Define main themes emerging from the text (e.g., microgravity-induced bone density loss, radiation-triggered cellular mutations, sex-specific metabolic adaptations). For each theme:
        # - Extract important points and impactful discoveries, citing specific mechanisms or findings from the text.
        # - Identify cause-effect correlations (e.g., reduced gravity causes decreased osteoblast activity leading to bone resorption).
        # - Deduce potential cascade effects (e.g., bone loss cascades into increased fracture risk, compromising mission safety and post-flight recovery).
        # - Highlight interesting observations for future research, including potential lacunas, areas of consensus or disagreement with existing literature, and actionable hypotheses for space missions.

        # Integrate and refine themes from previous chunks to build a cohesive understanding. Analyze this chunk of text from a scientific document on space biology: {previous_themes}.

        # For each theme:
        #     - Extract important points and discoveries.
        #     - Identify cause-effect correlations.
        #     - Deduce potential cascade effects.
        #     - Highlight interesting observations for future research.

        # Output strictly in valid JSON without additional text:
        # {{
        #     "themes": {{
        #         "theme_name": {{
        #             "points": ["point1", "point2"],
        #             "cause_effects": ["cause1 -> effect1", "cause2 -> effect2"],
        #             "cascade_effects": ["effect1 -> cascade1 -> cascade2"],
        #             "observations": ["observation1 with research implication", "observation2"],
        #             "impactful": [...],

        #         }},
        #         ...
        #     }}
        # }}

        # Chunk: {chunk}
        # """


        system = """
        You are a senior space biologist. Your task is to analyze scientific documents on space biology, identifying key themes and insights.
        Output must be strictly valid JSON, following the structure: points, cause_effects, cascade_effects, observations, impactful.
        Do NOT include explanations, text, or markdown outside the JSON.
        Focus on capturing all relevant scientific insights.
        """

        content_template = """
        Analyze the following chunk of a scientific document on space biology.

        Previous accumulated themes: {previous_themes}

        Instructions:
        - Identify main themes emerging from the text.
        - For each theme, extract:
        - points: important findings
        - cause_effects: cause -> effect relationships
        - cascade_effects: downstream consequences
        - observations: notes for future research or interesting phenomena
        - impactful: insights with high significance or implications

        Ensure:
        - Themes emerge from the text itself, do NOT invent them.
        - JSON output must match exactly the following structure:

        {{
        "themes": {{
            "theme_name": {{
            "points": ["..."],
            "cause_effects": ["..."],
            "cascade_effects": ["..."],
            "observations": ["..."],
            "impactful": ["..."]
            }},
            ...
        }}
        }}

        Text chunk:
        {chunk}
        """

        chunks = self.chunk_text(text)
        accumulated_themes = {}

        for i, chunk in enumerate(chunks):
            log.info(f"🔬 [Qwen] Processing chunk {i+1}/{len(chunks)} ({len(chunk)} chars)")
            prev_context = self.handle.call(
                "get_last_llm_memory",
                pipeline_id=pipeline_id,
                model_name="qwen"
            )

            previous_themes = json.dumps(accumulated_themes, indent=2) if accumulated_themes else "No previous themes available."
            user_content = content_template.format(previous_themes=previous_themes, chunk=chunk)
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": user_content}
            ]

            try:
                response = ollama.chat(model="qwen2.5:1.5b-instruct-q4_0", messages=messages)
                raw_content = response.get("message", {}).get("content", "").strip()
                log.info(f"Response QWWEN Cientific: {response}")

                if raw_content.startswith("```json"):
                    raw_content = raw_content.removeprefix("```json").removesuffix("```").strip()
                elif raw_content.startswith("```"):
                    raw_content = raw_content.removeprefix("```").removesuffix("```").strip()

                try:
                    data = json.loads(raw_content)
                except json.JSONDecodeError:
                    log.warning(f"⚠️ Chunk {i}: JSON parse failed. Attempting cleanup...")
                    raw_content = raw_content.split("```")[0].strip()
                    data = json.loads(raw_content)

                for theme, details in data.get("themes", {}).items():
                    if theme not in accumulated_themes:
                        accumulated_themes[theme] = details
                    else:
                        for key, values in details.items():
                            if key in accumulated_themes[theme]:
                                accumulated_themes[theme][key].extend([v for v in values if v not in accumulated_themes[theme][key]])
                            else:
                                accumulated_themes[theme][key] = values
                self.handle.call("insert_llm_memory", pipeline_id=pipeline_id, model_name="qwen", chunk_index=i, context_json=data)
                log.info(f"✅ [Qwen] Chunk {i+1}/{len(chunks)} processed successfully")
            except json.JSONDecodeError:
                log.warning(f"Invalid response from Qwen in the chunk: {i}")
            except Exception as e:
                log.error(f"Error processing Qwen chunk {i}: {e}")

        log.info(f"🧠 [Qwen] Total accumulated themes: {len(accumulated_themes)}")
        return {"themes": accumulated_themes}

    def process_llama(self, qwen_data, pipeline_id):
        """Usa o Llama como analista de dados sênior"""
        system = """
        You are a senior data analyst specializing in space biology, with a focus on synthesizing complex scientific analyses into actionable, impressive insights. 
        Your goal is to assimilate detailed outputs from a space biologist, highlighting patterns, implications, and strategic recommendations for space exploration. 
        Ensure outputs are structured for easy integration into dashboards, with clear, quantifiable, and visually representable elements where possible.
        """
        content_template = """
        Assimilate the space biologist's outputs (themes with points, cause-effect relationships, cascade effects, observations). Generate comprehensive and impressive insights:
        - Identify areas of scientific progress (e.g., breakthroughs in understanding microgravity's cellular impacts).
        - Highlight knowledge gaps (e.g., limited data on long-term radiation effects in females).
        - Note consensus or disagreement (e.g., consensus on bone loss but disagreement on mitigation strategies).
        - Provide actionable insights for space planners (e.g., mission design adjustments), astronauts (e.g., countermeasures), and researchers (e.g., priority experiments).
        - Include an impressive summary (200-300 words) that emphasizes groundbreaking discoveries and their broader implications for human spaceflight.

        Output strictly in valid JSON without additional text:
        {{
            "insights": [
                {{"category": "progress", "details": ["detail1", "detail2"]}},
                {{"category": "gaps", "details": ["gap1", "gap2"]}},
                {{"category": "consensus", "details": ["consensus1", "disagreement2"]}},
                {{"category": "actionable_insights", "details": ["insight1 for planners", "insight2 for astronauts"]}}
            ],
            "impressive_summary": "..."
        }}

        Biologist's output: {qwen_output}
        """

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": content_template.format(qwen_output=json.dumps(qwen_data, indent=2))}
        ]
        try:
            log.info("📡 [Llama] Starting synthesis phase")
            response = ollama.chat(model="llama3:8b", messages=messages)
            raw = response["message"]["content"].strip()
            if not raw.endswith("}"):
                raw += "}"
            data = json.loads(raw)
            log.info(f"Response LLAMA Analisys: {response}")
            self.handle.call("insert_llm_memory", pipeline_id=pipeline_id, model_name="llama", chunk_index=0, context_json=data)
            log.info("✅ [Llama] Insight synthesis complete")
            return data
        except json.JSONDecodeError:
            log.warning("Invalid response from Llama")
        except Exception as e:
            log.error(f"Error processing Llama: {e}")