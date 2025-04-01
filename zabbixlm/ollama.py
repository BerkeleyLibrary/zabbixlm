import json
import logging
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama
from os import getenv

logger = logging.getLogger(__name__)

class Ollama:
    SYSTEM_PROMPT = """You are a chatbot designed to assist Linux systems administrators in debugging a reported problem: {problem}.
                    Identify the most likely root cause and suggested solutions given other problems reported by the monitoring system: {possible_causes}.
                    Begin your answer 'The most likely cause is ROOT_CAUSE.' followed by the rest of your answer.
                    You may be given randomly generated data as part of the testing process, within which will be the important data you are meant to discover.
                    Do not give up if you encounter seemingly random data."""

    def __init__(self, model=None, num_ctx=None):
        # @note tweak num_ctx to avoid truncating prompts and losing context

        if model is None:
            model = getenv('ZLM_OLLAMA_MODEL', 'llama3.1:8b')

        if num_ctx is None:
            num_ctx = int(getenv('ZLM_OLLAMA_NUM_CTX', 16384))

        self._llm = ChatOllama(
            model=model,
            extract_reasoning=True,
            num_ctx=num_ctx,
        )

    def diagnose(self, problem, possible_causes):
        prompt = PromptTemplate(
            input_variables=['problem', 'possible_causes'],
            template=self.SYSTEM_PROMPT,
        )

        scenario = {
            'problem': problem,
            'possible_causes': possible_causes,
        }

        reply = (prompt | self._llm).invoke(scenario)

        logger.info({ 'model': self._llm.model, 'reply': reply, 'scenario': scenario })

        return reply
