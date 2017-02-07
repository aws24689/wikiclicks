# !/usr/bin/env python3
# Author: Austin Smith - https://github.com/aws24689

# Import Dependencies
import requests
from bs4 import BeautifulSoup
import pickle
import networkx as nx
import time

class WikiDump:
    """Class to Create Networkx Digraph With a Node for Every Single Wiki Page.

    Pulls every single Wikipedia page starting at a seed page specified by user. It loops through
    all pages until it reaches a max number of nodes. It can be restarted so it doesn't need to be
    run at once. This script can take a very long time to run, and is very memory intensive.

    Parameters
    ----------
    stop_count : int
        The number at which to stop looping. As of February 2017, there are 5,323,885 pages on
        Wikipedia. The default value is set to 5,000,000. Additionally, this can be run again with
        a higher stop_count. The algorithm will likely stop slightly higher than the stop_count,
        due to the way the iterations work.
    seed_page : str
        The page to start the network from. Chose a page with a large quantity of links on it for
        this, the default is: 'https://en.wikipedia.org/wiki/United_States'. If an invalid URL is
        entered, the program will initialize with a random seed_page.
    rand_seed : bool
        True or False. If True, it will ignore the seed_page parameter and initialize with a random
        seed.
    save_path : str
        The path for which the output should be saved. It defaults to 'Data/fullnet1.pickle'. This
        must end in *.pickle.

    new_dump : bool
        True or False, default is True. If True, it will start from the seed, if False it will
        start with a user specified previous run.

    previous_path : str
        If starting from a previously created file enter the filepath here including the *.pickle
        portion.

    save_increment : int
        The approximate value for how frequently the data is saved. Default is 100,000,
        however, it may be better to use smaller to avoid losing data in between saves.
        On save, it prints the current time and whether or not it was successfully written.
        It will save as close to this interval as possible but may be slightly over due to the
        nature of the scraping process.

    suppress_output : bool
        True or False, if set to True, the script will run silent and only display a message to
        indicate it has reached the stop_count.

    Examples
    --------
    >>> # Start New Dump
    >>> WD = WikiDump(save_path = "Data/Full_WIKI.pickle")
    >>> WD.start_dump()
    [OUTPUT]
    >>> # Restart Previous Dump
    >>> NWD = WikiDump(stop_count = 5000000, rand_seed = False,
    >>> save_path = "Data/Full_WIKI1.pickle", new_dump = False, 
    >>> previous_path = "Data/Full_WIKI.pickle", save_increment = 10000, suppress_output = False)
    >>> NWD.start_dump()
    [OUTPUT]
    
    """
    def __init__(self, stop_count = 5000000, seed_page = 'https://en.wikipedia.org/wiki/United_States', rand_seed = False, save_path = 'Data/fullnet1.pickle', new_dump = True, previous_path = None, save_increment = 100000, suppress_output = False ):
        self.__suppress_output = suppress_output
        self._stop_count = stop_count
        # Setting Seed
        self._seed = seed_page
        if rand_seed != True:
            # Check if Valid, If not Use random
            if self.verify_url(seed_page) == True:
                self._seed = seed_page
            if self.verify_url(self._seed) != True:
                self.alert("Invalid Seed Page! Using Random Page")
                self._seed = self.rand_wiki()
        if rand_seed == True:
            self._seed = self.rand_wiki()
        
        self._save_path = save_path
        self._new = new_dump
        self._save_inc = save_increment
        self._previous = previous_path
        
        if new_dump != False:
            self.alert("Seed Page Set to: {}".format(self._seed))
            
        # Initializing DiGraph
        if self._new == True:
            self._G = nx.DiGraph()
            self._G.add_node(self._seed)
            self._viewed = dict()
        if self._new == False:
            try:
                self.alert("Initializing Previous Network...")
                with open(self._previous, 'rb') as handle:
                    self._G = pickle.load(handle)

                with open(self._previous[:-7]+'dict'+'.pickle', 'rb') as handle:
                    self._viewed = pickle.load(handle)
                self.alert("Previous Network Initialized With {} Nodes".format(len(self._G.nodes())))
            except:
                self.alert("Graph Initialization Failed!")
                     
    def get_urls(self, url):
        """Searches through webpage for any link between <p> tags.
        
        Parameters
        ----------
        url : str
            URL of page to search for links.
        Returns
        -------
        list
            List of URLs on page.

        """
        #Get/Parse Website
        resp = requests.get(url)
        page = BeautifulSoup(resp.text,"lxml")
        #Emptry Links list
        links = []
        #Loop Through the p Tags
        for x in page.find_all('p'):
            #Parse URLS Into List
            l = [g.get('href') for g in x.find_all('a') if 'en.wikipedia.org' not in g.get('href')]
            l = [k for k in l if ':Citation_needed' not in k]
            l = [k for k in l if '//' not in k]
            l = ['https://en.wikipedia.org'+ k for k in l if '#' not in k]
            #Append Valid URLS Into Links List
            [links.append(r) for r in l]
        #Return List of Links
        return(links)
            
    def rand_wiki(self):
        """Returns verified URL for random Wikipedia page.
        
        Parameters
        ----------
        None.

        Returns
        -------
        str
            Full Wikipedia URL

        """

        resp = requests.get('https://en.wikipedia.org/wiki/Special:Random')
        page = BeautifulSoup(resp.text,"lxml")
        url = 'https://en.wikipedia.org'+page.find_all('a',{'accesskey':'c'})[0].get('href')
        if verify_url(url) == True:
            return(url)
        
    def verify_url(self, url):
        """Checks to see if a URL is a valid Wikipedia page.

        Parameters
        ----------
        url : str
            url to verify

        Returns
        -------
        bool
            True or False

        """
        if 'https://en.wikipedia.org/wiki/' in url: 
            return(True)
            
    def alert(self, message):
        """Prints Message if User Has Not Suppressed the Outputs

        Checks to determine whether or not the user has the suppressed_outputs parameter set to
        True, if not, it prints the message passed to the function.

        Parameters
        ----------
        url : str
            URL to verify

        """
        if self.__suppress_output != True:
            print(message)
                
    def start_dump(self):
        """Starts Building Network of Wikipedia Pages"""
        nds_save = 0 
        while len(self._G.nodes()) < self._stop_count:
            for i in self._G.nodes():
                nds = len(self._G.nodes())
                if i not in self._viewed:
                    temp = self.get_urls(i)
                    for j in temp:
                        self._G.add_edge(i,j)
                    self._viewed[i] = 1
                if nds > nds_save:
                    nds_save = nds+self._save_inc
                    self.alert(time.ctime(time.time()))
                
                    with open(self._save_path, 'wb') as handle:
                        pickle.dump(self._G, handle, protocol = pickle.HIGHEST_PROTOCOL)
                    with open(self._save_path[:-7]+'dict'+'.pickle', 'wb') as handle:
                        pickle.dump(self._viewed, handle, protocol = pickle.HIGHEST_PROTOCOL)
                    self.alert("File Saved! # of Nodes:{}".format(nds))
                    
                if nds > self._stop_count:
                    break
        print("Program Complete! Node Count Reached {}".format(self._stop_count))
        with open(self._save_path, 'wb') as handle:
            pickle.dump(self._G, handle, protocol = pickle.HIGHEST_PROTOCOL)
        with open(self._save_path[:-7]+'dict'+'.pickle', 'wb') as handle:
            pickle.dump(viewed, handle, protocol = pickle.HIGHEST_PROTOCOL)
            print(time.ctime(time.time()))
            print("File Saved! # of Nodes:{}".format(nds))
