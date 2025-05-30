# Fragma API Chat Interface

A Streamlit application that allows users to interact with the Fragma API's chat completion endpoint.

## Features

- Select from multiple LLM models (GPT-4, GPT-4o, Claude, Gemini, etc.)
- Custom system prompt input
- Interactive chat interface
- Secure API key handling

## Setup and Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   streamlit run app.py
   ```

## Usage

1. Enter your Fragma API base URL and API key in the sidebar
2. Click "Validate API Key" to verify your credentials
3. Select a model from the dropdown
4. Optionally, enter a system prompt to guide the model's behavior
5. Start chatting in the main window

## Available Models

- gpt-35-turbo
- gpt-4
- gpt-4o
- gemini-15-pro
- claude-35-sonnet

## API Details

The application uses the following API endpoint format:

- URL: `https://[BASE_URL]/openai/deployments/{modelName}/chat/completions`
- Method: POST
- Headers:
  - Content-Type: application/json
  - api-key: [API_KEY]
