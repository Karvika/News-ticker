from google.adk.agents import Agent
import google.generativeai as genai
from google.adk.tools.base_tool import BaseTool
from datetime import datetime
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

# Configure Gemini API with explicit key
genai.configure(api_key=api_key)

class NewsUpdateTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="news_update",
            description="Generate current AI news headlines using Gemini model"
        )
        self.schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        # Try to initialize the preferred model with fallback
        self.model = None
        models_to_try = ['gemini-1.5-pro', 'gemini-1.5-flash']
        
        for model_name in models_to_try:
            try:
                self.model = genai.GenerativeModel(model_name)
                print(f"Successfully initialized {model_name} model")
                break
            except Exception as e:
                print(f"Error initializing {model_name}: {str(e)}")
                if model_name == models_to_try[-1]:  # If this was the last model to try
                    raise Exception(f"Failed to initialize any Gemini model: {str(e)}")

    def execute(self, inputs=None):
        try:
            current_time = datetime.now().strftime("%I:%M %p")
            
            # Generate headlines using Gemini
            prompt = """You are a professional AI news generator.
            Generate 5 factual headlines about recent artificial intelligence developments.
            Focus on major AI companies, research breakthroughs, and industry developments.
            Keep headlines professional and informative.
            Format: Return exactly 5 headlines, one per line.
            Do not include any numbering or extra text."""

            generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 256,
            }

            response = self.model.generate_content(
                contents=prompt,
                generation_config=generation_config
            )
            
            if hasattr(response, 'text'):
                # Split response into lines and clean up
                headlines_text = [line.strip() for line in response.text.split('\n') if line.strip()][:5]
                
                # Process headlines
                headlines = []
                for i, headline_text in enumerate(headlines_text):
                    headline = {
                        "id": str(i + 1),
                        "title": headline_text,
                        "timestamp": current_time,
                        "isLatest": i == 0
                    }
                    headlines.append(headline)
                
                if headlines:
                    return json.dumps(headlines)
                else:
                    raise Exception("No valid headlines generated")
            else:
                raise Exception("No text in Gemini response")
            
        except Exception as e:
            # Log the actual error for debugging
            print(f"Error in NewsUpdateTool: {str(e)}")
            return json.dumps({
                "error": f"News generation failed: {str(e)}",
                "fallback_headlines": [
                    {
                        "id": "1",
                        "title": "OpenAI Announces Major Updates to GPT-4",
                        "timestamp": current_time,
                        "isLatest": True
                    },
                    {
                        "id": "2",
                        "title": "Google DeepMind Achieves Breakthrough in AI Research",
                        "timestamp": current_time,
                        "isLatest": False
                    },
                    {
                        "id": "3",
                        "title": "Microsoft Enhances Azure AI Capabilities",
                        "timestamp": current_time,
                        "isLatest": False
                    },
                    {
                        "id": "4",
                        "title": "AI Ethics Board Releases New Guidelines",
                        "timestamp": current_time,
                        "isLatest": False
                    },
                    {
                        "id": "5",
                        "title": "Meta's AI Research Shows Promise in Language Understanding",
                        "timestamp": current_time,
                        "isLatest": False
                    }
                ]
            })

root_agent = Agent(
    name="ai_news_agent",
    model="gemini-pro",
    description="AI News headlines agent",
    instruction="Generate and return the latest AI news headlines.",
    tools=[NewsUpdateTool()]
)
