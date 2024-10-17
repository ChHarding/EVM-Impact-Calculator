
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

#Run code with streamlit run "c:/Users/CassieLynn/Documents/Python/CassieSmith - EVM Impacts Project/EVM-Impact-Calculator/main.py"  replacing the file location 

def execute_code():

    st.title("Interactive EVM Analysis")
        
    #User Inputs
    item_number = "10001"
    item_lead_time = 20 #days
    item_cost = 22 #usd
    item_yeild = .80 #%
    item_hours = 2.5 #hours
    cost_datafile_location = "sample data/InitialUploadData.csv"  # Ch alwasys use relative paths!
    attrib_datafile_location = "sample data/AttributesData.csv"


    #create dictionary of user inputs
    user_attributes_dictionary = {
        "item_lead_time": item_lead_time,  
        "item_cost": item_cost,     
        "item_yeild": item_yeild,
        "item_hours":item_hours
    }

    #Upload both datafiles
    cost_df = import_cost_data(cost_datafile_location)
    attributes_df = import_attributes_data(attrib_datafile_location)

    #filter the cost_df by the desire item number
    filtered_df = filter_data(cost_df, item_number)
    filtered_attributes_df = filter_data(attributes_df, item_number)

    #Calculate the percent change impacts for each attribute
    impacts_dic = assess_impacts(filtered_attributes_df, user_attributes_dictionary)

    #Modify datafile based on impacts
    modified_df = modify_dataset(filtered_df, impacts_dic)

    #create a common X dataset - combined data set is three columns, x value of dates, y values of og costs, and y values of modified costs
    combined_data_set = create_common_x_value(filtered_df, modified_df)

    #Calculate EVM data and adds columns to the combined_data_set for the time-phased values
    combined_data_set_with_evm, evm_summary_data = calculate_evm(combined_data_set) 
    
    # Plot line chart using Streamlit
    st.header("Line Chart: Time Phased Data")
    plot_line_chart_with_percent_delta(combined_data_set_with_evm, evm_summary_data, "Baseline", "Modified", "Time Phased Data")

    # Plot bubble chart using Streamlit
    st.header("Bubble Chart: Baseline vs Current Costs")
    plot_bubble_chart(combined_data_set)


def validate_columns_exist(expected_columns, df):

        # Check if all expected columns are present in attributes data
    for column in expected_columns:
        if column not in df.columns:
            print(f"Column '{column}' is missing in the attributes data file.")

def import_cost_data(datafile_location):
        

    # Import cost data file as CSV 
    cost_df = pd.read_csv(datafile_location)

    # Define expected columns
    expected_columns = ['Date', 'Cost', 'Item Number', 'Type']
    validate_columns_exist(expected_columns, cost_df)

    # Format columns
    cost_df['Date'] = pd.to_datetime(cost_df['Date'])  # Format date column
    cost_df['Cost'] = pd.to_numeric(cost_df['Cost'], errors='coerce')  # Format cost column as numeric
    cost_df['Item Number'] = cost_df['Item Number'].astype(str)  # Format item number as string
    cost_df['Type'] = cost_df['Type'].astype(str)  # Format type as string

    #return the dataset
    return cost_df

def import_attributes_data(datafile_location):
        

    # Import attributes data file as CSV 
    attributes_df = pd.read_csv(datafile_location)

    # Define expected columns for attributes data
    expected_columns = ['Item Number', 'Cost', 'Lead Time', 'Yield', 'Hours']
    validate_columns_exist(expected_columns, attributes_df)
    
    # Format columns for attributes data
    attributes_df['Item Number'] = attributes_df['Item Number'].astype(str)  # Format item number as string
    attributes_df['Cost'] = pd.to_numeric(attributes_df['Cost'], errors='coerce')  # Format cost as numeric
    attributes_df['Lead Time'] = pd.to_numeric(attributes_df['Lead Time'], errors='coerce')  # Format lead time as numeric
    attributes_df['Yield'] = pd.to_numeric(attributes_df['Yield'], errors='coerce') / 100  # Format yield as percentage
    attributes_df['Hours'] = pd.to_numeric(attributes_df['Hours'], errors='coerce')  # Format hours as numeric

    #return the dataset
    return attributes_df

