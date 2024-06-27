import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

"""
This library processes the 'system.csv' file coming from
the resource consumption monitoring script. 
It produces plots and files with readable informations.
The main class, Report, expects a folder as input 
where it searches for 'system.csv' and places the output artifacts
"""

class Report:
    def __init__(self, data_path='.', CPU_THRESHOLD=0, RAM_BASE=0):
        # `CPU_THRESHOLD` and `RAM_BASE` are float cutoff values used 
        # to exclude the baseline system consumption from the calculations.

        # Save the data path and thresholds into the object's attributes.
        self.data_path = data_path
        self.CPU_THRESHOLD = CPU_THRESHOLD
        self.RAM_BASE = RAM_BASE
        
        # Create a pandas DataFrame with the data from 'system.csv'.
        self.csv = pd.read_csv(data_path+'/system.csv', sep=";")

        # Initialize dictionaries to store CPU and GPU informations after processing.
        self.CPU = {}
        self.GPU = {}

        # Preprocess and normalize data as part of the initialization process.
        self.preprocess_gpu()
        self.preprocess()
        self.normalize()

    def preprocess_gpu(self):

        csv = self.csv

        # Extract the GPU-specific header, the last column, containing JSON string about GPU usage.
        header = csv.columns[-1]
        self.GPU_header = header

        # Initialize the GPUS dictionary with parsed header data
        self.GPUS = json.loads(self.GPU_header.replace("GPUs: ", "").replace("'", '"'))  

        # Initialize GPU dictionary with the number of GPUs and a placeholder for total GPU RAM.
        self.GPU = {} 
        self.GPU["number"] = len(self.GPUS) 
        self.GPU["RAM_TOTAL"] = 0
 
        # Convert GPU column element from a JSON string to a dictionary 
        csv[self.GPU_header] = csv[self.GPU_header].apply(lambda x : json.loads(x.replace("'", '"')) )
        
        #give a name to every GPU and create colums "gproc-i", "gtemp-i" and "gmem-i" for every gpu 
        gproc = []
        gmem = []
        for i in range(self.GPU["number"]):
            gproc.append('gproc-'+str(i))
            gmem.append('gmem-'+str(i))
            csv['gtemp-'+str(i)]=csv[self.GPU_header].apply(lambda x: x[i]['temp'])
            csv['gproc-'+str(i)]=csv[self.GPU_header].apply(lambda x: float(x[i]['cpu_usage'][:-1]))
            csv['gmem-'+str(i)]=csv[self.GPU_header].apply(lambda x: float(x[i]['mem_used'])/1024)

            # Record extremal values for core usage and RAM usage for each GPU.
            self.GPUS[i]['CORES_MAX_USAGE'] = csv['gproc-'+str(i)].max()
            self.GPUS[i]['MIN_RAM_USAGE'] = csv['gmem-'+str(i)].min()
            self.GPUS[i]['MAX_RAM_USAGE'] = csv['gmem-'+str(i)].max()

            # Accumulate total RAM usage from all GPUs.
            self.GPU["RAM_TOTAL"] += float(self.GPUS[i]["mem_total"][:-2]) / 1024

        # mean GPU Cores and RAM consumption values
        csv['GPU Core %'] = csv[gproc].mean(axis=1)
        csv['GPU RAM'] = csv[gmem].sum(axis=1)  

        # record extremal values in the GPU dictionary
        self.GPU["CORES_MAX_USAGE"]= csv['GPU Core %'].max()
        self.GPU["MIN_RAM_USAGE"]= csv['GPU RAM'].min()
        self.GPU["MAX_RAM_USAGE"]= csv['GPU RAM'].max()


    def preprocess(self):
        csv = self.csv

        # Record the maximum CPU usage percentage from the data.
        self.CPU["MAX_USAGE"]=csv['CPU usage %'].max()

        # Convert JSON strings in 'Cores usage %' to numpy arrays 
        # and calculate the number of cores, the average cores usage
        csv['Cores usage %'] = csv['Cores usage %'].apply(json.loads).apply(np.array)
        self.CPU["CORES"]=len(csv['Cores usage %'][0])
        csv['Cores %'] = csv['Cores usage %'].apply(np.mean)

        # Count the number of cores exceeding the CPU threshold for each row.
        csv['Cores N.'] = csv['Cores usage %'].apply(lambda x : np.sum(x > self.CPU_THRESHOLD))

        # Extract the total RAM from the first row, assume units are in GB
        # (splitting the string to get the numeric part).
        self.CPU['RAM_TOTAL']=float(csv['RAM total'][0].split(' ')[1])

        # Calculate actual RAM usage in GB based on the percentage usage and total RAM.
        csv['RAM']=csv['RAM usage %']*(self.CPU["RAM_TOTAL"]/100)

        #record the extremal values
        self.CPU["MIN_RAM_USAGE"] = csv['RAM'].min()
        self.CPU["MAX_RAM_USAGE"] = csv['RAM'].max()

        # Set the baseline RAM usage,
        self.RAM_GROUND = min(self.RAM_BASE, self.CPU["MIN_RAM_USAGE"])

        # Find the maximum count of cores used that exceed the CPU threshold.
        self.CPU["MAX_CORES_USED"] = csv['Cores N.'].max()

        # Track changes in the 'Modulo' column to detect sequential changes, 
        # which can be used for session or event segmentation.
        csv['Control']=csv['Modulo'].ne(csv['Modulo'].shift()).cumsum()
 

    def normalize(self):
        # Create a DataFrame with normalized data to facilitate comparison 
        # across different data types, such as RAM usage and cores usage.

        csv = self.csv
        norm = pd.DataFrame()

        norm['CPU']= csv['CPU usage %']/100
        norm['Cores'] = csv['Cores N.']/self.CPU["MAX_CORES_USED"]
        norm['RAM'] = (csv['RAM']-self.RAM_GROUND)/(self.CPU["RAM_TOTAL"]-self.RAM_GROUND)

        norm['GPU'] = csv['GPU Core %']/100
        norm['gRAM'] = csv['GPU RAM']/self.GPU["RAM_TOTAL"]

        norm['Modulo'] = csv['Modulo']
        norm['Control'] = csv['Control']

        self.norm = norm


    def interval(self, df):
        # Calculate the time interval between the first and last entries of the DataFrame.
        return df.iloc[-1]['Time']-df.iloc[0]['Time']

    @property
    def scores(self):
        # resource exploitation indicator 
        # from normalized data

        # drop the 'Control' column
        norm = self.norm.drop('Control', axis=1)

        # calculate group-wise averages by 'Modulo'.
        s = norm.groupby('Modulo').mean()

        # Add a 'Total' row that calculates the mean across all data
        s.loc['Total'] = norm.drop('Modulo', axis=1).mean()
        
        # Calculate the mean of all resource usage scores as a resource exploitation indicator.
        s['Mean']=s.mean(axis=1)

        # Evaluate the time intervals
        s['Interval (seconds)']=self.csv.groupby('Modulo').apply(self.interval)
        # Total is not the sum of individual intervals
        s.loc['Total','Interval (seconds)'] = self.interval(self.csv)

        return s
    

    def export(self):
        #  Convert and export system monitoring data to JSON and Excel formats.

        def convert(data):
            ogg = {}
            for p in data:
                if p not in ['id','model', 'mem_total']:
                    ogg[p]=float(data[p])
                else:
                    ogg[p]=data[p]
            return ogg
        
        j = {
            "CPU":convert(self.CPU),
            "GPU":convert(self.GPU),
            "GPUS": [convert(x) for x in self.GPUS]
        }

        # Write the dictionary data to the JSON file
        with open(self.data_path+'/data.json', "w") as json_file:
            json.dump(j, json_file, indent=4)

        self.scores.to_excel(self.data_path+'/scores.xlsx')
        
    
