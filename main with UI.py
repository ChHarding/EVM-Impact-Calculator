#Import libraries
import streamlit as st
st.set_page_config(layout="wide")
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image, ImageDraw, ImageFont
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


# Run pip install -U kaleido to install the kaleido package needed for plotly to_image()
# Note on Windows must use kaleido version 0.1.0post1 for it to work with plotly


# Initialize session state for navigation and data storage
if 'page' not in st.session_state:
    st.session_state.page = 'upload_screen_1'  # Set default page
if 'cost_df' not in st.session_state:
    st.session_state.cost_df = None
if 'attribute_df' not in st.session_state:
    st.session_state.attribute_df = None

def main():
    # Route to the correct page based on session state
    if st.session_state.page == 'upload_screen_1':
        show_initial_screen()
    elif st.session_state.page == 'upload_screen_2':
        upload_attr_data_page()
    elif st.session_state.page == 'chart_screen':
        show_chart_screen()

def navigate_to_upload_screen_1():
    """modifies the session state page to the first screen"""
    st.session_state.page = 'upload_screen_1'

def navigate_to_upload_screen_2():
    """modifies the session state page to the second screen"""
    st.session_state.page = 'upload_screen_2'

def navigate_to_chart_screen():
    """modifies the session state page to the final screen"""
    st.session_state.page = 'chart_screen'

def show_initial_screen():
    """Launches the screen to upload the detailed datafile"""
    st.title("Interactive EVM Tool")
    st.write("This tool will take a cost profile and item attributes to create an understanding of changes to EVM data")
    st.subheader("Upload Cost Data")

    # File uploader to get the data file loaded 
    uploaded_file = st.file_uploader("Choose your cost profile dataset", type=['csv', 'xlsx'])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            # Define expected columns for detail data
            expected_columns = ['Date', 'Cost', 'Item Number', 'Type']
            valid_file = validate_columns_exist(expected_columns, df)

            if valid_file:
                # Format columns
                df['Date'] = pd.to_datetime(df['Date'])  # Format date column
                df['Cost'] = pd.to_numeric(df['Cost'], errors='coerce')  # Format cost column as numeric
                df['Item Number'] = df['Item Number'].astype(str)  # Format item number as string
                df['Type'] = df['Type'].astype(str)  # Format type as string
                
                #create a data preview
                st.write("Data Preview:")
                st.dataframe(df.head())
                st.success(f"File '{uploaded_file.name}' successfully uploaded file")
                st.session_state.cost_df = df  # Store the dataframe in session state
                st.button("Next", on_click=navigate_to_upload_screen_2)

            else:
                st.error(f"missing columns from file")
                st.write("required columns: Date, Cost, Item Number, Type")
                st.write("Data Preview:")
                st.dataframe(df.head())

        except Exception as e:
            st.error(f"Error: {e}")

def upload_attr_data_page():
    """Launches a screen to upload the data attributes"""
    st.title("Interactive EVM Tool")
    st.write("This tool will take a cost profile and item attributes to create an understanding of changes to EVM data")
    st.subheader("Upload Attribute Data")

    # File uploader to get item attributes data
    uploaded_file = st.file_uploader("Choose a file for feeder page", type=['csv', 'xlsx'])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)


            # Define expected columns for attributes data
            expected_columns = ['Item Number', 'Cost', 'Lead Time', 'Yield', 'Hours']
            valid_file = validate_columns_exist(expected_columns, df)

            if valid_file:

                # Format columns for attributes data
                df['Item Number'] = df['Item Number'].astype(str)  # Format item number as string
                df['Cost'] = pd.to_numeric(df['Cost'], errors='coerce')  # Format cost as numeric
                df['Lead Time'] = pd.to_numeric(df['Lead Time'], errors='coerce')  # Format lead time as numeric
                df['Yield'] = pd.to_numeric(df['Yield'], errors='coerce') / 100  # Format yield as percentage
                df['Hours'] = pd.to_numeric(df['Hours'], errors='coerce')  # Format hours as numeric

                #create a data preview
                st.write("Data Preview:")
                st.dataframe(df.head())
                st.success(f"File '{uploaded_file.name}' successfully uploaded file")
                st.session_state.attribute_df = df  # Store the dataframe in session state
                st.button("Next", on_click=navigate_to_chart_screen)
            else:
                st.error(f"missing required columns")
                st.write("required columns: Item Number, Cost, Lead Time, Yield, Hours")
                st.write("Data Preview:")
                st.dataframe(df.head())

        except Exception as e:
            st.error(f"Error: {e}")
            
