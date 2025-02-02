import google.generativeai as genai
import os


class OCR:
    def __init__(self, api_key=None):
        if api_key is None:
            try:
                with open(".env", "r") as f:
                    for line in f:
                        if "GEMINI_API_KEY" in line:
                            self.api_key = line.split("=")[1]
                            break
            except Exception as e:
                self.api_key = ""
        else:
            self.api_key = api_key
            genai.configure(api_key=self.api_key)
            # supported_models = genai.list_models()
            # for model in supported_models:
            #     print(model)
            self.model = genai.GenerativeModel("models/gemini-2.0-flash-exp")

    def extract_text(self, image_path):
        prompt = "Extract text from the image without changing the content. Please use $...$ or $$...$$ to denote math expressions."
        
        myfile = genai.upload_file(image_path)
        
        response = self.model.generate_content(
            contents=[
                prompt,
                myfile
            ]
        )

        return response.parts[0].text
        