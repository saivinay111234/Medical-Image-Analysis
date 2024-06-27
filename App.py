# Importing necessary libraries
import streamlit as st
import google.generativeai as genai
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
from reportlab.lib.units import inch

# Calling api_key
from API_Key import api_key

# Configure Gen AI with API Key
genai.configure(api_key=api_key)

# Creating the model
generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

# Apply safety settings
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

system_prompt = """
As a highly skilled medical practitioner specializing in image analysis, you are tasked with examining medical images for a renowned 
hospital. Your expertise is crucial in identifying any anomalies, diseases, or health issues that may be present in the image.

Your Responsibilities:
1. Detailed Analysis: Thoroughly analyze each image and give me detailed analysis focusing on identifying any abnormal findings.
2. Findings Report: Document all observed anomalies or signs of diseases, clearly articulating these findings in a structured format.
3. Recommendations and Next Steps: Based on your analysis, suggest potential 2 to 3 recommendations and next steps, including further tests or treatments as applicable.
4. Treatment Suggestions: If appropriate, recommend possible treatment options or interventions.

Important Notes:
1. Scope of Response: Only respond if the image pertains to human health issues.
2. Clarity of Images: In cases where the image quality impedes clear analysis, note that certain aspects are unable to be determined based on the provided image.
3. Disclaimer: Accompany your analysis with a disclaimer to consult a doctor before making any medical decisions.
4. Clinical Guidance: Your insights are valuable in guiding clinical decisions. Please proceed with the analysis adhering to the structured approach outlined above.

Please provide the output with the following headings in bold:

1. Detailed Analysis
2. Findings Report
3. Recommendations and Next Steps
4. Treatment Suggestions(in list)
"""

# Configure the model
model = genai.GenerativeModel(
    model_name="gemini-1.0-pro-vision-latest",
    generation_config=generation_config,
    safety_settings=safety_settings
)

def create_pdf(image_path, analysis):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Add the image
    im = Image(image_path, 2 * inch, 2 * inch)
    elements.append(im)

    # Add the analysis text
    styles = getSampleStyleSheet()
    analysis_paragraph = Paragraph(analysis.replace('\n', '<br/>'), styles['BodyText'])
    elements.append(analysis_paragraph)

    doc.build(elements)
    buffer.seek(0)
    return buffer

# Creating front end web with streamlit
st.set_page_config(page_title='Medical Image Analysis', page_icon=':robot:')

# Creating a logo
st.image('image.png', width=200)

# Create a title
st.title("🧑‍⚕️🩺 Medical Image Analysis 📊")
st.subheader('', divider='rainbow')

# Create Subtitle
st.subheader("""An Application that can help the users to understand the medical problem by performing analysis from the given Medical condition image""")

# Initialize session state for the analysis
if 'analysis' not in st.session_state:
    st.session_state['analysis'] = None

# Upload the Image
file = st.file_uploader("Upload the medical image for analysis", type=["png", "jpg", "jpeg"])
if file:
    st.image(file, width=200)
submit_button = st.button("Generate the Analysis")

if submit_button and file:
    image_data = file.getvalue()

    image_parts = [
        {
            "mime_type": "image/jpeg",
            "data": image_data
        }
    ]

    prompt_parts = [
        image_parts[0],
        system_prompt,
    ]

    response = model.generate_content(prompt_parts)
    if response:
        st.session_state['analysis'] = response.text

        # Save the uploaded image to a file
        image_path = "uploaded_image.jpg"
        with open(image_path, "wb") as f:
            f.write(image_data)

        # Generate the PDF
        pdf_buffer = create_pdf(image_path, response.text)

        # Add a download button
        st.download_button(
            label="Download Analysis as PDF",
            data=pdf_buffer,
            file_name="medical_analysis.pdf",
            mime="application/pdf"
        )

# Display the analysis if it exists in the session state
if st.session_state['analysis']:
    st.title("Below is the analysis for the above medical condition")
    st.write(st.session_state['analysis'])