def show_chart_screen():    
    """Launches the final screen that includes the charts based on the uploaded data file"""

    #determines multipliers that defines max value of slider bars
    material_multiplier = 10 
    leadtime_multiplier = 10 

    st.header("Interactive EVM Tool")
    # Generate PDF and display download button
    if st.session_state.cost_df is not None and st.session_state.attribute_df is not None:
     
            # create a unique list of items from the cost data file
            unique_items = st.session_state.cost_df['Item Number'].unique()

            #Use unique list to create dropdown box for user interaction
            selected_item = st.sidebar.selectbox("Select Item Number", unique_items)

            # Get default attribute values for the selected item
            item_attributes = st.session_state.attribute_df[st.session_state.attribute_df['Item Number'] == selected_item]
            
            if not item_attributes.empty:
                default_cost = item_attributes['Cost'].values[0]
                default_lead_time = item_attributes['Lead Time'].values[0]
                default_yield = item_attributes['Yield'].values[0]
                default_hours = item_attributes['Hours'].values[0]
            else:
                st.warning("No matching attributes found for the selected item.")
                return

            # Material Cost Slider Bar
            cost_slider = st.sidebar.slider(
                f"Material Cost (default: ${default_cost})",
                min_value=0.0, 
                max_value=float(material_multiplier*default_cost), 
                value=float(default_cost)
                )

            st.sidebar.divider()

            # Lead Time Slider Bar
            lead_time_slider = st.sidebar.slider(
                f"Lead Time (default: ${default_lead_time})", 
                min_value=0, 
                max_value=default_lead_time*leadtime_multiplier, 
                value=int(default_lead_time)
                )

            st.sidebar.divider()

            # Yield Slider Bar
            yield_slider = st.sidebar.slider(
                f"Lead Time (default: ${default_yield})", 
                min_value=0.0,
                max_value=1.0, 
                value=float(default_yield)
                )

            st.sidebar.divider()

            # Hours Slider Bar
            hours_slider = st.sidebar.slider(
                f"Hours (default: ${default_hours})", 
                min_value=0.0, 
                max_value=10.0, 
                value=float(default_hours)
                )

            # User attributes dictionary based on slider values
            user_attributes_dictionary = {
                "item_lead_time": lead_time_slider,
                "item_cost": cost_slider,
                "item_yeild": yield_slider,
                "item_hours": hours_slider
            }
           
            #Display charts in tabs 
            tab1, tab2 = st.tabs([
                "Cummulative Line Chart",
                "Bubble Chart",
                ]
                )

            with tab1: #Cummulative line chart
                
                placeholder = st.empty()
                with placeholder.container():
                    fig1 = generate_charts(st.session_state.cost_df, st.session_state.attribute_df, item_number=selected_item, user_attributes_dictionary=user_attributes_dictionary, chart_type="line_chart")


            with tab2: #Bubble chart
                placeholder = st.empty()
                with placeholder.container():
                    fig2 = generate_charts(st.session_state.cost_df, st.session_state.attribute_df,item_number=selected_item, user_attributes_dictionary=user_attributes_dictionary, chart_type="bubble_chart")


            # PDF Generation
            # Single button for export and download
            if st.button("Export and Download PDF", key="export_pdf"):
                initial_details = f"Initial Attributes: {default_yield*100}% Yield, ${default_cost:,.2f} item cost, {default_lead_time:,.2f} days lead time, {default_hours:,.2f} hours"
                new_details = f"Modified Attributes: {yield_slider*100}% Yield, ${cost_slider:,.2f} item cost, {lead_time_slider:,.2f} days lead time, {hours_slider:,.2f} hours"
                chart_details = f"{initial_details}\n{new_details}"
                chart_title = f"Modified Cost Profile for {selected_item}"
                st.write("Exporting PDF...")  # Debug log
                # Generate the PDF
                pdf_buffer = export_charts_to_pdf(fig1, fig2, chart_title, chart_details)
                
                if pdf_buffer:
                    st.success("PDF generated successfully!")
                    # Immediately serve the file for download
                    st.download_button(
                        label="Click here to download your PDF",
                        data=pdf_buffer,
                        file_name="charts.pdf",
                        mime="application/pdf",
                        key="download_button"
                    )
                else:
                    st.error("PDF generation failed. Please check your input.")

