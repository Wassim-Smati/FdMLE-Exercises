"""
Cas de Code Review #3 — Pipeline d'Évaluation LLM, Tracing & Guardrails
Société: Enterprise AI Quality & Observability Service
Fichier à reviewer par le candidat en vue du call Mistral AI.
"""

import uuid
import logging
from typing import List, Dict, Any, Tuple
from fastapi import FastAPI, Request, BackgroundTasks
from opentelemetry import trace 

app = FastAPI(title="LLM Evaluation & Guardrails API")
logger = logging.getLogger("eval_service")

class AssessLLMJudge(BaseModel): 
    is_factual : bool
    is_objective : bool
    is_persuasive : bool

class LLMJudgeEvaluator:
    def __init__(self, mistral_client: Any):
        self.mistral_client = mistral_client

    async def audit_quality_background(self, user_query: str, generated_answer: str) -> str:
        # Évaluation par LLM-as-a-Judge
        judge_prompt = f'Renvoie un json pour noter la réponse en remplissant un json avec des booléens pour is_factual, is_objective, is_persuasive'
            
        response = await self.mistral_client.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": judge_prompt}]
        )
        
        res = AssessLLMJudge.model_validate_json(response.message.content)

                # 4. Vérification de la note obtenue
        if res.is_factual and res.is_objective and res.is_persuasive: 
            return {"status": "success", "answer": generated_text}
        else:
            return {"status": "flagged", "message": "Réponse rejetée par le juge"}


class BenchmarkEvaluationSuite:
    def __init__(self, mistral_client: Any):
        self.mistral_client = mistral_client

    def evals(self, test_dataset: List[Dict[str, str]]) -> tuple:
        # Exécution des benchmarks d'évaluation offline
        results = []
        true_positives = 0
        total_predictions = 0

        for item in test_dataset:
            try: 
                response = self.mistral_client.chat.complete(
                    model="mistral-small-latest",
                    messages=[{"role": "user", "content": item["question"]}],
                    temperature=0.0,
                    seed = 42
                )
                output = response.choices[0].message.content
                
                if item["expected_keyword"] in output:
                    true_positives += 1
                total_predictions += 1

            except Exception as e: 
                logger.info(f'échec du benchmark de la requête {item} avec erreur {e}')
                continue

        # Calcul de la métrique de précision
        if total_predictions != 0.0:
            precision = true_positives / total_predictions
        else: 
            precision = 0.0
        
        return (precision, true_positives, total_predictions)


class AgentStepTracer:
    def log_agent_execution_step(self, step_name: str, trace_id: str, input_payload: dict, output_payload: dict):
        # Tracing de l'exécution des sous-étapes d'un agent
        logger.info(f"Agent Step Executed: {step_name} | Input: {input_payload} | Output: {output_payload} | Id : {trace_id}")


judge_evaluator = LLMJudgeEvaluator(mistral_client=None)
benchmark_suite = BenchmarkEvaluationSuite(mistral_client=None)
tracer = AgentStepTracer()

class ValidRequest(BaseModel): 
    query: str

@app.post("/generate_with_validation")
async def generate_endpoint(request: ValidRequest, background_tasks: BackgroundTasks):
    user_query = request.query
    trace_id = str(uuid.uuid4())
    
    # 1. Tracing de l'étape initiale
    tracer.log_agent_execution_step("init_request", trace_id, {"query": user_query}, {})
    
    # 2. Génération de la réponse
    generated_text = "Voici la réponse générée pour votre demande."

    tracer.log_agent_execution_step("answer", trace_id, {}, {"answer": generated_text})
    
    background_tasks.add_task(
        judge_evaluator.audit_quality_background,
        user_query, 
        generated_text
    )

    tracer.log_agent_execution_step("add_background_task", trace_id, {"query":user_query, "answer":
        generated_text}, {})

    return {
        "status": "success",
        "answer": generated_text,
        "trace_id": trace_id
    }
    
