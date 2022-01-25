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
from matplotlib import cm
import random
#plt.rcParams['font.sans-serif'] = "Comic Sans MS"


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
        self.good_head=['Person', 'Date', 'Time', 'Number of Guesses', 
                   'Correct Letters Guess 1', 'Correct Letters Guess 2', 
                   'Correct Letters Guess 3', 'Correct Letters Guess 4', 
                   'Correct Letters Guess 5', 'Correct Letters Guess 6']
        if not set(self.good_head).issubset(set(self.data.columns.values)):
            raise IOError(f"Columns should be : {self.good_head}\n, "\
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
        self.colourdict={'Rhi':"palevioletred", 
                "Kathryn":"forestgreen",
                "Celeste":"indigo"}

        #Grab Errors for full dataset
        if self.verbose:
            print("Grabbing full set of errors")
        self.figs=[]

        if self.verbose:
            print("Initialised data, ready to plot!")

    
    #Methods for returning stuff
    def getColour(self, name):
        if name in self.colourdict.keys():
            colour=self.colourdict[name]
        else:
            colour=cm.rainbow(random.randint(1,250))
            self.colourdict[name] = colour
        return colour
                             
    
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
    
    def setAxisStuff(self, ax):
        ax.tick_params(axis='both', which='major', labelsize=10)
        ax.tick_params(axis='both', which='minor', labelsize=8)
        return ax
    
    #Plot total times
    
    def saveToOutput(self):
        pdf = PdfPages(f'{self.output}.pdf')
        for fig in self.figs:
            pdf.savefig(fig)
            plt.close(fig)
        pdf.close()
            
    def getMeanVariables(self, datatable, variable, binvar=None, binval=None,  name=None):
        '''

        Parameters
        ----------
        variable : String,
            Variable you need standard deviation and mean of
        name : String, optional
            Persons name. The default is None.
        date : String, optional
            Date. The default is None.
        Raises
        ------
        ValueError
            If person provides name/data not present in data,  breaks.

        Returns
        -------
        Mean times and standard deviations.

        '''
        if variable not in self.good_head:
            raise ValueError(f"Variable {variable} not in {self.good_head}")
        if name not in self.displayNames() and name!=None:
            raise ValueError(f"{name} not in {self.names}")
        if name!=None:
            datatable=datatable[datatable['Person']==name]
        if binvar!=None:
            datatable=datatable[datatable[binvar]==binval]
        
        mean=datatable[variable].mean()
        stddev=datatable[variable].std()
        return mean, stddev
    
        '''
        Plots we want:
            1 Average time submitted/date
            2 Person's submit time against date
            3 Average number of guesses/date
            4 Person's number of guesses/date
            5 Everyone's guess total in bar plot (both for a given date and for all dates)
            6 Hist of total number of guesses binned by time [variable binning]
            
        COMMON AXES
            1,2 : Same x,y axes 
                -Want same code but make errors optional
            3,4 : (See above) 
        '''
        
        
    def getMean_Error(self, datatable, binvar, variable, name=None):
        #Gets errors based on date, returns dataframe of date, mean etc.

        if variable not in datatable.columns.values.tolist() and variable!=None:
            raise ValueError(f"Variable not in {datatable.columns.values.tolist}")
        if binvar not in datatable.columns.values.tolist():
            raise ValueError(f"Binning variable not in {datatable.columns.values.tolist}")
        if name!=None:
            datatable=datatable[datatable['Person']==name]
            if variable=='Time':
                datatable['Time']=pd.to_datetime(datatable['Time'], format='%H:%M:%S')
        
        if self.verbose:
            print("Getting errors for {variable} per {binvar}")
        binvararr=datatable[binvar].unique()
        meanarr=[]
        stddevarr=[]
        for b in binvararr:
            #print(b)
            m,s=self.getMeanVariables(datatable, variable, binvar, b, name=name)
            meanarr.append(m)
            stddevarr.append(s)
            
        datemeanstd=pd.DataFrame()
        datemeanstd[binvar]=binvararr
        datemeanstd['Mean']=meanarr
        datemeanstd['Error']=stddevarr
        
        return datemeanstd

    def formatTimeErrors(self, dataframe):
        #Reformats errors of timestamps
        dataframe['Error']=pd.to_timedelta(dataframe['Error'])
        return dataframe
    
    def formatTimeAxis(self):
        return mdates.DateFormatter('%H:%M')

    def formatDateAxis(self, ax):
        ax.set_xlim([datetime.date(2022, 1, 13), 
                     datetime.date.today()+datetime.timedelta(1)])
        ax.set_xlabel("Date")
        ax.xaxis.labelpad=-20

        return ax

    
    def getAverageTimeDate(self, df, name=None):
        #df goes in, means by date go out
        meandf=self.getMean_Error(df, 'Date', 'Time', name=name)
        meandf=meandf.dropna()
        #print(meandf)
        meandf = self.formatTimeErrors(meandf)
        if self.verbose:
            print(meandf)
        return meandf
    
    def getAverageGuessDate(self, df, name=None):
        meandf=self.getMean_Error(df, 'Date', 'Guess', name=name)
        if self.verbose:
            print(meandf)
        return meandf
    
##############################    
    
    def doLinePlot(self, ax, data, label, xname, yname, yerr=None,
                   color='black', backplot=False):
        #Does line plot for stuff
        self.setAxisStuff(ax)
        kwargs={}
        ecolor='red'
        
        if backplot==True:
            ecolor='grey'
            color='black'
            optkwargs={'alpha':0.5,'linestyle':'dashed'}
            kwargs={**kwargs,**optkwargs}
        if yerr!=None:
            optkwargs={'yerr':yerr, 'ecolor':ecolor,'capsize':10.0}
            kwargs={**kwargs,**optkwargs}

        data.plot(x=xname, y=yname, ax=ax, label=label, legend=False, color=color, **kwargs)
        return ax
    
    def plotAverageTimeDate(self, backplot=False):
        df=self.displayData()
        meandf=self.getMean_Error(df, 'Date', 'Time')
        
        fig=plt.figure() 
        ax= fig.add_subplot(1,1,1)
        ax.yaxis.set_major_formatter(self.formatTimeAxis())
        ax=self.doLinePlot(ax, meandf, 'Average Data Set', 'Date', 'Mean',
                           yerr='Error', backplot=backplot)
        ax=self.formatDateAxis(ax)
        ax.set_ylabel("Time/O'Clock")
        self.figs.append(fig)
        return fig,ax

    def plotTimeDateName(self, name):
        df=self.displayData()

        fig,ax = self.plotAverageTimeDate(backplot=True)
        #Don't want to double plot!
        self.figs=self.figs[:-1]
        
        meandf=self.getMean_Error(df, 'Date', 'Time',name=name)
        ax=self.doLinePlot(ax, meandf, f'{name}', 'Date', 'Mean',
                           color=self.getColour(name))
        self.figs.append(fig)
        ax.legend()
        ax.set_title(f"Time of day Submitted for {name}")
        return fig,ax
    
    def plotAverageGuessDate(self, backplot=False):
        df=self.displayData()
        meandf=self.getMean_Error(df, 'Date', 'Number of Guesses')
        
        fig=plt.figure() 
        ax= fig.add_subplot(1,1,1)
        ax=self.doLinePlot(ax, meandf, 'Average Data Set', 'Date', 'Mean',
                           yerr='Error', backplot=backplot)
        ax=self.formatDateAxis(ax)
        ax.set_ylabel("Number of Guesses")
        self.figs.append(fig)
        return fig,ax
    
    def plotGuessDateName(self, name):
        df=self.displayData()

        fig,ax = self.plotAverageGuessDate(backplot=True)
        #Don't want to double plot!
        self.figs=self.figs[:-1]
        
        meandf=self.getMean_Error(df, 'Date', 'Number of Guesses',name=name)
        ax=self.doLinePlot(ax, meandf, f'{name}', 'Date',
                           'Mean', color=self.getColour(name))
        self.figs.append(fig)
        ax.legend()
        ax.set_title(f"Number of guesses submitted for {name}")
        return fig,ax

    def plotPersonalPlots(self, namearr):
        for name in namearr:
            self.plotTimeDateName(name)
            self.plotGuessDateName(name)
            
##########################

    def getBarPlot(self, ax, datatable, binvar, variable, bins):
        meanstdarr=self.getMean_Error(datatable, binvar=binvar,
                                          variable=variable)
        meanstdarr=meanstdarr[meanstdarr[binvar].isin(bins)]
        
        if variable=='Time':
            meanstdarr['Mean']=meanstdarr['Mean'].dt.strftime('%H%M%S')
            meanstdarr['Error']=meanstdarr['Error'].dt.strftime('%H%M%S')
            
            
        if binvar=='Person':
            colarr=[self.getColour(name) for name in bins]
        else:
            colarr=[cm.rainbow(1.*t/len(bins)) for t in range(len(bins))]
    
        
        meanstdarr.plot.bar(ax=ax, x=binvar, y='Mean', yerr='Error',
                            capsize=30/len(bins), color=colarr,legend=False)
        return ax

    def plotAverageGuessBar(self,datatable,namesarr):
        #Plots average guesses as bare
        if not set(namesarr).issubset(set(self.names)):
            raise ValueError(f"Names provided aren't in {self.names}")
        fig=plt.figure()
        ax=fig.add_subplot(1,1,1)
        
        ax=self.getBarPlot(ax, datatable, 'Person', 'Number of Guesses', namesarr)
        ax.set_ylabel("Average Guess")
        ax.set_title("Average number of guesses until correct per person")
        ax.set_xticklabels(namesarr, fontsize=6, rotation=0)
        self.figs.append(fig)
        return fig,ax

    def plotNLettersPlot(self, datatable, N):
        bins=datatable[f'Correct Letters Guess {N}'].unique()
        fig=plt.figure()
        ax=fig.add_subplot(1,1,1)
        ax=self.getBarPlot(ax, datatable, f'Correct Letters Guess {N}', 
                           'Number of Guesses', np.sort(bins))
        ax.set_ylabel("Average Attempts to Guess")
        ax.set_xlabel(f"Number of Correct Letters in Guess {N}")
        ax.set_title(f"Average attempts given guess {N} has x correct letters")
        ax.set_xticklabels(np.sort(bins),fontsize=6, rotation=0)
        self.figs.append(fig)
        return fig,ax

    def doMyPlotting(self):
        _,ax1=self.plotAverageGuessDate()
        ax1.set_title("Average Guesses to be Correct Per Day")
        _,ax2=self.plotAverageTimeDate()
        ax2.set_title("Average time submitted per day")
        namesarr=self.names
        namesarr=np.delete(namesarr, np.where(namesarr=='Owen'))
        self.plotAverageGuessBar(self.displayData(),namesarr)
        self.plotNLettersPlot(self.displayData(),1)
        self.plotPersonalPlots(namesarr)
        self.saveToOutput()


if __name__=="__main__":

    
    FILE="~/WordlePlotter/worldeplotter.csv"
    OUTFILE="wordleplotter"
    x=wordleplotter(FILE, OUTFILE, verbose=False)
    x.doMyPlotting()
    