# plots

    def add_colored_background(self, ax, df):
        # fix the comments

        colors = {1: 'white', 2: "#EFEFEF"}  # Mappa i colori alternati
        current_color = df['Control'][0]  # Start with the initial color based on the first entry
        start_change = df.index[0]  # Index where the first segment starts
        modulo_value = df['Modulo'][0]  # Get initial "Modulo" value for the first segment
        
        # Define how much lower to place the annotations
        vertical_offset = -0.02 * (ax.get_ylim()[1] - ax.get_ylim()[0])  # Negative to move downward, adjust the factor as needed

        for idx in range(1, len(df)):
            if df['Control'][idx] != current_color:
                end_change = df.index[idx]
                # Place the annotation for the previous segment
                midpoint = (start_change + end_change) / 2
                ax.text(midpoint, ax.get_ylim()[0]+vertical_offset, str(modulo_value), verticalalignment='top', horizontalalignment='left', rotation=90)
                ax.axvspan(start_change, end_change, facecolor=colors[current_color % 2 + 1], alpha=1)
                # Update for new segment
                start_change = df.index[idx]
                current_color = df['Control'][idx]
                modulo_value = df['Modulo'][idx]  # Update modulo_value for the new segment
        
        # Handle the last segment, which won't necessarily trigger in the loop
        end_change = df.index[-1]
        midpoint = (start_change + end_change) / 2
        ax.text(midpoint, ax.get_ylim()[0]+ vertical_offset, str(modulo_value), verticalalignment='top', horizontalalignment='left', rotation=90)
        ax.axvspan(start_change, end_change, facecolor=colors[current_color % 2 + 1], alpha=1)

    def PLOT(self, figsize, save=True):
        """
        Plot and optionally save normalized system monitoring data for CPU, RAM, Cores, GPU, and gRAM usage.
        Accepts:
        - `figsize`: A tuple specifying the dimensions of the plot.
        - `save`: A boolean indicating whether to save the plot to disk (default is True).
        """
        csv = self.norm

        fig, ax = plt.subplots(figsize=figsize)
        
        csv['CPU'].plot(ax=ax, label='CPU', color='blue')  
        csv['RAM'].plot(ax=ax, label='RAM', linestyle='--', color='blue')
        csv['Cores'].plot(ax=ax, label='Cores', linestyle='dotted', color='blue')  
        csv['GPU'].plot(ax=ax, label='GPU', color='red' )
        csv['gRAM'].plot(ax=ax, label='gRAM',  linestyle='--', color='red' )

        self.add_colored_background(ax, csv)

        ax.legend(loc='upper left',bbox_to_anchor=(-0.03, 0.9), shadow=True, fancybox=False, title='Legend', edgecolor='black', facecolor='white')
        ax.set_xlim(csv.index[0], csv.index[-1])
        ax.set_xticklabels([])

        self.plt = plt
        self.plt.tight_layout()
        if (save):
            self.plt.savefig(self.data_path+'/plot_all.png', format='png')  # Adjust the filename, format, and DPI as needed
    
    def GPU_PLOT(self, figsize, save=True):
        """
        Plot and optionally save GPU-related data, specifically memory usage for individual GPUs.
        Accepts:
        - `figsize`: A tuple specifying the dimensions of the plot.
        - `save`: A boolean indicating whether to save the plot to disk (default is True).
        """
        csv = self.csv

        fig, ax = plt.subplots(figsize=figsize)
        
        #csv['GPU Core %'].plot(ax=ax, label='Cores Aggr', color='yellow')  
        csv['GPU RAM'].plot(ax=ax, label='Sum', linestyle='--', color='green')
        #csv['gproc-0'].plot(ax=ax, label='gpu 0', color='red' )
        csv['gmem-0'].plot(ax=ax, label='gpu 0',  linestyle='--', color='red' )        
        #csv['gproc-1'].plot(ax=ax, label='gpu 1, color='blue' )
        csv['gmem-1'].plot(ax=ax, label='gpu 1',  linestyle='--', color='blue' )

        self.add_colored_background(ax, csv)

        ax.legend(loc='upper left',bbox_to_anchor=(-0.03, 0.9), shadow=True, fancybox=False, title='GPUs Mem (GB)', edgecolor='black', facecolor='white')
        ax.set_xlim(csv.index[0], csv.index[-1])
        ax.set_xticklabels([])

        self.plt = plt
        self.plt.tight_layout()
        if (save):
            self.plt.savefig(self.data_path+'/plot_gpu.png', format='png')  # Adjust the filename, format, and DPI as needed
       
    # def show(self):
    #     self.plt.tight_layout()
    #     self.plt.show()

    # def save(self,filename):
    #     assert isinstance(filename, str)
    #     # Save the plot to a file
    #     self.plt.tight_layout()
    #     self.plt.savefig(filename, format='png')  # Adjust the filename, format, and DPI as needed