def filter_data(df, filter_item_number):

    #create a acopy of the datafile to filter
    filtered_data = df.copy()  #CH

    if filter_item_number:
        filtered_data = filtered_data[filtered_data['Item Number'].astype(str) == filter_item_number]
    
    # Ensure there's data to plot
    if filtered_data.empty:
        print("Warning", "No data matches the filters.")        
        
    return filtered_data

def assess_impacts(initial_attributes, user_attributes_dictionary):

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
    material_impacts = (1 + new_cost_percent + new_yield)
    labor_impacts = (1 + new_item_hours + new_yield)
    date_impacts = new_lead_time

    #add to dictionary for simplicity downstream
    impacts_dictionary = {
        "material_impacts": material_impacts,  
        "labor_impacts": labor_impacts,     
        "date_impacts": date_impacts 
    }


    return impacts_dictionary

def modify_dataset(filtered_df, impacts_dic):

    modified_df = filtered_df.copy()

    #modify filtered_df cost column when type = hours by multiplying impacts_dic item labor_impacts
    modified_df.loc[filtered_df['Type'] == 'Labor', 'Cost'] *= impacts_dic['labor_impacts']

    #modify filtered_df cost column when type = material by multiplying impacts_dic item material_impacts
    modified_df.loc[filtered_df['Type'] == 'Material', 'Cost'] *= impacts_dic['material_impacts']

    #modify filtered_df date column by aadding impacts_dic item date_impacts
    modified_df['Date'] += pd.to_timedelta(impacts_dic['date_impacts'], unit='d')

    return modified_df 

def create_common_x_value(filtered_df, modified_df):

        # Create Dataset arrays for "Baseline" and "Current"
        dataset_1 = filtered_df
        dataset_2 = modified_df

        # Extract x (dates) and y (build costs) values for both datasets
        x_values_1 = dataset_1['Date']
        y_values_1 = dataset_1['Cost']

        x_values_2 = dataset_2['Date']
        y_values_2 = dataset_2['Cost']      

        #create a common x_value
        min_date = min(x_values_1.min(),x_values_2.min())
        max_date = max(x_values_1.max(),x_values_2.max())

        x_values_common = pd.date_range(start=min_date, end=max_date)
        
        #Create dictionary of datasets
        y_values_dict_1 = dict(zip(x_values_1,y_values_1))
        y_values_dict_2 = dict(zip(x_values_2,y_values_2))

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
    for idx, current_date in  enumerate(combined_data_set['Date']):  # CH current_date is not used ?
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


    #Data for the chart
    x_values = evm_data["Date"]
    y_values_1 = evm_data["Initial_Costs"].cumsum()
    y_values_2 = evm_data["Modified_Costs"].cumsum()

    #Summary data for the annotations
    BAC = evm_summary_data["BAC"]
    EAC = evm_summary_data["EAC"]

    #add in a modifier if BAC and EAC are too close together
    print((BAC-EAC)/BAC)
    print(.1*BAC)

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
        title=dict(           
            text=chart_title,
            x=0.5,
            xanchor='center',
            yanchor='top'
        ),

        hovermode='x unified',
        yaxis_tickprefix='$',
        yaxis_tickformat=',.0f',
        showlegend=False,
        plot_bgcolor='white',  # Set the plot background to white
        paper_bgcolor='white',  # Set the overall chart background to white
        xaxis=dict(showgrid=True, 
                   gridcolor='lightgray'),  # Set grid lines for better visibility
        yaxis=dict(showgrid=True, 
                   gridcolor='lightgray'),
        margin=dict(l=80, 
                    r=150, 
                    t=50, 
                    b=50)  # Adjust 'r' for right margin size (150px in this example)
    )

    # Update x-axis to show datetime tick marks and values
    fig.update_xaxes(
        tickformat='%Y-%m-%d',  # Format for datetime tick marks
        tickmode='auto',        # Automatically determine the number of ticks
        tickangle=45,           # Angle of the tick labels
        title_text='Date'       # Title of the x-axis
        )

    fig.update_layout(paper_bgcolor ="black") # make background black b/c I don't know how to get black tick labels

    st.plotly_chart(fig)

def plot_bubble_chart(data):


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
        title='Baseline vs Current Costs Over Time',
        xaxis_title='Date',
        yaxis_title='',
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
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False  # Remove the legend
    )

    st.plotly_chart(fig)

if __name__ == "__main__":
    execute_code()