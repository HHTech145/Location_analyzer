import os
import pandas as pd
from bokeh.plotting import figure, save, output_file
from bokeh.models import ColumnDataSource, HoverTool, CheckboxGroup, CustomJS, Div
from bokeh.layouts import column, row


class PredictionsPlotter:
    def __init__(self, postcode_info_path, folder_path, output_file_name):
        self.postcode_info_path = postcode_info_path
        self.folder_path = folder_path
        self.output_file_name = output_file_name
        self.all_predictions = []
        self.postcode_info_df = None
        self.combined_df = None

    def load_postcode_info(self, postcodes):
        postcode_info_df = pd.read_excel(self.postcode_info_path)
        postcode_info_df = postcode_info_df.round(3)

        # Filter based on provided postcodes
        postcode_info_df = postcode_info_df[postcode_info_df['postcode'].isin(postcodes)]
        print(postcode_info_df)
        postcode_info_df['Town'] = postcode_info_df['postcode']  # If 'Town' column does not exist, use 'postcode'
        return postcode_info_df

    def load_predictions(self):
        postcodes = []
        
        for file_name in os.listdir(self.folder_path):
            if file_name.endswith('.xlsx'):
                postcode = os.path.splitext(file_name)[0]
                postcodes.append(postcode)
                
                file_path = os.path.join(self.folder_path, file_name)
                df = pd.read_excel(file_path)
                df['Date'] = pd.to_datetime(df['Date'])
                df['Postcode'] = postcode
                self.all_predictions.append(df)

        # Now load postcode info based on collected postcodes
        self.postcode_info_df = self.load_postcode_info(postcodes)

    def process_predictions(self):
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

        print(self.combined_df[['Postcode', 'Prediction', 'Average Prediction']].describe())

    def create_plot(self):
        output_file(self.output_file_name, title="Predictions Plot", mode="inline")

        if self.combined_df.empty or self.combined_df[['Prediction', 'Average Prediction']].isnull().any().any():
            print("Error: DataFrame is empty or contains NaN values.")
            return

        p = figure(x_axis_type='datetime', width=1500, height=800,
                   title="Predictions for All Postcodes with Demographics",
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

        layout = column(checkbox, p, row(postcode_info_div_1, postcode_info_div_2))

        save(layout)


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

    def run(self):
        self.load_predictions()
        self.process_predictions()
        self.create_plot()

# # Usage
if __name__ == "__main__":
    postcode_info_path = 'free_map_tools/demographic_file/updated_outer_demog_sales_data_radius_1.xlsx'
    folder_path = 'free_map_tools/results'
    output_file_name = 'free_map_tools/predictions_plot_with_postcode_info_radius_2.html'

    plotter = PredictionsPlotter(postcode_info_path, folder_path, output_file_name)
    plotter.run()
