from WikiCrawl import * 

#Find Number of Clicks Between Specified URLs
crawl = WikiCrawl(start_url = 'https://en.wikipedia.org/wiki/Entscheidungsproblem',
end_url = 'https://en.wikipedia.org/wiki/My_Little_Pony:_Friendship_Is_Magic',
max_iter = 6, 
save_path = 'Data/')

#Start Searching
crawl.find_path()

#Initialize ExportViz With Data From The 'crawl' Instance of WikiCrawl
exp = ExportViz('Data/b939c0ade3436e8945a03753d35722de39dfc84a-'+
'a2212e0647d7bc34252dd05124c2d98b3e3120f8.pickle')

#Export the Pruned Tree
exp.export_gexf(prune = True)

