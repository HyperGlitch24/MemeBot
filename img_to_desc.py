import os
import json
import base64
from pathlib import Path
import re
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

# print("API Key Loaded:", os.getenv("GOOGLE_API_KEY")) 


llm = ChatOpenAI(model = "gpt-4o")


def img_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')
    

def generate_meme_description(image_path):

    # print(f"Processing image: {image_path.name}")


    extension = image_path.suffix.lower()
    if extension == ".jpg" or extension == ".jpeg":
        mime_type = "image/jpeg"
    elif extension == ".png":
        mime_type = "image/png"
    else:
        # print(f"Warning: Unsupported file type {extension} for {image_path.name}")
        return None


    prompt = """
    You are a meme cataloging expert. Analyze this meme template.
    Return a single JSON object with "name", "filename", and "description".
    Do not include any other text or markdown formatting.
    """

    message = HumanMessage(
        content =[
            {"type": "text", "text": prompt},
            {"type": "text", "text": f"The file name is : {image_path.name}"},
            {"type": "image_url", "image_url": { "url" : f"data:{mime_type};base64,{img_to_base64(image_path)}"}
             },

        ]
    )


    try:
       response = llm.invoke([message])

       json_match = re.search(r'\{.*}', response.content, re.DOTALL)
       if json_match:
           json_string = json_match.group(0)
           return json.loads(json_string)
       else:
        #    print(f"No JSON found in the response for {image_path.name}")
           return None

    except Exception as e:
        print(f"An error occurred for {image_path.name}: {e}")
        return None   




if __name__ == "__main__":

    image_directory = Path("meme_templates")
    all_meme_data = []

    if not image_directory.exists():
        print(f"Directory {image_directory} does not exist.")
        exit(1) 

    else:
        image_files = list(image_directory.glob('*.jpg')) + list(image_directory.glob('*.png')) + list(image_directory.glob('*.jpeg'))
        for img_path in image_files:
            meme_data = generate_meme_description(img_path)
            print(meme_data)
            if meme_data:
                all_meme_data.append(meme_data)

        with open("memes.json", "w") as f:
            json.dump(all_meme_data,f, indent =4)

        print(f"Processed {len(all_meme_data)} images. Data saved to memes.json")