def generate_charts(
        cost_df,
        attributes_df, 
        user_attributes_dictionary,
        chart_type="line_chart",
        item_number=""
        ):
    """generates a line and bubble line chart"""

    #filter the cost_df by the desire item number
    filtered_df = filter_data(cost_df, item_number)
    filtered_attributes_df = filter_data(attributes_df, item_number)

    #Calculate the percent change impacts for each attribute
    impacts_dic = assess_impacts(filtered_attributes_df, user_attributes_dictionary)

    #Modify datafile based on impacts
    modified_df = modify_dataset(filtered_df, impacts_dic)

    #create a common X dataset - combined data set is three columns, x value of dates, y values of og costs, and y values of modified costs
    combined_data_set = create_common_x_value_by_month(filtered_df, modified_df)

    #Calculate EVM data and adds columns to the combined_data_set for the time-phased values
    combined_data_set_with_evm, evm_summary_data = calculate_evm(combined_data_set) 
    
    # Plot the relevant chart based on the chart type
    if chart_type == "line_chart":
        fig = plot_line_chart_with_percent_delta(combined_data_set_with_evm, evm_summary_data, "Baseline", "Modified", "")
        st.plotly_chart(fig, use_container_width=True)
    elif chart_type == "bubble_chart":
        fig = plot_bubble_chart(combined_data_set)
        st.plotly_chart(fig, use_container_width=True)

    return fig

def validate_columns_exist(expected_columns, df):
    """validates that the required columns exist in the uploaded dataframe"""
    # Check if all expected columns are present in attributes data
    return all(column in df.columns for column in expected_columns)
        
def filter_data(df, filter_item_number):
    """create a copy of the datafile that is filtered to specific item"""

    #create a acopy of the datafile to filter
    filtered_data = df.copy()

    if filter_item_number:
        filtered_data = filtered_data[filtered_data['Item Number'].astype(str) == filter_item_number]
    
    # Ensure there's data to plot
    if filtered_data.empty:
        print("Warning", "No data matches the filters.")        
        
    return filtered_data

def assess_impacts(initial_attributes, user_attributes_dictionary):

    """creates a dictionary of the impacts between initial attributes and user changes"""
    #item_lead_time changes the date only, change will be expressed in days. This will use averages in the case there are multiple data entries for attributes
    initial_lead_time = initial_attributes['Lead Time'].mean() 
    initial_cost = initial_attributes['Cost'].mean() 
    initial_yeild = initial_attributes['Yield'].mean() 
    initial_item_hours = initial_attributes['Hours'].mean() 

    #Changes
    new_lead_time = user_attributes_dictionary["item_lead_time"] - initial_lead_time #will be added to all line items
    new_cost_percent = (user_attributes_dictionary["item_cost"] -initial_cost)/initial_cost #percent will be applied to materials costs
    new_yield = user_attributes_dictionary["item_yeild"] - initial_yeild #already percentages, so this will give a percent change that should be applied to labor and material costs
    new_item_hours = (user_attributes_dictionary["item_hours"]-initial_item_hours)/initial_item_hours #percentage will be applied to labor costs

    #summarize change impacts
    material_impacts = (1 + new_cost_percent - new_yield)
    labor_impacts = (1 + new_item_hours - new_yield)
    date_impacts = new_lead_time

    #add to dictionary for simplicity downstream
    impacts_dictionary = {
        "material_impacts": material_impacts,  
        "labor_impacts": labor_impacts,     
        "date_impacts": date_impacts 
    }


    return impacts_dictionary

def modify_dataset(filtered_df, impacts_dic):
    """takes the filtered data and makes a modifed dataframe based on impacts"""

    modified_df = filtered_df.copy()

    #modify filtered_df cost column when type = hours by multiplying impacts_dic item labor_impacts
    modified_df.loc[filtered_df['Type'] == 'Labor', 'Cost'] *= impacts_dic['labor_impacts']

    #modify filtered_df cost column when type = material by multiplying impacts_dic item material_impacts
    modified_df.loc[filtered_df['Type'] == 'Material', 'Cost'] *= impacts_dic['material_impacts']

    #modify filtered_df date column by aadding impacts_dic item date_impacts
    modified_df['Date'] = pd.to_datetime(modified_df['Date'])
    date_impact = pd.Timedelta(days=impacts_dic['date_impacts'])
    modified_df['Date'] = modified_df['Date'] + date_impact
    
    return modified_df 

