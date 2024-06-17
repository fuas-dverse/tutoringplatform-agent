import os
import re

import requests
from agentDVerse import Agent

from StudyMaterialService import StudyMaterialService


class TutoringPlatformAgent(Agent):
    def __init__(self):
        super().__init__(
            name="TutoringPlatformAgent",
            description="Handles study material queries.",
            topics=["education", "literature", "art", "education"],
            output_format="json",
            callback=self.callback
        )
        self.study_material_service = StudyMaterialService(os.environ["MONGO_URI"])
        self.keywords = ["literature", "art"]  # Predefined keywords to trigger search

    def extract_keywords(self, text):
        found_keywords = [keyword for keyword in self.keywords if re.search(rf"\b{keyword}\b", text, re.IGNORECASE)]
        return found_keywords

    def search_study_materials(self, keyword):
        return self.study_material_service.search_study_materials(keyword)

    def handle_search_request(self, keyword):
        results = self.search_study_materials(keyword)
        return self.process_results(results)

    def process_results(self, results):
        # Implement any additional processing or formatting of results here if needed
        return results

    def callback(self, message):
        user_input = message.get('user_input')
        if user_input:
            keywords = self.extract_keywords(user_input)
            search_results = []
            for keyword in keywords:
                search_results.extend(self.handle_search_request(keyword))
            self.send_response_to_next(message, {"results": search_results})

    def send_response_to_next(self, initial, message):
        formatted_message = {
            "agent": "TutoringPlatformAgent",
            **message
        }

        initial.get("content").append(formatted_message)
        steps = initial.get("content")[0].get("steps")
        step = steps.index("TutoringPlatformAgent")

        if step == len(steps) - 1:
            self.send_message(f"{self.name}.output", initial)
        else:
            next_agent = steps[step + 1]
            self.send_message(f"{next_agent}.input", initial)


if __name__ == "__main__":
    tutoring_agent = TutoringPlatformAgent()
    sample_message = {
        "user_input": "Can you find me some literature or art study materials?",
        "classifier-agentDVerse": {
            "steps": ["TutoringPlatformAgent"]
        }
    }
    tutoring_agent.callback(sample_message)
