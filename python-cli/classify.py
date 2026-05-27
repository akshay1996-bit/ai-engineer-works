import os
import pandas as pd
from anthropic import Anthropic
from dotenv import load_dotenv
import json
import re
import argparse

load_dotenv()
client = Anthropic()
parser = argparse.ArgumentParser()
parser.add_argument("--limit",type=int)
args = parser.parse_args()
def classify_tickets(subject: str, body: str) -> dict:
    """Classify tickets based on bug, feature or billing"""
    prompt=f"""Act as a ticket classifier and classify the tickets
    
    body: {body}
    subject: {subject}

    return the response in json format only, in the below shown format:
    {{"category": "bug|feature_request|billing", "description": "one line description of the issue, "confidence": "confidence value of the response between 0 and 1"}}
    """

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=args.limit,
            messages=[{"role": "user","content":prompt}]
        )
        text = response.content[0].text
        match = re.search(r"\{.*\}", text, re.DOTALL)
        return json.loads(match.group())
    except anthropic.APIConnectionError as e:
        print("The server could not be reached")
        print(e.__cause__)
    except anthropic.RateLimitError as e:
        print("A 429 status code was received; we should back off a bit.")
    except anthropic.APIStatusError as e:
        print("Another non-200-range status code was received")
        print(e.status_code)
        print(e.response)


def main():
    try:
        df=pd.read_csv("tickets.csv")
        results=[]

        for _, row in df.iterrows():
            result = classify_tickets(row["subject"],row["body"])
            results.append(result)

        df["category"] = [r["category"] for r in results]
        df["description"] = [r["description"] for r in results]
        df["confidence"] = [r["confidence"] for r in results]

        df.to_csv("tickets_classified2.csv",index=False)
    
    except:
        print("An error occured")


if __name__ == "__main__":
    main()




