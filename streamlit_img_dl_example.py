import streamlit as st
import plotly.express as px
import plotly, ipykernel, kaleido
from PIL import Image, ImageDraw, ImageFont
import io



# Run pip install -U kaleido to install the kaleido package needed for plotly to_image()

# Step 1: Generate the Plotly graph
df = px.data.iris()
fig = px.scatter(df, x='sepal_width', y='sepal_length', color='species')

# Display the Plotly graph in Streamlit
st.plotly_chart(fig)

# Step 2: Take a "screenshot" of the Plotly graph
img_bytes = fig.to_image(format="png")

# Step 3: Add text to the image using PIL
image = Image.open(io.BytesIO(img_bytes))
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()  # You can also provide your custom font here if needed
text = "Sample Text"
text_position = (10, 10)
draw.text(text_position, text, font=font, fill="black")

# Save the modified image to a BytesIO object
img_buffer = io.BytesIO()
image.save(img_buffer, format="PNG")
img_buffer.seek(0)

# Step 4: Provide a download link in Streamlit
st.download_button(
    label="Download image",
    data=img_buffer,
    file_name="modified_image.png",
    mime="image/png"
)
