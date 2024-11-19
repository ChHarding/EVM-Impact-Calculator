### Developer Documentation for Interactive EVM Tool

---

## Table of Contents
1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Installation and Setup](#installation-and-setup)
4. [In-code Documentation](#in-code-documentation)
5. [User Interaction and Flow](#user-interaction-and-flow)
6. [Known Issues](#known-issues)
7. [Future Work](#future-work)
8. [Ongoing Deployment/Development](#ongoing-deploymentdevelopment)

---

## Overview
The **Interactive EVM Tool** is a web-based application built using Streamlit to analyze changes in cost profiles and item attributes and their impact on Earned Value Management (EVM) metrics. The tool enables users to upload datasets, adjust key parameters, view data visualizations, and export results as PDF reports. 

This documentation provides a comprehensive guide for developers to understand the project structure, codebase, and development workflow.

---

## Project Structure

The project follows a modular structure to separate functionality and maintain code readability:

```
InteractiveEVMTool/
│
├── docs/
│   ├── User_Guide.md
│   ├── Developer_Documentation.md
│   ├── Project_Specification.pdf
│   ├── Project_Specification.docx
│
├── sample_data/
│   ├── AttributesData.csv
│   ├── InitialUploadData.csv
│
├── main.py
├── README.md
└── LICENSE
```

- **`docs/`**: Contains user and developer documentation.
- **`sample_data/`**: sample datasets to run the application.
- **`main.py`**: Entry point of the application.
- **`README.md`**: Provides an overview and instructions for users.
- **`LICENSE`**: Contains the license information for the project.

---

## Installation and Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/InteractiveEVMTool.git
   cd InteractiveEVMTool
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python src/main.py
   ```

---
### In-code Documentation

The **Interactive EVM Tool** has a modular codebase with well-defined functions to handle data processing, visualization, and user interactions. This section provides an overview of all the functions in the code, categorized by their purpose, along with their descriptions.

---

#### **Navigation and Session State Management**

These functions manage the navigation between different screens of the app and initialize session state variables.

1. **`main()`**
   - **Purpose:** The entry point of the application. Routes the user to the appropriate page based on the current session state.
   - **Key Logic:**
     - Routes to `show_initial_screen`, `upload_attr_data_page`, or `show_chart_screen`.

2. **`navigate_to_upload_screen_1()`**
   - **Purpose:** Sets the session state to navigate to the initial screen for uploading cost data.
   - **Usage:** Called when the user clicks the "Back" or "Start Over" button.

3. **`navigate_to_upload_screen_2()`**
   - **Purpose:** Sets the session state to navigate to the screen for uploading attribute data.
   - **Usage:** Triggered when the user clicks "Next" after uploading valid cost data.

4. **`navigate_to_chart_screen()`**
   - **Purpose:** Sets the session state to navigate to the chart visualization screen.
   - **Usage:** Triggered when the user clicks "Next" after uploading valid attribute data.

---

#### **Screen Display Functions**

These functions define the content and layout of the different app screens.

1. **`show_initial_screen()`**
   - **Purpose:** Displays the initial screen where the user uploads the cost data file.
   - **Key Features:**
     - Validates uploaded file for required columns: `Date`, `Cost`, `Item Number`, `Type`.
     - Previews data in a table if valid.
     - Stores the cost data in session state for later use.

2. **`upload_attr_data_page()`**
   - **Purpose:** Displays the screen for uploading attribute data.
   - **Key Features:**
     - Validates uploaded file for required columns: `Item Number`, `Cost`, `Lead Time`, `Yield`, `Hours`.
     - Previews data in a table if valid.
     - Stores the attribute data in session state for later use.

3. **`show_chart_screen()`**
   - **Purpose:** Displays the final screen with sliders and visualizations.
   - **Key Features:**
     - Provides sliders to adjust `Cost`, `Lead Time`, `Yield`, and `Hours`.
     - Updates visualizations dynamically based on slider inputs.
     - Includes an "Export and Download PDF" button.

---

#### **Data Validation and Processing Functions**

These functions handle data validation, filtering, and transformation.

1. **`validate_columns_exist(expected_columns, df)`**
   - **Purpose:** Checks if the required columns exist in the uploaded dataset.
   - **Inputs:**
     - `expected_columns`: A list of required column names.
     - `df`: The uploaded dataset as a pandas DataFrame.
   - **Output:** Returns `True` if all columns exist, otherwise `False`.

2. **`filter_data(df, filter_item_number)`**
   - **Purpose:** Filters a DataFrame for a specific `Item Number`.
   - **Key Features:**
     - Handles cases where the filtered dataset is empty.

3. **`assess_impacts(initial_attributes, user_attributes_dictionary)`**
   - **Purpose:** Calculates the impact of user adjustments on attributes like `Cost`, `Lead Time`, and `Yield`.
   - **Key Features:**
     - Generates a dictionary summarizing the percent change impacts.

4. **`modify_dataset(filtered_df, impacts_dic)`**
   - **Purpose:** Modifies a dataset based on the calculated impacts.
   - **Key Features:**
     - Adjusts the `Cost` column for `Labor` and `Material` types.
     - Shifts dates based on lead time impacts.

5. **`create_common_x_value_by_month(filtered_df, modified_df)`**
   - **Purpose:** Aligns two datasets by a common set of monthly dates for consistent plotting.
   - **Output:** Returns a combined DataFrame with aligned `Date`, `Initial_Costs`, and `Modified_Costs`.

6. **`calculate_evm(combined_data_set)`**
   - **Purpose:** Calculates EVM metrics like Planned Value (PV), Earned Value (EV), Schedule Variance (SV), and Cost Variance (CV).
   - **Output:** Returns the dataset with EVM columns and a summary dictionary (`BAC` and `EAC`).

---

#### **Visualization Functions**

These functions create interactive charts for the app.

1. **`generate_charts(cost_df, attributes_df, user_attributes_dictionary, chart_type, item_number)`**
   - **Purpose:** Generates either a line chart or bubble chart based on the user's selected item and adjusted attributes.
   - **Key Features:**
     - Uses Plotly for dynamic, interactive visualizations.
     - Accepts `chart_type` as either `"line_chart"` or `"bubble_chart"`.

2. **`plot_line_chart_with_percent_delta(evm_data, evm_summary_data, data_label_1, data_label_2, chart_title)`**
   - **Purpose:** Creates a cumulative line chart displaying original and modified costs with annotations for `BAC` and `EAC`.
   - **Key Features:**
     - Includes hover tooltips for EVM metrics.

3. **`plot_bubble_chart(data)`**
   - **Purpose:** Creates a bubble chart showing cost magnitudes by month for baseline and modified data.
   - **Key Features:**
     - Bubble sizes represent cost values.

---

#### **PDF Export Function**

1. **`export_charts_to_pdf(chart1, chart2, title, settings_text)`**
   - **Purpose:** Exports the generated charts and analysis details to a PDF file.
   - **Key Features:**
     - Converts Plotly charts to images.
     - Uses `reportlab` for creating a professional PDF layout.

---

### Summary of Key Interactions

| **User Action**                   | **Function(s) Involved**                                                                 |
|-----------------------------------|------------------------------------------------------------------------------------------|
| Upload cost data                  | `show_initial_screen`, `validate_columns_exist`, `st.file_uploader`                      |
| Upload attribute data             | `upload_attr_data_page`, `validate_columns_exist`, `st.file_uploader`                    |
| Adjust sliders and view charts    | `show_chart_screen`, `generate_charts`, `plot_line_chart_with_percent_delta`, `plot_bubble_chart` |
| Visualizations                    | `export_charts_to_pdf`, `generate_charts`, `calculate_evm`                               |


---

## Known Issues

### Minor Issues
- **Slider Ranges:** Default slider ranges may not always align with extreme dataset values.
- **Error Handling:** User feedback could be improved for uncommon errors during file upload or processing.

### Major Issues
- **Dataset Compatibility:** The app currently assumes datasets follow specific column formats and does not provide schema auto-correction.

---

## Future Work

### Enhancements
- Add schema detection and column mapping for greater flexibility with user datasets.
- Enhance UI/UX with additional styling and customization options.

### New Features
- Add support for saving and loading user sessions.
- Enable batch processing of multiple datasets for comparative analysis.
- Allow impacts to multiple items to be combined in an output


---

## Ongoing Deployment/Development

- **Code Reviews:** Regularly review contributions to maintain code quality.
- **Documentation Updates:** Keep the documentation current with any new features.

---
