from WikiCrawl import * 

#Find Between Specified
crawl = WikiCrawl(start_url = 'https://en.wikipedia.org/wiki/Entscheidungsproblem',
end_url = 'https://en.wikipedia.org/wiki/My_Little_Pony:_Friendship_Is_Magic',
max_iter = 6, 
save_path = 'Data/')

#Start Searching
crawl.find_path()

