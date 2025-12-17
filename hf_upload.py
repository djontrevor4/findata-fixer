import os, sys

FD = os.path.expanduser("~/findata")
DATA = FD + "/training_data.jsonl"

def upload():
    from huggingface_hub import HfApi, upload_file
    token = open(os.path.expanduser("~/.hf_token")).read().strip()
    api = HfApi(token=token)
    user = api.whoami()["name"]
    print("User: " + user)
    repo = "findata-fixer"
    try:
        api.create_repo(repo_id=repo, repo_type="dataset", private=True)
        print("Created repo")
    except:
        print("Repo exists")
    upload_file(path_or_fileobj=DATA, path_in_repo="training_data.jsonl", repo_id=user+"/"+repo, repo_type="dataset", token=token)
    print("Uploaded! https://huggingface.co/datasets/" + user + "/" + repo)

if __name__ == "__main__":
    upload()