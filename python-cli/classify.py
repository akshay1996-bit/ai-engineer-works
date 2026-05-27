import os
import pandas as pd
from anthropic import Anthropic
from dotenv import load_dotenv
import json
import re

load_dotenv()
client = Anthropic()
def classify_tickets(body: str, subject: str) -> dict:
    """Classify tickets based on bug, feature or billing"""
    prompt=f"""Act as a ticket classifier and classify the tickets
    
    body: {body}
    subject: {subject}

    return the response in json format only, in the below shown format:
    {{"category": "bug|feature_request|billing", "description": "one line description of the issue"}}
    """
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=200,
        messages=[{"role": "user","content":prompt}]
    )
    text = response.content[0].text
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return json.loads(match.group())


def main():
    df=pd.read_csv("tickets.csv")
    results=[]

    for _, row in df.iterrows():
        print(f"{row}")
        result = classify_tickets(row["body"],row["subject"])
        results.append(result)

    df["category"] = [r["category"] for r in results]
    df["description"] = [r["description"] for r in results]

    df.to_csv("tickets_classified2.csv",index=False)


if __name__ == "__main__":
    main()




