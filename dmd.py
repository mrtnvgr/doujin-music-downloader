import requests, os, json, sys, time, re
from bs4 import BeautifulSoup
title = "Doujin Music Downloader v0.0.6"

def clear():
    if os.name=='nt':
        os.system('cls')
    else:
        os.system("clear")

def wait():
    if os.name=='nt':
        os.system("pause")
    else:
        os.system('read -n1 -r -p "Press any key to continue..."')

while True:
    clear()
    print(title)
    print()
    args = sys.argv
    mpthree_ch = "n"
    repeats_ch = "n"
    log_name = ""
    log_type = "json"
    search = ""
    if len(args)>1:
        for i in range(len(args)):
            if args[i]=="--search" or args[i]=="-s":
                search = args[i+1]
            elif args[i]=="--mp3" or args[i]=="-m":
                mpthree_ch = args[i+1].lower()
            elif args[i]=="--file" or args[i]=="-f":
                    log_name = args[i+1]
            elif args[i]=="file-type" or args[i]=="-ft":
                    log_type = args[i+1]
            elif args[i]=="--repeats" or args[i]=="-r":
                repeats_ch = args[i+1].lower()
            elif args[i]=="--help" or args[i]=="-h":
                print("dmd.py [...]")
                print(" Arguments: ")
                print(" --help(-h) - print this text")
                print(" --search(-s) - search text")
                print(" --mp3(-m) - mp3 doujinstyle toggle search (y/n, default=n)")
                print(" --repeats(-r) - remove similar albums from output (y/n, default=n)")
                print(" --file(-f) - file output name")
                print(" --file-type(-ft) - file output type (text/json, default=json)")
                sys.exit(0)
        if search=="": # search not specified
            print("--search(-s) required: use --help")
            sys.exit(0)
        elif mpthree_ch=="":
            print("--mp3(-m) required: use --help")
            sys.exit(0)
        elif log_name=="":
            print(" --file(-f) required: use --help")
            sys.exit(0)
    else:
        search = input("Search: ")
        if search=="": continue
        mpthree_ch = input("Do you want to search with mp3 files (doujinstyle)?(y/n): ").lower()
        repeats_ch = input("Do you want to remove similar albums?(y/n): ").lower()
    # capture origin time
    start_time = time.monotonic()
    # searching in doujinstyle
    print()
    print("Searching on doujinstyle...")
    ds_names = []
    ds_links = []
    ds_prev_det = ""
    for i in range(0, 1000):
        print("Current page: " + str(i))
        try:
            if mpthree_ch=="y":
                ds_response = requests.get("https://doujinstyle.com/?p=search&type=blanket&result=" + search + "&format0=on&format1=on&page=" + str(i))
            else:
                ds_response = requests.get("https://doujinstyle.com/?p=search&type=blanket&result=" + search + "&format0=on&page=" + str(i))
        except TimeoutError:
            print("Connection failed! Check your internet connection.")
            sys.exit(0)
        ds_response.encoding = 'utf-8'
        soup = BeautifulSoup(ds_response.text, 'lxml')
        ds_details = soup.find_all('div',class_='gridDetails')
        if ds_details==[]:
            break
        if ds_prev_det==ds_details: # if page end
            break
        ds_prev_det = ds_details
        for ds_detail in ds_details:
            ds_href = ds_detail.find('a')
            ds_names.append(ds_href.find('span', class_='limitLine tagGap').text)
            ds_links.append("https://doujinstyle.com" + ds_href['href'][1:])

    # searching in 9tensu
    print()
    print("Searching on 9tensu...")
    nt_links = []
    nt_names = []
    tensu_headers = {
        'Host': 'www.9tensu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }
    nt_response = requests.get("http://www.9tensu.com/feeds/posts/default?alt=json-in-script&start-index=1&q=" + search + "&orderby=relevance&max-results=999999", headers=tensu_headers)
    nt_response.encoding = 'utf-8'
    clean_data = nt_response.text.replace("gdata.io.handleScriptLoaded(", "").replace(");", "") # cleaning
    try:
        json_data = json.loads(clean_data)['feed']['entry']
        for json_line in json_data:
            nt_links.append(json_line['link'][4]['href'])
            nt_names.append(json_line['link'][4]['title'])
    except KeyError:
        pass
    names = []
    links = []
    if ds_names!=[] and ds_links!=[]:
        names = names + ds_names
        links = links + ds_links
    if nt_names!=[] and nt_links!=[]:
        names = names + nt_names
        links = links + nt_links
    print()
    print("Converting...")
    for i in range(len(links)):
        if "https://doujinstyle.com" in links[i]:
            headers = {
                'Host':'doujinstyle.com',
                'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0',
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language':'en-US,en;q=0.5',
                'Accept-Encoding':'gzip, deflate, br',
                'Content-Type':'application/x-www-form-urlencoded',
                'Origin': 'https://doujinstyle.com',
                'Connection': 'keep-alive',
                'Referer': links[i],
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
            }
            links[i] = requests.post(links[i], headers=headers, data=b"type=1&id=" + links[i].split("id=")[1].split("&")[0].encode() + b"&source=0&download_link=", allow_redirects=False).headers["location"]
        elif "http://www.9tensu.com" in links[i]:
            for line in requests.get(links[i], headers=tensu_headers).text.split("\n"):
                if "EXTRA : " in line:
                    links[i] = ' '.join(re.findall(r'(?<=<a href=")[^"]*', line))
                    continue
    # printing time
    print("Seconds elapsed: " + str(int(time.monotonic()-start_time)))
    if repeats_ch=="y":
        t_names = []
        for i in range(len(names)):
            try:
                if names[i].lower().replace(" ", "") not in t_names:
                    t_names.append(names[i].lower().replace(" ", "")) # bug fix
                else:
                    names.remove(names[i])
                    links.remove(links[i])
            except IndexError:
                i = i - 1
                continue
    if len(args)>1: # output
        if names!=[] or links!=[]:
            if log_type=="json":
                json_string = "{"
                for i in range(len(names)):
                    update = '"album": {"name": "' + names[i] + '", "link": "' + links[i] + '"}'
                    if json_string=="{":
                        json_string = "{" + update
                    else:
                        json_string = json_string + "," + update
                json_string = json_string + "}"
                open(log_name + ".json", "w", encoding="UTF-8").write(json_string)
            elif log_type=="text":
                log_text = ""
                for i in range(len(names)):
                    log_text = log_text + "\n" + names[i] + " (" + links[i] + ")"
                open(log_name, "w", encoding="UTF-8").write(log_text)
        sys.exit(0)
    if names==[] and links==[]:
        clear()
        print("Nothing!")
        print()
        wait()
        clear()
        continue
    while True:
        print()
        print("Total results: ")
        for i in range(len(names)-1):
            print("[" + str(i) + "] " + names[i])
        ch = input("Download (all-view all links): ")
        if ch=="": continue
        clear()
        if "," in ch:
            print("Links: ")
            for link in ch.split(","):
                print("[" + link + "] " + links[int(link)])
        else:
            if ch.lower()=="m":
                break
            if ch.lower()=="all":
                print("Links: ")
                for link in range(len(names)):
                    print("[" + str(link) + "] " + links[link])
            else:
                print("Link: ")
                print(links[int(ch)])
        print()
        chh = input("Main menu/Current download list/Quit(m,c,q): ")
        if chh=="m":
            break
        elif chh=="c":
            continue
        elif chh=="q":
            sys.exit(0)
    clear()
