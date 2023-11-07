import os
import time
import openai

openai.api_key = "OPEN_AI_API_KEY"

def upload_file():
    training_response=openai.File.create(file=open("hanifa_chat_converted_pruned.jsonl", "rb"), purpose="fine-tune")
    training_file_id=training_response["id"]
    print("Training_file_ID:", training_file_id)
    return training_file_id


def finetune(training_file_id):
    response = openai.FineTuningJob.create(training_file=training_file_id, model="gpt-3.5-turbo")
    job_id = response["id"]
    print("Job ID:", response["id"])
    print("Status:", response["status"])
    return job_id

if __name__ == "__main__":
    # train_id = "file-FM3aYtUjpPBKUHwMju39DD6N"
    train_id = upload_file()

    time.sleep(20)

    test = finetune(train_id)