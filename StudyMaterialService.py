from pymongo import MongoClient


class StudyMaterialService:
    def __init__(self, connection_string):
        client = MongoClient(connection_string)
        database = client.get_database("StudyMaterial")
        self._studyMaterialCollection = database.get_collection("TutoringPlatform")

    def search_study_materials(self, keyword):
        filter = {
            "$or": [
                {"Title": {"$regex": keyword, "$options": "i"}},
                {"Tags": {"$regex": keyword, "$options": "i"}},
                {"Description": {"$regex": keyword, "$options": "i"}}
            ]
        }
        return list(self._studyMaterialCollection.find(filter))

