#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 22 01:30:40 2022

@author: henryisrael
"""

import pandas as pd
pd.options.mode.chained_assignment = None #SILENCE WENCH
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates



class wordleplotter():
    '''
    Does wordle plotting stuff!
    '''
    def __init__(self, pathtodata, verbose=True):
        '''
        

        Parameters
        ----------
        pathtodata : String, Path to data
        verbose : Bool, optional
            Enable print statements. The default is True.

        Raises
        ------
        TypeError
            You've not given me a string for pathtodata.
        IOError
            1- You've not given me a CSV file.
            2- You've given me an incorrectly format data table

        Returns
        -------
        None.

        '''
        #Reads in data from pathtodata
        if not isinstance(pathtodata, str):
            raise TypeError(f"Data path must be of type str, you've given me a {type(pathtodata)}")
        if pathtodata[-3:]!='csv':
            raise IOError("File should be of type .csv")
        # if not exists(pathtodata):
        #     raise IOError(f"Could not find {pathtodata}")
        self.data=pd.read_csv(pathtodata)
        
        #SO NO HEAD (throws phone on ground)
        good_head=['Person', 'Date', 'Time', 'Number of Guesses', 
                   'Correct Letters Guess 1', 'Correct Letters Guess 2', 
                   'Correct Letters Guess 3', 'Correct Letters Guess 4', 
                   'Correct Letters Guess 5', 'Correct Letters Guess 6']
        if not set(good_head).issubset(set(self.data.columns.values)):
            raise IOError(f"Columns should be : {good_head}\n, "\
                          f"instead you provided {self.data.columns.values}")

        #Speak when plotting?
        self.verbose=verbose

        #Corrects time column to play nicely with everything else
  
        tvals=pd.to_datetime(self.data['Time'], format='%H:%M:%S')
        tarr=[i.asm8.astype(np.int64) for i in tvals]
        self.data['Time']=tarr
        
        
        self.data['Date'] = pd.to_datetime(self.data['Date'], format='%d/%m/%Y')

        
        #Useful Variables
        self.names=self.data['Person'].unique() #Array of
        self.dates=self.data['Date'].unique()

        #Grab Errors for full dataset
        if self.verbose:
            print("Grabbing full set of errors")
        self.errortable=self.getErrors(self.data)

        #Grab Personal Errors
        nameerrarr=[]
        for name in self.names:
            if self.verbose:
                print(f"Getting errors for {name}")
            nameerrarr.append(self.getErrors(self.data[self.data['Person']==name]))
            
        #Nice little dictionary
        self.nameerrdict={name : err for name,err in zip(self.names, nameerrarr)}


        if self.verbose:
            print("Initialised data, ready to plot!")
            
    def getErrors(self, df):
        '''
        Parameters
        ----------
        df : Dataframe.

        Returns
        -------
        errortable : Errors for each date.

        '''
        #Errors By Date:
        errortable=pd.DataFrame()
        errortable['Date']=self.dates
        errortable['Mean_Time']=np.nan
        errortable['StdDev_Time']=np.nan
        errortable['Mean_Guess']=np.nan
        errortable['StdDev_Guess']=np.nan
 
        for index,date in enumerate(self.dates):
            dataslice=df.loc[df['Date']==date]
            errortable['Mean_Time'][index]=np.mean(dataslice['Time'])
            errortable['StdDev_Time'][index]=np.std(dataslice['Time'])
            
            errortable['Mean_Guess'][index]=np.mean(dataslice['Number of Guesses'])
            errortable['StdDev_Guess'][index]=np.std(dataslice['Number of Guesses'])

        return errortable
           
        

    def totaltimes(self):
        print(self.errortable)
        
        fig= plt.figure()
        ax=fig.add_subplot(1,1,1)
        
        ax.plot(self.errortable['Date'], pd.to_datetime(self.errortable['Mean_Time'], unit='ns'))
        xformatter = mdates.DateFormatter('%H:%M')
        ax.yaxis.set_major_formatter(xformatter)

       

        
        # formatter = DateFormatter('%Y-%m-%d %H:%M:%S')
        # ax.yaxis.set_major_formatter(formatter)#,
        #              #yerr=pd.to_datetime(self.errortable['StdDev_Time']).dt.strftime('%H:%M:%S'))
        plt.show()
       
            

if __name__=="__main__":
    FILE="~/WordlePlotter/worldeplotter.csv"
    x=wordleplotter(FILE)
    print(x.errortable)
    x.totaltimes()