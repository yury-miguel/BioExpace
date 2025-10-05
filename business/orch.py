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
log = save.setup_logs('orch_debug.txt')


class BioInsightPipeline:
    def __init__(self):
        self.handle = HandlerDatabase()

    def run(self):
        docs = self.handle.call("get_documents", limit=5)
        for doc in docs:
            log.info(f"🧩 Processing {doc.title}")

            # === Stage 1: Scientific interpretation (Qwen) ===
            qwen_id = self.handle.call(
                "insert_llm_pipeline",
                publication_id=doc.id,
                stage="qwen_analysis",
                status="running"
            )
            qwen_output = self.process_qwen(doc.text_extratect, qwen_id)
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
            llama_output = self.process_llama(qwen_output, llama_id)
            self.handle.call(
                "insert_llm_pipeline",
                publication_id=doc.id,
                stage="llama_insight",
                result_json=llama_output,
                status="success"
            )

    def chunk_text(self, text: str, max_tokens: int = 1500):
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
        system = """
        You are a senior space biologist with extensive expertise in the effects of space environments on biological systems. Your role is to deeply analyze scientific documents on space biology, 
        identifying key themes without prior knowledge of the document's structure. 
        Themes should emerge organically from the content, such as microgravity impacts on cellular processes,
        cosmic radiation effects on DNA, sex-specific biological responses in space, regenerative potential of stem cells under altered gravity, 
        or immunological changes during long-duration missions. For each theme, provide a rigorous, 
        evidence-based interpretation focusing on scientific accuracy and implications for human space exploration.
        Output must be scientifically rigorous and structured in JSON.
        """

        content = """
        Analyze this chunk of the scientific document on space biology. Define main themes emerging from the text (e.g., microgravity-induced bone density loss, radiation-triggered cellular mutations, sex-specific metabolic adaptations). For each theme:
        - Extract important points and impactful discoveries, citing specific mechanisms or findings from the text.
        - Identify cause-effect correlations (e.g., reduced gravity causes decreased osteoblast activity leading to bone resorption).
        - Deduce potential cascade effects (e.g., bone loss cascades into increased fracture risk, compromising mission safety and post-flight recovery).
        - Highlight interesting observations for future research, including potential lacunas, areas of consensus or disagreement with existing literature, and actionable hypotheses for space missions.

        Integrate and refine themes from previous chunks to build a cohesive understanding. Analyze this chunk of text from a scientific document on space biology: {previous_themes}.

        For each theme:
            - Extract important points and discoveries.
            - Identify cause-effect correlations.
            - Deduce potential cascade effects.
            - Highlight interesting observations for future research.

        Output strictly in valid JSON without additional text:
        {
            "themes": {
                "theme_name": {
                    "points": ["point1", "point2"],
                    "cause_effects": ["cause1 -> effect1", "cause2 -> effect2"],
                    "cascade_effects": ["effect1 -> cascade1 -> cascade2"],
                    "observations": ["observation1 with research implication", "observation2"],
                    "impactful": [...],

                },
                ...
            }
        }

        Chunk: {chunk}
        """

        chunks = self.chunk_text(text)
        accumulated_themes = {}

        for i, chunk in enumerate(chunks):
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
                response = ollama.chat(model="qwen2.5", messages=messages)
                raw = json.loads(response["message"]["content"])
                if not raw.endswith("}"):
                    raw += "}"
                data = json.loads(raw)

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
            except json.JSONDecodeError:
                logger.warning(f"Invalid response from Qwen in the chunk: {i}")
            except Exception as e:
                log.error(f"Error processing Qwen chunk {i}: {e}")

        return {"themes": accumulated_themes}

    def process_llama(self, qwen_data, pipeline_id):
        """Usa o Llama como analista de dados sênior"""
        system = """
        You are a senior data analyst specializing in space biology, with a focus on synthesizing complex scientific analyses into actionable, impressive insights. 
        Your goal is to assimilate detailed outputs from a space biologist, highlighting patterns, implications, and strategic recommendations for space exploration. 
        Ensure outputs are structured for easy integration into dashboards, with clear, quantifiable, and visually representable elements where possible.
        """
        content = """
        Assimilate the space biologist's outputs (themes with points, cause-effect relationships, cascade effects, observations). Generate comprehensive and impressive insights:
        - Identify areas of scientific progress (e.g., breakthroughs in understanding microgravity's cellular impacts).
        - Highlight knowledge gaps (e.g., limited data on long-term radiation effects in females).
        - Note consensus or disagreement (e.g., consensus on bone loss but disagreement on mitigation strategies).
        - Provide actionable insights for space planners (e.g., mission design adjustments), astronauts (e.g., countermeasures), and researchers (e.g., priority experiments).
        - Include an impressive summary (200-300 words) that emphasizes groundbreaking discoveries and their broader implications for human spaceflight.

        Output strictly in valid JSON without additional text:
        {
            "insights": [
                {"category": "progress", "details": ["detail1", "detail2"]},
                {"category": "gaps", "details": ["gap1", "gap2"]},
                {"category": "consensus", "details": ["consensus1", "disagreement2"]},
                {"category": "actionable_insights", "details": ["insight1 for planners", "insight2 for astronauts"]}
            ],
            "impressive_summary": "..."
        }

        Biologist's output: {qwen_output}
        """

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": content.format(qwen_output=json.dumps(qwen_data, indent=2))}
        ]
        try:
            response = ollama.chat(model="llama3.1", messages=messages)
            raw = response["message"]["content"].strip()
            if not raw.endswith("}"):
                raw += "}"
            data = json.loads(raw)
            self.handle.call("insert_llm_memory", pipeline_id=pipeline_id, model_name="llama", chunk_index=0, context_json=data)
            return data
        except json.JSONDecodeError:
            logger.warning("Invalid response from Llama")
        except Exception as e:
            log.error(f"Error processing Llama: {e}")