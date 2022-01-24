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
import matplotlib.dates as mdates
import datetime
from matplotlib.backends.backend_pdf import PdfPages

plt.rcParams['font.sans-serif'] = "Comic Sans MS"


class wordleplotter():
    '''
    Does wordle plotting stuff!
    '''
    def __init__(self, pathtodata, outname, verbose=False):
        '''
        

        Parameters
        ----------
        pathtodata : String, Path to data
        outname : String, Path to outputs
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
        self.output=outname
        #Time Formating
        self.data['Time']=pd.to_datetime(self.data['Time'], format='%H:%M:%S')
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
        self.figs=[]

        if self.verbose:
            print("Initialised data, ready to plot!")
    
    #Methods for returning stuff
    
    def displayError(self):
        if self.verbose:
            print(self.errortable)
        return self.errortable
    
    def displayData(self):
        if self.verbose:
            print(self.data)
        return self.data
    
    def displayNames(self):
        if self.verbose:
            print(self.names)
        return self.names
    
    def displayDates(self):
        return self.dates
    
    def setVerbose(self, verbose):
        if not isinstance(verbose, bool):
            raise TypeError(f"Verbosity must be of type bool not type {type(verbose)}")
        self.verbose=verbose
        print(f"Switching verbosity to {self.verbose}")
        
    def displayNameErrDict(self):
        if self.verbose:
            print(self.nameerrdict)
        return self.nameerrdict
        
    def displayOutput(self):
        if self.verbose:
            print(self.output)
        return self.output
            
    #Grab errors while they're hot 
    
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
            errortable['StdDev_Time'][index]=pd.to_timedelta(np.std(dataslice['Time']))
            
            errortable['Mean_Guess'][index]=np.mean(dataslice['Number of Guesses'])
            errortable['StdDev_Guess'][index]=np.std(dataslice['Number of Guesses'])

        #Get rid of bad stuff
        return errortable.dropna()
           
    def setAxisStuff(self, ax):
        ax.tick_params(axis='both', which='major', labelsize=10)
        ax.tick_params(axis='both', which='minor', labelsize=8)
        return ax
    
    #Plot total times

    def saveToOutput(self):
       
        pdf = PdfPages(f'{self.output}.pdf')
        for fig in self.figs:
            pdf.savefig(fig)
        pdf.close()
        plt.close('all')
        
        
    def plotTimes(self, errors, name=None):
        '''
        

        Parameters
        ----------
        errortable : PD DataFrame
            DataFrame with error.
        name : String, optional
            Adds name to title. The default is None.

        Returns
        -------
        None.

        '''
        if not 'Date' in errors:
            raise ValueError("Date is not present in given error array")
        if not 'Mean_Time' in errors or not 'StdDev_Time' in errors:
            raise ValueError("Error array requires time mean and standard deviation")
        if not name in self.names and name!=None:
            raise ValueError(f"Given name of {name} does not exist in {self.names}")
        
        fig= plt.figure()
        ax=fig.add_subplot(1,1,1)

        # ax.errorbar(self.errortable['Date'],
        #             pd.to_timedelta(self.errortable['Mean_Time'], unit='ns'),
        #             pd.to_datetime(self.errortable['StdDev_Time']), unit='ns')
        yformatter = mdates.DateFormatter('%H:%M')
        ax.yaxis.set_major_formatter(yformatter)

        errors.plot(x='Date', y='Mean_Time', yerr='StdDev_Time',
                             ax=ax,legend=False,capsize=10.0,
                             color='black', ecolor='red')
        ax.set_xlim([datetime.date(2022, 1, 13), datetime.date.today()])
        ax.set_ylabel("Time (O'Clock)")
        ax.set_xlabel("Date")
        ax.xaxis.labelpad=-20
        ax = self.setAxisStuff(ax)
        if name==None:
            ax.set_title("Average Time for Wordle Completion")
        else:
            ax.set_title(f"Time for Wordle Completion for : {name}")
        
        if self.verbose:    
            plt.show()
        
        self.figs.append(fig)
        return fig, ax

    def plotGuesses(self, errors, name=None):
        if not 'Date' in errors:
            raise ValueError("Date is not present in given error array")
        if not 'Mean_Guess' in errors or not 'StdDev_Guess' in errors:
            raise ValueError("Error array requires time mean and standard deviation")
        if not name in self.names and name!=None:
            raise ValueError(f"Given name of {name} does not exist in {self.names}")
        plt.tick_params(labelsize=8, rotation=45)
        fig = plt.figure()
        ax=fig.add_subplot(1,1,1)
        ax.set_xlim([datetime.date(2022, 1, 13), datetime.date.today()])
        ax=self.setAxisStuff(ax)
        errors.plot(x='Date', y='Mean_Guess', yerr='StdDev_Guess', 
                    ax=ax,legend=False,capsize=10.0,
                    color='black', ecolor='red')
        
        ax.set_xlim([datetime.date(2022, 1, 13), datetime.date.today()])
        ax.set_xlabel("Date")
        ax.xaxis.labelpad=0

        ax.set_ylabel("Average number of guesses")
        if name==None:
            ax.set_title("Average Number ofGuesses for Wordle Completion")
        else:
            ax.set_title(f"Number of Guesses for Wordle Completion for : {name}")        
        
        if self.verbose:
            plt.show()
        
        self.figs.append(fig)
        
        return fig,ax
    
    def plotAverageGuessesByName(self, name_arr):
        '''
        Plots names/average score + errors

        Parameters
        ----------
        name_arr : Iterable<String>

        Returns
        -------
        axis

        '''
        if not set(self.names).issubset(name_arr):
            raise ValueError(f"name_arr provided contains names not in {self.names}")
        
        
        means=[]
        stddev=[]
        for name in name_arr:
            means.append(np.mean(self.nameerrdict[name]['Mean_Guess']))
            stddev.append(np.std(self.nameerrdict[name]['Mean_Guess']))
        
        fig = plt.figure()
        ax=fig.add_subplot(1,1,1)
        ax.bar(name_arr, means, 0.8, yerr=stddev, align='center', alpha=0.5, color='forestgreen', 
               ecolor='black', capsize=5)
        ax.set_ylabel('Average Guesses until Correct')
        ax.set_title("Average guesses for everyone")
        
        
        if self.verbose:
            plt.show()
        self.figs.append(fig)
        return fig, ax

if __name__=="__main__":
    FILE="~/WordlePlotter/worldeplotter.csv"
    OUTFILE="worldeplotter"
    x=wordleplotter(FILE, OUTFILE, verbose=False)
    errors=x.getErrors(x.displayData())
    x.plotAverageGuessesByName(x.displayNames())
    for name in x.displayNames():
        x.plotTimes(x.displayNameErrDict()[name], name=name)
        x.plotGuesses(x.displayNameErrDict()[name], name)
    x.plotTimes(x.displayError())
    x.plotGuesses(x.displayError())
    x.saveToOutput()
    