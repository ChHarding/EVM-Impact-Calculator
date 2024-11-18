import plotly.graph_objects as go
import numpy as np
import os
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import streamlit as st
import plotly.io as pio
from PIL import Image

# Set Plotly renderer
pio.renderers.default = 'browser'

# Ensure output directory exists
os.makedirs("images", exist_ok=True)

# Function to create a responsive Plotly chart
def create_plotly_chart():
    # Set random seed for reproducibility
    np.random.seed(1)

    # Generate random data
    N = 100
    x = np.random.rand(N)
    y = np.random.rand(N)
    colors = np.random.rand(N)
    sz = np.random.rand(N) * 30

    # Create figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode="markers",
        marker=dict(
            size=sz,
            color=colors,
            opacity=0.6,
            colorscale="Viridis"
        )
    ))

    # Update layout for dynamic screen adjustment
    fig.update_layout(
        autosize=True,
        margin=dict(l=10, r=10, t=10, b=10)
    )

    return fig

# Function to export charts to a PDF with high resolution
def export_charts_to_pdf(chart1, chart2, title, settings_text):
    # Create an in-memory bytes buffer for the PDF
    pdf_buffer = io.BytesIO()

    # Initialize a PDF canvas
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    width, height = letter

    # Add title to the PDF
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 72, title)

    # Add settings text
    c.setFont("Helvetica", 12)
    text_y = height - 100
    for line in settings_text.split('\n'):
        c.drawString(72, text_y, line)
        text_y -= 14


    # Convert Plotly charts to high-resolution images
    chart1_img = Image.open(io.BytesIO(chart1.to_image(format="png", width=1200, height=600, scale=2)))
    chart2_img = Image.open(io.BytesIO(chart2.to_image(format="png", width=1200, height=600, scale=2)))

    # Add the first chart image to the PDF
    chart1_reader = ImageReader(chart1_img)
    c.drawImage(chart1_reader, 10,text_y- 300, width=500, height=250)

    # Add the second chart image to the PDF
    chart2_reader = ImageReader(chart2_img)
    c.drawImage(chart2_reader, 10, text_y - 650, width=500, height=250)

    # Finalize and save the PDF
    c.showPage()
    c.save()

    # Reset buffer position
    pdf_buffer.seek(0)
    return pdf_buffer

# Streamlit app logic
st.title("Plotly to PDF Exporter")

# Generate Plotly charts
fig1 = create_plotly_chart()
fig2 = create_plotly_chart()  # Duplicate for simplicity; replace with another chart if needed

# Display charts in the Streamlit app
st.subheader("Generated Charts")
st.plotly_chart(fig1, use_container_width=True)
st.plotly_chart(fig2, use_container_width=True)

# Single button for export and download
if st.button("Export and Download PDF", key="export_pdf"):
    st.write("Exporting PDF...")  # Debug log

    # Generate the PDF
    pdf_buffer = export_charts_to_pdf(fig1, fig2, "My Charts PDF", "Custom Settings Applied")

    if pdf_buffer:
        st.success("PDF generated successfully!")
        # Serve the file for download
        st.download_button(
            label="Click here to download your PDF",
            data=pdf_buffer,
            file_name="charts.pdf",
            mime="application/pdf",
            key="download_button"
        )
    else:
        st.error("PDF generation failed. Please check your input.")