def create_common_x_value_by_month(filtered_df, modified_df):
    """creates a consistent date field between both datafiles for the x-axis"""
    # Ensure the Date columns are in datetime format
    filtered_df['Date'] = pd.to_datetime(filtered_df['Date'])
    modified_df['Date'] = pd.to_datetime(modified_df['Date'])

    # Resample both datasets by month, using the last day of each month, and sum the costs
    dataset_1_monthly = filtered_df.resample('ME', on='Date').sum().reset_index()
    dataset_2_monthly = modified_df.resample('ME', on='Date').sum().reset_index()

    # Extract x (dates) and y (costs) values for both datasets
    x_values_1 = dataset_1_monthly['Date']
    y_values_1 = dataset_1_monthly['Cost']

    x_values_2 = dataset_2_monthly['Date']
    y_values_2 = dataset_2_monthly['Cost']

    # Create a common x_value range from the minimum to the maximum dates
    min_date = min(x_values_1.min(), x_values_2.min())
    max_date = max(x_values_1.max(), x_values_2.max())

    # Generate the common date range at monthly intervals
    x_values_common = pd.date_range(start=min_date, end=max_date, freq='ME')

    # Create dictionaries to map costs to each date
    y_values_dict_1 = dict(zip(x_values_1, y_values_1))
    y_values_dict_2 = dict(zip(x_values_2, y_values_2))

    # Align y-values to the common date range, filling missing dates with 0
    y_values_1_aligned = [y_values_dict_1.get(date, 0) for date in x_values_common]
    y_values_2_aligned = [y_values_dict_2.get(date, 0) for date in x_values_common]

    # Combine data for export
    combined_data_set = pd.DataFrame({
        'Date': x_values_common,
        'Initial_Costs': y_values_1_aligned,
        'Modified_Costs': y_values_2_aligned
    })

    return combined_data_set

def calculate_evm(combined_data_set):
    """Calculates the Earned Value Management metrics for each date"""
    # Initialize lists to store calculated values
    pv_to_date_list = []
    schedule_percent_complete_list = []
    ac_to_date_list = []
    percent_complete_list = []
    ev_list = []
    schedule_variance_list = []
    cost_variance_list = []

    # Calculate BAC (Budget at Completion) and EAC (Estimate at Completion)
    BAC = combined_data_set['Initial_Costs'].sum()
    EAC = combined_data_set['Modified_Costs'].sum()

    # Calculate BAC (Budget at Completion) and EAC (Estimate at Completion)
    BAC = combined_data_set['Initial_Costs'].sum()
    EAC = combined_data_set['Modified_Costs'].sum()
    
    # Iterate over each date in the combined dataset
    for idx in range(len(combined_data_set)):
        # Filter the data to include only dates up to the current date
        current_data = combined_data_set.iloc[:idx + 1]

        # Calculate Planned Value (PV) to date (sum of Initial_Costs up to current date)
        PV_to_date = current_data['Initial_Costs'].sum()
        pv_to_date_list.append(PV_to_date)

        # Calculate Schedule Percent Complete (PV_to_date / BAC)
        schedule_percent_complete = PV_to_date / BAC * 100 if BAC != 0 else 0
        schedule_percent_complete_list.append(schedule_percent_complete)

        # Calculate Actual Cost (AC) to date (sum of Modified_Costs up to current date)
        AC_to_date = current_data['Modified_Costs'].sum()
        ac_to_date_list.append(AC_to_date)

        # Calculate Percent Complete (AC_to_date / EAC)
        percent_complete = AC_to_date / EAC * 100 if EAC != 0 else 0
        percent_complete_list.append(percent_complete)

        # Calculate Earned Value (EV) as % complete times BAC
        EV = percent_complete * BAC / 100
        ev_list.append(EV)

        # Calculate Schedule Variance (SV) as PV_to_date - EV
        schedule_variance = PV_to_date - EV
        schedule_variance_list.append(schedule_variance)

        # Calculate Cost Variance (CV) as EV - AC_to_date
        cost_variance = EV - AC_to_date
        cost_variance_list.append(cost_variance)

    # Add calculated values to the combined_data_set
    combined_data_set['PV_to_Date'] = pv_to_date_list
    combined_data_set['Schedule_Percent_Complete'] = schedule_percent_complete_list
    combined_data_set['AC_to_Date'] = ac_to_date_list
    combined_data_set['Percent_Complete'] = percent_complete_list 
    combined_data_set['Earned_Value'] = ev_list
    combined_data_set['Schedule_Variance'] = schedule_variance_list
    combined_data_set['Cost_Variance'] = cost_variance_list

    # Create summary data for EVM
    evm_summary_data = {
        'BAC': BAC,
        'EAC': EAC,

    }




    return combined_data_set, evm_summary_data 

