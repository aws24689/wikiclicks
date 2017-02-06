#!/usr/bin/env python3
#Author: Austin Smith - https://github.com/aws24689

#Import Depencies
import requests
from bs4 import BeautifulSoup
from treelib import Node, Tree
import pickle
import hashlib

class WikiCrawl:
    """Determintes The Number of Clicks to Navigate from one Wikipedia Page to Another.

    This class constructs a tree of pages until it reaches the end webpage. It is intended 
    to be used for testing how many clicks it takes to get from one page to the next. The 
    tree is saved for future analysist in two parts. The filenames are the hash of each URL 
    seperated by a hyphen as follows:
    'b939c0ade3436e8945a03753d35722de39dfc84a-a2212e0647d7bc34252dd05124c2d98b3e3120f8.pickle'
    there is also a pickle file which stores a dictionary key to decode the hashed names. This
    file naming is necessary to avoid having special characters from the URLs in the filename.


    Parameters
    ----------
    start_url : str
        The URL for the Wikipedia page you wish to start from. Default
        is None, if left as such, it will initialize with a random
        Wikipedia page.
    end_url : str
        The destination URL for the Wikipedia page to count the number of clicks. 
        Default is None, if left as such, it will initialize with a random
        Wikipedia page.
    max_iter : int
        The number of levels to iterate through in the search.
    save_path : str
        The path for which the output should be saved. It defaults to the current
        working directory.

    Examples
    --------
    >>> wiki = WikiCrawl(start_url = 'https://en.wikipedia.org/wiki/Entscheidungsproblem',
    >>> end_url = 'https://en.wikipedia.org/wiki/My_Little_Pony:_Friendship_Is_Magic',
    >>> max_iter = 6,
    >>> save_path = 'Data/')
    
    """
    def __init__(self, start_url = None, end_url = None, max_iter = 6, save_path = ''):
        self._max_iter = int(max_iter)
        self._save_path = save_path
        
        if start_url == None:
            self._start_url = self.rand_wiki()
        else:
            self._start_url = start_url
        print('Start: ' + self._start_url)
        
        if end_url == None:
            self._end_url = self.rand_wiki()
        else:
            self._end_url = end_url
        print('End: ' + self._end_url)
        
        if self.verify_url(self._start_url) != True:
            print('Invalid Start URL, Using Random Instead')
            self._start_url = self.rand_wiki()
            print('Start: ' + self._start_url)
            
        if self.verify_url(self._end_url) != True:
            print('Invalid End URL, Using Random Instead')
            self._end_url = self.rand_wiki()
            print('End: ' + self._end_url)
            
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
        return('https://en.wikipedia.org'+page.find_all('a',{'accesskey':'c'})[0].get('href'))
    
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
        if 'https://en.wikipedia.org/wiki/' in url: return(True)
        if 'https://en.wikipedia.org/wiki/' not in url: return(False)
    
    def resolve_path(self, path):
        """Determines the pages in the path and outputs the path.
        
        Parameters
        ----------
        path : :obj:`list` of :obj:`str`:
            Ordered list of URLs in path from start url to end url.

        Returns
        -------
        str
            Prints final output report for user.

        """
        titles = []
        for x in path:
            resp = requests.get(x)
            page = BeautifulSoup(resp.text,"lxml")
            titles.append(page.find_all('title')[0].get_text())
        print('You Can Get From "{}" to "{}" in {} Clicks \nTree Size: {}\n\nPath:'
        .format(titles[0][:-12], titles[-1][:-12], len(path)-1, self._tree.size()))
        for i in range(len(titles)):
            print('{}: {}'.format(titles[i][:-12], path[i]))
            
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
        #Empty Links list
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
    
    def find_path(self):
        """Iteratively scrapes pages from start_url until end_url has been reached.

        Searches through the pages while building the tree. If max iterations are
        reached before the end_url is found it will print a message. Otherwise, the
        results are printed when the end_url is found.

        """
        self._tree = Tree()
        self._tree.create_node(self._start_url, self._start_url)
        quit  = False
        for b in range(self._max_iter):
            print('Size at Level #{}: {}'.format(self._tree.depth(), self._tree.size()))
            self.save_tree(finished = False)
            for i in self._tree.paths_to_leaves():
                try:
                    urls = self.get_urls(i[-1])
                except:
                    continue
                for x in urls:
                    try:
                        self._tree.create_node(x, x, parent = i[-1])
                        if x == self._end_url:
                            for x in self._tree.paths_to_leaves():
                                if self._end_url in x: 
                                    self.resolve_path(x)
                                    self.url_path = x
                            print('Size at Level #{}: {}'.format(self._tree.depth(), self._tree.size()))
                            self.save_tree(finished = True)
                            quit = True
                            break
                    except:
                        continue
                if quit == True: break
            if quit == True: break
        if quit != True: 
            print('You Cannot Navigate Between These Pages In {} Clicks'.format(self._max_iter))

    def save_tree(self, finished = False):
        """Saves the tree for backup purposes and upon search completion.

        Saves the files in the following format, 'hashed start_url'-'hashed end_url'.pickle
        This is to prevent the special characters in the URLs from causing the
        save to raise an error. Additionally, a file with the word 'KEY' at the end,
        which contains a dict object to allow the user to reverse the hashed URL.

        
        Parameters
        ----------
        finished : bool
            True or False, whether or not the search has been completed

        """
        filename = self.hash_url(self._start_url[30:])+'-'+self.hash_url(self._end_url[30:])
        
        name_key = {
        self.hash_url(self._start_url[30:]):self._start_url[30:],
        self.hash_url(self._end_url[30:]):self._end_url[30:],
        'Completed':finished
        }

        if finished == False:#FIX THIS FEATURE
            #Save Tree
            with open('{}.pickle'.format(self._save_path+filename), 'wb') as handle:
                pickle.dump(self._tree, handle, protocol = pickle.HIGHEST_PROTOCOL)
            #print('Tree Saved as "{}.pickle"'.format(filename))

            #Save Key
            with open('{}.pickle'.format(self._save_path+filename+str('KEY')), 'wb') as handle:
                pickle.dump(name_key, handle, protocol = pickle.HIGHEST_PROTOCOL)
            print('Tree Saved as "{}.pickle"'.format(filename))

        if finished == True: #FIX THIS FEATURE
            #Save Tree
            with open('{}.pickle'.format(self._save_path+filename), 'wb') as handle:
                pickle.dump(self._tree, handle, protocol = pickle.HIGHEST_PROTOCOL)
            #print('Tree Saved as "{}.pickle"'.format(filename))

            #Save Key
            with open('{}.pickle'.format(self._save_path+filename+str('KEY')), 'wb') as handle:
                pickle.dump(name_key, handle, protocol = pickle.HIGHEST_PROTOCOL)
            print('Tree Saved as "{}.pickle"'.format(filename))


    def hash_url(self, input_url):
        """Hashes URL into characters.
        
        Parameters
        ----------
        url : str
            URL which needs to be hashed.

        """
        """Hash URL For Filename"""
        hasher = hashlib.new('ripemd160')
        hasher.update(input_url.encode('utf-8'))
        return(hasher.hexdigest())

