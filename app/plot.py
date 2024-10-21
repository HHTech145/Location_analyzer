import os
import pandas as pd
from bokeh.plotting import figure, save, output_file, show
from bokeh.models import ColumnDataSource, HoverTool, CheckboxGroup, CustomJS, Div, DataTable, TableColumn
from bokeh.layouts import column, row
from bokeh.plotting import curdoc

class PredictionsPlotter:
    def __init__(self, postcode_info_path, folder_path, output_file_name):
        self.postcode_info_path = postcode_info_path
        self.folder_path = folder_path
        self.output_file_name = output_file_name
        self.all_predictions = []
        self.postcode_info_df = None
        self.combined_df = None

    def load_postcode_info(self, postcodes,postcode):
        postcode_info_df = pd.read_excel(self.postcode_info_path)
        postcode_info_df = postcode_info_df.round(3)
        # limit to only one p   ostcode 
        print("_________________________________",postcode)

        postcode_info_df=postcode_info_df[postcode_info_df['postcode']==postcode]

        # Filter based on provided postcodes
        postcode_info_df = postcode_info_df[postcode_info_df['postcode'].isin(postcodes)]
        print(postcode_info_df)
        postcode_info_df['Town'] = postcode_info_df['postcode']  # If 'Town' column does not exist, use 'postcode'
        print("############################################",postcode_info_df)
        return postcode_info_df

    def load_predictions(self,postcode):
        postcode_0=postcode
        print("________________________________________________________________ load predictions",postcode)
        postcodes = []
        
        for file_name in os.listdir(self.folder_path):
            if file_name.endswith('.xlsx'):
                if file_name==f"{postcode}.xlsx":
                    postcode = os.path.splitext(file_name)[0]
                    postcodes.append(postcode)
                    
                    file_path = os.path.join(self.folder_path, file_name)
                    df = pd.read_excel(file_path)
                    df['Date'] = pd.to_datetime(df['Date'])
                    df['Postcode'] = postcode
                    self.all_predictions.append(df)

        # Now load postcode info based on collected postcodes
        print("________________________________________________________________ load predictions",postcode)
        self.postcode_info_df = self.load_postcode_info(postcodes,postcode_0)

    def process_predictions(self,postcode):
        if not self.all_predictions:
            print("No prediction data available.")
            return

        self.combined_df = pd.concat(self.all_predictions)
        print(f"Combined data has {len(self.combined_df)} records.")

        self.combined_df.replace([float('inf'), float('-inf')], pd.NA, inplace=True)
        
        if 'Prediction' in self.combined_df:
            self.combined_df['Prediction'].fillna(self.combined_df['Prediction'].mean(), inplace=True)

        postcode_averages = self.combined_df.groupby('Postcode')['Prediction'].mean().reset_index()
        postcode_averages.columns = ['Postcode', 'Average Prediction']
        
        self.combined_df = self.combined_df.merge(postcode_averages, on='Postcode', how='left')
        self.combined_df['Average Prediction'].fillna(0, inplace=True)

        self.combined_df=self.combined_df[self.combined_df['Postcode']==postcode]
        print(self.combined_df[['Postcode', 'Prediction', 'Average Prediction']].describe())

    def create_plot(self,demographics_df,restaurants_df,pubs_df):
        output_file(self.output_file_name, title="Predictions Plot", mode="inline")
        
        if self.combined_df.empty or self.combined_df[['Prediction', 'Average Prediction']].isnull().any().any():
            print("Error: DataFrame is empty or contains NaN values.")
            return

        p = figure(x_axis_type='datetime', width=1500, height=800,
                   title="Predictions of Postcode with Demographics",
                   x_axis_label='Date', y_axis_label='Prediction')

        unique_postcodes = self.combined_df['Postcode'].unique()
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                  '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

        lines = []
        for i, postcode in enumerate(unique_postcodes):
            postcode_data = self.combined_df[self.combined_df['Postcode'] == postcode]
            source = ColumnDataSource(postcode_data)

            if postcode_data[['Prediction', 'Average Prediction']].isnull().any().any():
                print(f"Warning: Data for postcode {postcode} contains NaN values.")
                continue

            line = p.line(x='Date', y='Prediction', source=source, line_width=2,
                          color=colors[i % len(colors)], legend_label=postcode)
            self.add_hover_tool(p, source)
            lines.append(line)

        checkbox = CheckboxGroup(labels=list(unique_postcodes), active=list(range(len(unique_postcodes))))
        postcode_info_div_1 = Div(text="", width=600, css_classes=["postcode-info"])
        postcode_info_div_2 = Div(text="", width=600, css_classes=["postcode-info"])

        self.add_interactivity(p, unique_postcodes, lines, checkbox, postcode_info_div_1, postcode_info_div_2)

        # layout = column(checkbox, p, row(postcode_info_div_1, postcode_info_div_2),)

        #add crystal 
        # postcode_df=self.postcode_info_df.transpose(T)

        # Convert columns to rows
        # Convert columns to rows
        demographics = self.postcode_info_df.columns.tolist()
        values = self.postcode_info_df.iloc[0].tolist()

        # Create a new DataFrame for the converted format with string keys
        converted_df = pd.DataFrame({
            'Demographics': demographics,
            'Values': values
        })
        # print(self.postcode_info_df)
    
        # Create a new DataFrame for the converted format
        # converted_df = pd.DataFrame([demographics, values], index=['Demographics', 'Values'])


        postcode_info_source = ColumnDataSource(converted_df)


        postcode_info_columns = [
            TableColumn(field="Demographics", title="Demographics"),
            TableColumn(field="Values", title="Values")
        ]
        postcode_info_table = DataTable(source=postcode_info_source, columns=postcode_info_columns, width=800, height=500)

        ###############################################

        # Converting the data to ColumnDataSources
        demographics_source = ColumnDataSource(demographics_df)
        restaurants_source = ColumnDataSource(restaurants_df)
        pubs_source = ColumnDataSource(pubs_df)

        # Defining columns for the Demographics table
        demographics_columns = [
            TableColumn(field="Demographics", title="Demographics"),
            TableColumn(field="Percentage", title="Percentage")
        ]
        demographics_table = DataTable(source=demographics_source, columns=demographics_columns, width=800, height=500)

        # Defining columns for the Restaurants table
        restaurants_columns = [
            TableColumn(field="Restaurant", title="Restaurant"),
            TableColumn(field="Distance", title="Distance")
        ]
        restaurants_table = DataTable(source=restaurants_source, columns=restaurants_columns, width=800, height=500)

        # Defining columns for the Pubs table
        pubs_columns = [
            TableColumn(field="Pub", title="Pub"),
            TableColumn(field="Distance", title="Distance")
        ]
        pubs_table = DataTable(source=pubs_source, columns=pubs_columns, width=800, height=600)

    # Create headers for the tables
        postcode_info_header=Div(text="<h3>Postcode area Demographics</h3>", width=800)
        demographics_header = Div(text="<h3>Ethnicity,Religion,Households</h3>", width=800)
        restaurants_header = Div(text="<h3>Restaurants Near Postcode</h3>", width=800)
        pubs_header = Div(text="<h3>Bars, pubs, clubs</h3>", width=800)


        layout = column(
            checkbox, 
            p,
            row(), 
            postcode_info_header,postcode_info_table,
            demographics_header, demographics_table,
            restaurants_header, restaurants_table,
            pubs_header, pubs_table
        )

        # Organize the layout with headers above each table
        # layout = column(
        #     checkbox, 
        #     p, 
        #     row(postcode_info_div_1, postcode_info_div_2),
        #     demographics_header, demographics_table,
        #     restaurants_header, restaurants_table,
        #     pubs_header, pubs_table
        # )

        # layout = column(checkbox, p, row(postcode_info_div_1, postcode_info_div_2),demographics_table,restaurants_table,pubs_table)

        save(layout)
        # show(layout)

    def add_hover_tool(self, p, source):
        hover = HoverTool(
            tooltips=[
                ("Date", "@Date{%F}"),
                ("Prediction", "@Prediction{0.000}"),
                ("Average Prediction", "@{Average Prediction}{0.000}")
            ],
            formatters={'@Date': 'datetime'},
            mode='vline'
        )
        p.add_tools(hover)

    def add_interactivity(self, p, unique_postcodes, lines, checkbox, div1, div2):
        # Convert postcode_info_df to a JSON-serializable dictionary
        # postcode_info_dict = self.postcode_info_df
        postcode_info_dict = self.postcode_info_df.set_index('postcode').T.to_dict()
        # Convert to a dictionary with a structure that can be easily accessed in JS
        postcode_info_json = {k: v for k, v in postcode_info_dict.items()}
        
        # Create the callback with the JSON serializable object
        callback = CustomJS(args=dict(lines=lines, checkbox=checkbox, div1=div1,
                                    div2=div2, postcode_info=postcode_info_json,
                                    postcodes=unique_postcodes.tolist()), 
                            code=self.get_js_callback_code())
        checkbox.js_on_change('active', callback)

    def get_js_callback_code(self):
        return """
            for (let i = 0; i < lines.length; i++) {
                lines[i].visible = checkbox.active.includes(i);
            }

            if (checkbox.active.length == 1) {
                const postcode = postcodes[checkbox.active[0]];
                const info = postcode_info[postcode];

                const tableCSS = `
                    <style>
                        table { border-collapse: collapse; width: 100%; }
                        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
                        th { background-color: #f2f2f2; }
                        tr:hover { background-color: #f5f5f5; }
                    </style>
                `;

                if (info) {
                    let info_html_1 = "<h3>Postcode Information (Part 1)</h3>" + tableCSS + "<table><tr><th>Key</th><th>Value</th></tr>";
                    let info_html_2 = "<h3>Postcode Information (Part 2)</h3>" + tableCSS + "<table><tr><th>Key</th><th>Value</th></tr>";
                    let count = 0;

                    for (const key in info) {
                        if (info.hasOwnProperty(key)) {
                            if (count < 25) {
                                info_html_1 += `<tr><td>${key}</td><td>${info[key]}</td></tr>`;
                            } else {
                                info_html_2 += `<tr><td>${key}</td><td>${info[key]}</td></tr>`;
                            }
                            count++;
                        }
                    }

                    info_html_1 += "</table>";
                    info_html_2 += "</table>";

                    div1.text = info_html_1;
                    div2.text = info_html_2;
                } else {
                    div1.text = "<p>No data available for this postcode.</p>";
                    div2.text = "<p>No data available for this postcode.</p>";
                }
            } else {
                div1.text = "<p>Select a single postcode to see its information.</p>";
                div2.text = "<p></p>";
            }
        """  # Add your JavaScript callback code here

    def create_plot_for_crystal(self,demographics_df,restaurants_df,pubs_df):
        bootstrap_css = """
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f8f9fa;
                margin: 0;
                padding: 20px;
            }
            .bk-root {
                max-width: 1200px;
                margin: 0 auto;
            }
            .bk-root .bk-figure {
                background-color: #ffffff;
                border: 1px solid #dddddd;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
                padding: 20px;
                margin-bottom: 20px;
            }
            .table-container {
                margin-top: 20px;
                border: 1px solid #cccccc;
                padding: 10px;
                background-color: #ffffff;
                border-radius: 8px;
                margin-bottom: 20px;
            }
            .table-title {
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
                color: #333333;
            }
        </style>
        """      
        # Converting the data to ColumnDataSources
        demographics_source = ColumnDataSource(demographics_df)
        restaurants_source = ColumnDataSource(restaurants_df)
        pubs_source = ColumnDataSource(pubs_df)

        # Defining columns for the Demographics table
        demographics_columns = [
            TableColumn(field="Demographics", title="Demographics"),
            TableColumn(field="Percentage", title="Percentage")
        ]
        demographics_table = DataTable(source=demographics_source, columns=demographics_columns, width=400, height=280)

        # Defining columns for the Restaurants table
        restaurants_columns = [
            TableColumn(field="Restaurant", title="Restaurant"),
            TableColumn(field="Distance", title="Distance")
        ]
        restaurants_table = DataTable(source=restaurants_source, columns=restaurants_columns, width=400, height=150)

        # Defining columns for the Pubs table
        pubs_columns = [
            TableColumn(field="Pub", title="Pub"),
            TableColumn(field="Distance", title="Distance")
        ]
        pubs_table = DataTable(source=pubs_source, columns=pubs_columns, width=400, height=200)

        # Convert DataFrames to Bootstrap-styled HTML tables
        demographics_table = demographics_df.to_html(classes="table table-striped table-bordered", index=False)
        restaurants_table = restaurants_df.to_html(classes="table table-striped table-hover", index=False)
        pubs_table = pubs_df.to_html(classes="table table-striped table-dark", index=False)

        # Create Divs for each section title and data table with Bootstrap classes
        demographics_div = Div(text=f"<div class='table-container'><div class='table-title'>Demographics</div>{demographics_table}</div>")
        restaurants_div = Div(text=f"<div class='table-container'><div class='table-title'>Restaurants</div>{restaurants_table}</div>")
        pubs_div = Div(text=f"<div class='table-container'><div class='table-title'>Pubs</div>{pubs_table}</div>")

        # Adding the tables to the layout
        # layout = column(demographics_table, restaurants_table, pubs_table)

# Save the layout as an HTML file
        # save(layout, filename="tables_layout.html")

            # Wrap the layout together, including the CSS and content
        layout = column(
            Div(text=bootstrap_css), # Inline CSS at the top
            demographics_div, 
            restaurants_div, 
            pubs_div
        )
                # Output to an HTML file and display
        output_file("bootstrap_styled_prediction_plot.html")
        save(layout)
    
    def run(self,demo_df,df_restaurants,df_pubs,postcode):
        self.load_predictions(postcode)
        self.process_predictions(postcode)
        self.create_plot(demo_df,df_restaurants,df_pubs)

# # Usage
if __name__ == "__main__":
    postcode_info_path = 'demographic_file/updated_outer_demog_sales_data_radius_1.xlsx'
    folder_path = 'results'
    # output_file_name = 'predictions_plot_with_postcode_info_radius_2.html'

    # plotter = PredictionsPlotter(postcode_info_path, folder_path, output_file_name)
    # plotter.run()
