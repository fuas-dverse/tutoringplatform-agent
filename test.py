import os
from agentDVerse import Agent
from StudyMaterialService import StudyMaterialService


class TutoringPlatformAgent(Agent):
    def __init__(self):
        self.study_material_service = StudyMaterialService(os.environ["MONGO_URI"])

    def search_study_materials(self, keyword):
        return self.study_material_service.search_study_materials(keyword)

    def handle_search_request(self, keyword):
        results = self.search_study_materials(keyword)
        return self.process_results(results)

    def process_results(self, results):
        # additional processing or formatting of results (?) not sure if needed
        return results

    def callback(self, message):
        keyword = message.get('keyword')
        if keyword:
            search_results = self.handle_search_request(keyword)
            self.send_response_to_next(message, search_results)

    def send_response_to_next(self, initial, message):
        formatted_message = {
            "agent": "TutoringPlatformAgent",
            **message
        }

        initial.get("content").append(formatted_message)

        # Retrieve the steps from the initial dictionary
        steps = initial.get("content")[0].get("steps")

        step = steps.index("TutoringPlatformAgent")

        if step == len(steps) - 1:
            self.__kafka_manager.send_message(f"TutoringPlatformAgent.output", initial)
        else:
            next_agent = steps[step + 1]
            self.__kafka_manager.send_message(f"{next_agent}.input", initial)


def search_study_material(x):
    search_results = tutoring_agent.handle_search_request(x['keyword'])
    print(search_results)

    agent.send_response_to_next(
        initial=x,
        message={
            "message": search_results
        }
    )


if __name__ == "__main__":
    tutoring_agent = TutoringPlatformAgent()

    agent = Agent(
        name="TutoringPlatformAgent",
        description="Handles study material queries.",
        topics=["education", "literature", "art"],
        output_format="json",
        callback=search_study_material
    )

    sample_message = {
        "keyword": "math",
        "classifier-agentDVerse": {
            "steps": ["TutoringPlatformAgent"]
        }
    }
    tutoring_agent.callback(sample_message)