def plot_line_chart_with_percent_delta(evm_data, evm_summary_data, data_label_1, data_label_2, chart_title):
    """creates a line chart with both datasets that displays EVM data"""

    #Data for the chart
    x_values = evm_data["Date"]
    y_values_1 = evm_data["Initial_Costs"].cumsum()
    y_values_2 = evm_data["Modified_Costs"].cumsum()

    #Summary data for the annotations
    BAC = evm_summary_data["BAC"]
    EAC = evm_summary_data["EAC"]

    if (BAC-EAC)/BAC < .05 and (BAC-EAC)/BAC > 0: #BAC is greater but they are close together
        space_modifier = .01*BAC
    elif (BAC-EAC)/BAC > -0.05: #EAC is greater
        space_modifier = -.01*BAC
    else:
        space_modifier = 0

    # Calculate BAC
    BAC = max(y_values_1)

    #Calculate EAC
    EAC = max(y_values_2)


    # Create the figure
    fig = go.Figure()

    # Add the first line (hoverinfo='skip' ensures it doesn't show on hover)
    fig.add_trace(go.Scatter(x=x_values, 
                             y=y_values_1, 
                             mode='lines', 
                             name=data_label_1, 
                             line=dict(color='blue'),
                             showlegend=False,
                             hoverinfo='skip'))  # Skip hover for this line


    # Add the second line (hoverinfo='skip' ensures it doesn't show on hover)
    fig.add_trace(go.Scatter(x=x_values, 
                             y=y_values_2, 
                             mode='lines', 
                             name=data_label_2, 
                             line=dict(color='green', 
                                       dash='dash'),
                             showlegend=False,
                             hoverinfo='skip'))  # Skip hover for this line


    fig.add_annotation(
        x=1.01,  # Position outside the plot area (in paper coordinates)        
        y=BAC+space_modifier,
        text=f'BAC ${BAC:,.2f}',
        showarrow=False,
        yref = 'y',
        xref='paper',  # Reference the figure's width, not the data coordinates        
        xanchor="left",  # Align text to the left of the annotation point
        yanchor="middle",
        font=dict(
            color='blue'  # Set the font color to blue
        )
    )
    fig.add_annotation(
        x=1.01,
        y=EAC-space_modifier,
        text=f'EAC ${EAC:,.2f}',
        showarrow=False,
        yref = 'y',
        xref='paper',  # Reference the figure's width, not the data coordinates
        xanchor="left",  # Align text to the left of the annotation point
        yanchor="middle",
        font=dict(
            color='green'  # Set the font color to blue
        )
    )
    

   # Add a third trace for hover text with the percent delta only
    fig.add_trace(go.Scatter(
        x=x_values, 
        y=y_values_1, 
        mode='lines',
        line=dict(color='rgba(0,0,0,0)'), # Set the line color to transparent
        customdata=evm_data[['Schedule_Percent_Complete', 'Percent_Complete', 'AC_to_Date', 'Earned_Value', 'Schedule_Variance', 'Cost_Variance', 'PV_to_Date']],        
        hovertemplate=(
            'Cummulative to date metrics<br>'
            '   Planned value to date: $%{customdata[6]:,.2f}<br>'
            '   Actual Cost to date: $%{customdata[2]:,.2f}<br>'
            '   Earned Value to date: $%{customdata[3]:,.2f}<br>'
            
            '<br>planned % Complete: %{customdata[0]:.2f}% <br>'
            'current % Complete: %{customdata[1]:.2f}% <br>'

            '<br>Variances <br>'
            '   Schedule Variance: $%{customdata[4]:,.2f}<br>'
            '   Cost Variance: $%{customdata[5]:,.2f}<extra></extra>'
        )
        ,        
        showlegend=False))  # No legend entry for this trace

    # Customize the layout
    fig.update_layout(
        title='Cummulative Cost Profile',
        height = 600,
        hovermode='x unified',
        yaxis_tickformat=',.0f',
        showlegend=False,
        plot_bgcolor='white',  # Set the plot background to white
        paper_bgcolor='white',  # Set the overall chart background to white
        xaxis=dict(showgrid=True, 
                   gridcolor='lightgray',
                   color='green'),  # Set grid lines for better visibility
        yaxis=dict(showgrid=True, 
                   gridcolor='lightgray',
                   color='blue'),
        margin=dict(l=80, 
                    r=150, 
                    t=50, 
                    b=50)  # Adjust 'r' for right margin size (150px in this example)
    )

    #format axis
    fig.update_xaxes(
        tickformat='%Y-%m',  # Format for datetime tick marks
        tickmode='auto',        # Automatically determine the number of ticks
        tickangle=0,           # Angle of the tick labels
        title_text='Date',
        title_font=dict(color='black'),  # Explicitly set title font color
        tickfont=dict(color='black')      # Title of the x-axis
        )

    fig.update_yaxes(
        tickformat='$,.2f',  # Format for datetime tick marks
        tickmode='auto',        # Automatically determine the number of ticks
        title_font=dict(color='black'),  # Explicitly set title font color
        tickfont=dict(color='black')      # Title of the x-axis
        )

    return fig

