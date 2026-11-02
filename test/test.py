import math
from parser import *

class test:
    
    def __init__(self):
        self.ROI_x_max = 2.68
        self.ROI_y_max = -2.645
        self.ROI_y_min = -5.08
        self.ROI_x_min = 2.057
        self.debugging_data = True
        self.clustering_distance = 0.6
        self.ROI_doppler = -0.6
        self.v6 = []
        self.v7 = []
        self.v8 = []
        self.raw_data = []
        self.xyz = []
        self.x = 0
        self.y = 0
        self.z = 0
        self.global_counter =0
        self.elevation = 0
        self.azimuth =0
        self. Mrange =0
        self.dck = False
        self.samples = 0
        self.samples_thresh = 19
    

    def load_data_csv(self,data_file):
        data = pd.read_csv(data_file,delimiter=',',on_bad_lines='skip')
        data = pd.read_csv(data_file,converters={"cloud_points": lambda x: x.strip("[]").split(", ")},on_bad_lines='skip')
        return data

    def readUartData(self):
        uartParser = uartParser()
        uartParser.connectComPorts(self, '/dev/ttyUSB0', '/dev/ttyUSB1')
        while True:
            data = uartParser.readAndParseUart()
            print(data)

    def process_data_csv(self, data_frame):
        
        data_frame = data_frame.reset_index()
        angle = 90
        # number of rows
        if self.debugging_data:
            print('Number of rows: ',len(data_frame))

        for index, data in data_frame.iterrows():

            self.raw_data.append(ast.literal_eval(data[2])) # convert str list into list


            for i in range (len(self.raw_data[-1])):
                #extract the v6 elements
                self.elevation = self.raw_data[-1][i][0] # evevation
                self.azimuth   = self.raw_data[-1][i][1] # azimuth
                self.doppler   = self.raw_data[-1][i][2] # doppler
                self.Mrange    = self.raw_data[-1][i][3] # range
                

   
                self.z = self.Mrange * math.sin(self.elevation)  
                self.x = self.Mrange * math.cos(self.elevation) * math.sin(self.azimuth)
                self.y = self.Mrange * math.cos(self.elevation) * math.cos(self.azimuth)
                

                if ((0.58*self.x)+2.22)<self.y<((0.58*self.x)+2.52)\
                    and self.doppler<=-0.6:
                    self.xyz.append([self.x,self.y,self.z])

            self.samples += 1 # increse the samples counter by 1 
            #if self.debugging_data:
                #print('xyz length',len(self.xyz))
                #print('sample: ', self.samples)   

            if (self.samples >= self.samples_thresh) or ((index == len(data_frame)-1) and (self.samples < self.samples_thresh)):
                try:
                    new_xyz = [x for x in self.xyz if len(x)>=3]
                    APPLICATION = ProcessPointCloud(pcd_file=new_xyz ,nrows_value=len(self.xyz) , display_output_flag=False)
                    cluster_centers, clustering_count, labels = APPLICATION.meanshift_clustring(xyz=new_xyz,distance_threshold = self.clustering_distance)
                    #cluster_centers, clustering_count, labels = APPLICATION.euclidean_clustering(xyz=self.xyz,distance_threshold = self.clustering_distance)
                    #clustering_count = APPLICATION.euclidean_clustering(distance_threshold = self.clustering_distance, cluster_parameters={"min_size":0})
                    
                    if self.debugging_data:
                        print('Prediction: ',(clustering_count)) # for debug only

                    self.global_counter+=(clustering_count)
                    print('Total: ',self.global_counter)

                except: 
                    # no input
                    clustering_count = 0

                self.xyz.clear()

                self.raw_data.clear()


                self.samples = 0

        print('Total: ',self.global_counter)


test = test()
test.readUartData()
