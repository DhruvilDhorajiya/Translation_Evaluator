import asyncio
from typing import Any, Dict

from config import AVAILABLE_LANGUAGES
from config import AVAILABLE_MODELS
from config import LANGUAGE_DISPLAY_NAMES
from config import MODEL_CONFIG
import streamlit as st

from services import TranslationService


class TranslationUI:

  def __init__(self):
    self.service = TranslationService()
    self._setup_page()
    self._setup_sidebar()

  def _setup_page(self):
    """Setup the Streamlit page layout."""
    st.title("Translation Evaluator")

  def _setup_sidebar(self):
    """Setup the sidebar with workflow explanation."""
    st.sidebar.title("How it Works")

    st.sidebar.markdown("""
    ### Translation Process
    1. **Input Text & Languages**
       - Enter your text
       - Select source and target languages
       - Optionally customize the API endpoint
    
    2. **Reference Translation**
       - Text is sent to the provided endpoint
       - Translation is received and used as reference
    
    3. **LLM Translation** (if enabled)
       - Text is translated using selected LLM model
       - This provides a second translation for comparison
    
    ### Evaluation Process
    1. **Cosine Similarity**
       - Measures text similarity between translations
       - Uses sentence-transformers model
       - Score ranges from 0% to 100%
    
    2. **LLM Evaluation**
       - Compares translations in detail
       - Evaluates accuracy and fluency
       - Provides detailed analysis
    
    ### Scoring Guide
    - **Cosine Similarity:**
      - 🟢 > 80%: High similarity
      - 🟡 60-80%: Moderate similarity
      - 🔴 < 60%: Low similarity
    
    - **Categories:**
      - 🟢 Excellent
      - 🟡 Very Good/Good
      - 🔴 Needs Improvement
    """)

  def render_input_section(self) -> tuple[str, str, str, bool, str, str]:
    """Render the input section and return user inputs."""
    # Add endpoint input at the top
    endpoint_url = st.text_input(
        "Translation API Endpoint",
        value="https://fragma-api-dev.yanolja.com/pre/translate",
        help="Enter the complete endpoint URL for translation")

    text_input = st.text_area("Enter text to translate",
                              placeholder="Type or paste your text here...",
                              height=150)

    # Create options for language selection with display names
    language_options = [
        (code, LANGUAGE_DISPLAY_NAMES[code]) for code in AVAILABLE_LANGUAGES
    ]

    col1, col2 = st.columns(2)
    with col1:
      source_language = st.selectbox(
          "Source Language",
          options=[code for code, _ in language_options],
          format_func=lambda x: LANGUAGE_DISPLAY_NAMES[x],
          index=0  # Default to EN-US
      )

    with col2:
      target_language = st.selectbox(
          "Target Language",
          options=[code for code, _ in language_options],
          format_func=lambda x: LANGUAGE_DISPLAY_NAMES[x],
          index=1  # Default to JA-JP
      )

    evaluate_translation = st.checkbox("Evaluate translation with LLM",
                                       value=True)

    model_name = None
    if evaluate_translation:
      model_options = [
          (display, tech) for tech, display in MODEL_CONFIG.items()
      ]
      selected_display_name = st.selectbox(
          "Select Model for Evaluation",
          [display for display, _ in model_options],
          index=2)
      model_name = next(tech for display, tech in model_options
                        if display == selected_display_name)

    return text_input, source_language, target_language, evaluate_translation, model_name, endpoint_url

  def render_translation_results(self, result: Dict[str, Any]):
    """Render translation and evaluation results."""
    if not result["success"]:
      st.error(result["error"])
      return

    st.success("Translation completed!")

    # Reference Translation
    st.subheader("Reference Translation (Endpoint)")
    st.write(result["reference_translation"])
    st.divider()

    # OpenAI Translation
    if "openai_translation" in result:
      st.subheader("OpenAI Translation")
      st.write(result["openai_translation"])
      st.divider()

      # Similarity Score
      if "similarity_score" in result:
        similarity = result["similarity_score"]
        st.subheader("Cousine Similarity")
        # Color code based on similarity score
        color = "green" if similarity > 0.8 else "orange" if similarity > 0.6 else "red"
        st.markdown(
            f"<span style='color: {color}; font-size: 20px;'>{similarity:.2%}</span>",
            unsafe_allow_html=True)
        st.divider()

      # Evaluation Results
      if "evaluation" in result:
        st.subheader("Evaluation with LLM")

        # Get evaluation data
        evaluation_data = result["evaluation"]
        category = evaluation_data.get("category", "N/A")
        reason = evaluation_data.get("reason", "N/A")

        # Display category with emoji
        emoji = "🟢" if category.lower(
        ) == "excellent" else "🟡" if category.lower() in ["very good", "good"
                                                         ] else "🔴"
        st.markdown(f"**Category:** {emoji} {category}")

        # Display reason
        st.markdown("**Detailed Analysis:**")
        st.write(reason)


def main():
  ui = TranslationUI()

  # Initialize session state for text input if not exists
  if "text_input" not in st.session_state:
    st.session_state.text_input = ""

  text_input, source_language, target_language, evaluate_translation, model_name, endpoint_url = ui.render_input_section(
  )

  # Update session state
  st.session_state.text_input = text_input

  # Use session state for button disabled check
  translate_disabled = not bool(st.session_state.text_input.strip())

  if st.button("Translate", type="primary", disabled=translate_disabled):
    if text_input.strip():
      with st.spinner("Processing..."):
        result = asyncio.run(
            ui.service.translate_text(text=text_input.strip(),
                                      source_language=source_language,
                                      target_language=target_language,
                                      evaluate=evaluate_translation,
                                      model_name=model_name,
                                      endpoint_url=endpoint_url))
        ui.render_translation_results(result)


if __name__ == "__main__":
  main()
