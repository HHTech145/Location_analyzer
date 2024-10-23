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

    def create_plot(self,demographics_df,restaurants_df,pubs_df,df_household_income,df_neighbourhood_income,full_address,df_occcupation,occupation_location_text):
        print("in plot ______________________________________________________")
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


        # self.postcode_info_df()
        self.postcode_info_df[['unemployment_rate','working','unemployed','ab','c1/c2','de', 'white', 'non-white']] = self.postcode_info_df[['unemployment_rate','working','unemployed','ab','c1/c2','de', 'white', 'non-white']].apply(lambda x: (x * 100).round(2))

        demographics = self.postcode_info_df.columns.tolist()
        values = self.postcode_info_df.iloc[0].tolist()

        # Create a new DataFrame for the converted format with string keys
        converted_df = pd.DataFrame({
            'Demographics': demographics,
            'Values': values
        })
        # print(self.postcode_info_df)

        postcode_info_source = ColumnDataSource(converted_df)


        postcode_info_columns = [
            TableColumn(field="Demographics", title="Demographics"),
            TableColumn(field="Values", title="Values")
        ]
        postcode_info_table = DataTable(source=postcode_info_source, columns=postcode_info_columns, width=800, height=500)

        ###############################################
        last_row = df_neighbourhood_income.iloc[-1]
        df_neighbourhood_income = df_neighbourhood_income.drop(df_neighbourhood_income.index[-1])


        # Converting the data to ColumnDataSources
        demographics_source = ColumnDataSource(demographics_df)
        restaurants_source = ColumnDataSource(restaurants_df)
        pubs_source = ColumnDataSource(pubs_df)
        income_source= ColumnDataSource(df_neighbourhood_income)
        occupation_source= ColumnDataSource(df_occcupation)

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


        # Defining columns for Affluence Table 
        income_columns = [
            TableColumn(field="Area", title="Area"),
            TableColumn(field="Income", title="Income")
        ]
        income_table = DataTable(source=income_source, columns=income_columns, width=800, height=150)

        # Defining columns for Occupation Table 
        occupation_columns = [
            TableColumn(field="Occupation", title="Occupation"),
            TableColumn(field="Percentage", title="Percentage")
        ]
        occupation_table = DataTable(source=occupation_source, columns=occupation_columns, width=800, height=400)        

        # last_row = df_neighbourhood_income.iloc[-1]
        # df_neighbourhood_income = df_neighbourhood_income.drop(df_neighbourhood_income.index[-1])
        print("_________________________________in plot _______________________________________________________________",df_household_income,df_neighbourhood_income,df_neighbourhood_income.columns,"))))",income_table)

    # Create headers for the tables
        plot_header=Div(text=f"<h1>{full_address}</h1>", width=800)
        postcode_info_header=Div(text="<h3>Postcode area Demographics</h3>", width=800)
        demographics_header = Div(text="<h3>Ethnicity,Religion,Households</h3>", width=800)
        restaurants_header = Div(text="<h3>Restaurants Near Postcode</h3>", width=800)
        pubs_header = Div(text="<h3>Bars, pubs, clubs</h3>", width=800)
        # HTML and CSS for the Div
        income_header = Div(
            text=f"""
            <h1>Income Section</h1>
            <div style="border: 1px solid #ccc; border-radius: 8px; padding: 15px; background-color: orange; color: black;"> 
                <p style="margin: 0; font-weight: bold;">Mean household income estimate before tax</p>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
                    <p style="margin: 0; font-size: 24px; font-weight: bold;">{df_household_income['income'][0]}</p>
                    <span style="font-size: 24px; font-weight: bold;">{df_household_income['rating'][0]}</span>
                </div>
                <p style="margin-top: 15px;font-size:15px;">{last_row['Income']}</p>
            </div>
            """,
            width=800
        )
        occupation_header=Div(
            
            text=f"""
            <h1>Occupation section</h1>
            <div style="border: 1px solid #ccc; border-radius: 6px; padding: 15px; background-color: Crimson; color: black;"> 
                <p style="margin: 0; font-weight: bold;">Occupation</p>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
                    <p style="margin: 0; font-size: 16px; font-weight: bold;">{occupation_location_text}</p>
                </div>
            </div>
            """,
            width=800
            
            )

        # income_header= Div(text=f"<h3>Income section </h3><h2>Testing in progress</h2><h2>Mean Household Income {df_household_income['income'][0]}</h2><p style='font-size:41px;color:red;'>Rating {df_household_income['rating'][0]}</p><h2 style='font-size:20px;color:green;'>{last_row['Income']}</h2>", width=800)
        # income_footer = Div(text=f"<h3>{last_row['Income']}</h3>", width=800)

        # print("__in plot ",last_row,income_footer)
        # Split the string by commas
        # Split the string by commas
        parts = [part.strip() for part in full_address.split(',')]

        # Further split the postal code
        postal_code_parts = parts[5].split()
        postcode_part=postal_code_parts[0]+"+"+postal_code_parts[1]

        # Rearrange the parts
        new_address = f"{parts[4]}+{parts[3]}+{postcode_part}+,+{parts[0]}"
        print("________________________________",new_address)

    # Use the public URL for Google Maps (without API key)
        # google_maps_url = "https://www.google.com/maps/place/High+St,+Southall+UB1+3DA,+UK/@51.5109211,-0.3772825,17z/data=!3m1!4b1!4m6!3m5!1s0x48760d54eef03057:0x68d5d16d4d902882!8m2!3d51.5109469!4d-0.3747371!16s%2Fg%2F1tf9mqyj?entry=ttu&g_ep=EgoyMDI0MTAxNi4wIKXMDSoASAFQAw%3D%3D"
        # url="https://maps.google.com/maps?q=chennai&t=&z=13&ie=UTF8&iwloc=&output=embed"
        # Google Maps iframe without API key
        google_maps_header=Div(text=f"<h2>Google Maps Section</h2>", width=300,height=100)
        google_maps_div = Div(
            text=f"""
                <div class="mapouter"><div class="gmap_canvas"><iframe width="1200" height="800" id="gmap_canvas" src="https://maps.google.com/maps?q={new_address}&t=&z=17&ie=UTF8&iwloc=&output=embed" frameborder="0" scrolling="no" marginheight="0" marginwidth="0"></iframe></div></div>
            """, 
            width=1000, height=800
        )


        layout = column(
            plot_header,
            checkbox, 
            p,
            row(), 
            postcode_info_header,postcode_info_table, # postcode section 
            demographics_header, demographics_table, # demographics section
            restaurants_header, restaurants_table, # restraunts section 
            pubs_header, pubs_table, # pubs section 
            income_header,income_table, # income section 
            occupation_header,occupation_table,
            google_maps_header,google_maps_div,  # Google Maps iframe without API key
        )
        save(layout)
        # show(layout)

    # def add_google_maps(self):
    #     <div style="overflow:hidden;max-width:100%;width:500px;height:500px;"><div id="google-maps-display" style="height:100%; width:100%;max-width:100%;"><iframe style="height:100%;width:100%;border:0;" frameborder="0" src="https://www.google.com/maps/embed/v1/place?q=UB1+3DA&key=AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU17R8"></iframe></div><a class="googl-ehtml" rel="nofollow" href="https://www.bootstrapskins.com/themes" id="grab-map-data">premium bootstrap themes</a><style>#google-maps-display img{max-width:none!important;background:none!important;font-size: inherit;font-weight:inherit;}</style></div>


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
    
    def run(self,demo_df,df_restaurants,df_pubs,df_household_income,df_neighbourhood_income,full_address,df_occcupation,occupation_location_text,postcode):
        self.load_predictions(postcode)
        self.process_predictions(postcode)
        self.create_plot(demo_df,df_restaurants,df_pubs,df_household_income,df_neighbourhood_income,full_address,df_occcupation,occupation_location_text,)

# # Usage
if __name__ == "__main__":
    postcode_info_path = 'demographic_file/updated_outer_demog_sales_data_radius_1.xlsx'
    folder_path = 'results'
    # output_file_name = 'predictions_plot_with_postcode_info_radius_2.html'

    # plotter = PredictionsPlotter(postcode_info_path, folder_path, output_file_name)
    # plotter.run()
