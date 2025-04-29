from transformers import AutoModelForCausalLM, AutoTokenizer
import pandas as pd
import json
import re
from tqdm import tqdm

def extract_tweet(text):
    """
    Extracts the value of 'tweet' from a string containing a JSON-like object.
    Handles escaped single quotes properly.
    Returns the tweet text as a string, or None if not found or invalid.
    """
    try:
        # Match pattern like {'tweet': '...'}, including escaped quotes
        match = re.search(r"\{'tweet':\s*'(.*?)'\}", text, re.DOTALL)
        if not match:
            return None

        tweet_raw = match.group(1)

        # Unescape any escaped single quotes
        tweet_clean = tweet_raw.replace("\\'", "'")
        return tweet_clean

    except Exception:
        return None


model_name = "Qwen/Qwen2.5-3B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(
    model_name,
    cache_dir="./hf_cache",  # Optional, to use a specific cache location
    local_files_only=False   # Ensure it tries downloading
)

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto",
    cache_dir="./hf_cache",  # same here
    local_files_only=False
)


df=pd.read_csv('dataset_pandas.tsv', sep='\t')

dico_new={}

for i, row in tqdm(df.iterrows()):
    content =  row['content']
    promptFake=f"Can you create a natural tweet that would be considered disinformation, using the real information of the following news. Responds in this format ABOSLUTELY {{'tweet': '...'}} : {content}"
    promptReal=f"Can you create a natural tweet that agrees with the following news. Responds in this format ABOSLUTELY {{'tweet': '...'}} : {content}"

    messages = [
        {"role": "system", "content": "You are a grad student creating data for a dataset of fake news identification in tweets. Responds in this format {'tweet': '...'}"},
        {"role": "user", "content": promptReal}
    ]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=512
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    tweetReal=extract_tweet(response)



    messages = [
        {"role": "system", "content": "You are a grad student creating data for a dataset of fake news identification in tweets. Responds in this format {'tweet': '...'}"},
        {"role": "user", "content": promptFake}
    ]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=512
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    tweetFake=extract_tweet(response)


    dico_new[len(dico_new)]={'index_news':i, 'Fake Tweet': tweetFake, 'Real Tweet': tweetReal, 'og_new':content}

df_final=pd.DataFrame.from_dict(dico_new, orient='index')
df_final.to_csv('Datav01.tsv', sep='\t')