def plot_bubble_chart(data):
    """create a bubble chart based on both datasets"""

    df = pd.DataFrame(data)

    # Create the bubble chart
    fig = go.Figure()

    # Add baseline and current data
    fig.add_trace(go.Scatter(
        x=pd.concat([df['Date'], df['Date']]),
        y=['Baseline'] * len(df) + ['Current'] * len(df),
        mode='markers',
        marker=dict(
            size=pd.concat([df['Initial_Costs'], df['Modified_Costs']]),  # Bubble size represents the cost
            sizemode='area',
            sizeref=2.*max(df[['Initial_Costs', 'Modified_Costs']].values.flatten())/(40.**2),  # Adjust this value to scale bubble sizes
            sizemin=4,
            color=['blue'] * len(df) + ['green'] * len(df),
            opacity=0.6
        ),
        hovertemplate='Date: %{x}<br>Cost: $%{marker.size}<extra></extra>'  # Show cost value in hover text
    ))

    # Customize the layout
    fig.update_layout(
        title='Cost Magnitudes by Month',
        height = 600,
        xaxis_title='Date',
        yaxis_title='',
        yaxis_tickformat=',.0f',
        yaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            tickvals=['Baseline', 'Current'],  # Define y-axis tick values
            ticktext=['Baseline', 'Current'],  # Define y-axis tick labels
            range=[-1, 2]  # Add spacing at the top and bottom
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
        ),

        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False  # Remove the legend
    )
    fig.update_xaxes(
        tickformat='%Y-%m',  # Format for datetime tick marks
        tickmode='auto',        # Automatically determine the number of ticks
        tickangle=0,           # Angle of the tick labels
        title_font=dict(color='black'),  # Explicitly set title font color
        tickfont=dict(color='black')      # Title of the x-axis
        )

    fig.update_yaxes(
        tickmode='auto',        # Automatically determine the number of ticks
        title_font=dict(color='black'),  # Explicitly set title font color
        tickfont=dict(color='black')      # Title of the x-axis
        )
    return fig

def export_charts_to_pdf(chart1, chart2, title, settings_text):
    # Create an in-memory bytes buffer for the PDF
    pdf_buffer = io.BytesIO()

    # Initialize a PDF canvas
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    height = letter

    # Add title to the PDF
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 72, title)

    # Add settings text
    c.setFont("Helvetica", 9)
    text_y = height - 100
    for line in settings_text.split('\n'):
        c.drawString(72, text_y, line)
        text_y -= 14

    # Convert Plotly charts to images
    chart1_img = Image.open(io.BytesIO(chart1.to_image(format="png", width=1200, height=600, scale=2)))
    chart2_img = Image.open(io.BytesIO(chart2.to_image(format="png", width=1200, height=600, scale=2)))

    # Add the first chart image to the PDF
    chart1_reader = ImageReader(chart1_img)
    c.drawImage(chart1_reader, 72, text_y - 300, width=500, height=250)

    # Add the second chart image to the PDF
    chart2_reader = ImageReader(chart2_img)
    c.drawImage(chart2_reader, 72, text_y - 600, width=500, height=250)

    # Finalize and save the PDF
    c.showPage()
    c.save()

    # Reset buffer position
    pdf_buffer.seek(0)
    return pdf_buffer



# Run the app
if __name__ == "__main__":
    main()

