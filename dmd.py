import requests, os, json
from bs4 import BeautifulSoup
title = "Doujin Music Downloader v0.0.1"

def clear():
    if os.name=='nt':
        os.system('cls')
    else:
        os.system("cls")

def wait():
    if os.name=='nt':
        os.system("pause")
    else:
        os.system('read -n1 -r -p "Press any key to continue..."')

while True:
    clear()

    print(title)
    print(" ")
    search = input("Search: ")
    mpthree_ch = input("Do you want to search with mp3 files (doujinstyle)?(y/n) ").lower()
    if search=="": continue
    # searching in doujinstyle
    print(" ")
    print("Searching on doujinstyle...")
    ds_names = []
    ds_links = []
    ds_prev_det = ""
    for i in range(0, 1000):
        print("Current page: " + str(i))
        if mpthree_ch=="y":
            ds_response = requests.get("https://doujinstyle.com/?p=search&type=blanket&result=" + search + "&format0=on&format1=on&page=" + str(i))
        else:
            ds_response = requests.get("https://doujinstyle.com/?p=search&type=blanket&result=" + search + "&format0=on&page=" + str(i))
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
    print(" ")
    print("Searching on 9tensu...")
    nt_links = []
    nt_names = []
    headers = {
        'Host': 'www.9tensu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }
    nt_response = requests.get("http://www.9tensu.com/feeds/posts/default?alt=json-in-script&start-index=1&q=" + search + "&orderby=relevance&max-results=999999", headers=headers)
    nt_response.encoding = 'utf-8'
    clean_data = nt_response.text.replace("gdata.io.handleScriptLoaded(", "").replace(");", "") # cleaning
    try:
        json_data = json.loads(clean_data)['feed']['entry']
        for json_line in json_data:
            nt_links.append(json_line['link'][4]['href'])
            nt_names.append(json_line['link'][4]['title'])
    except KeyError:
        pass

    # results
    clear()
    names = []
    links = []
    if ds_names!=[] and ds_links!=[]:
        names = names + ds_names
        links = links + ds_links
    if nt_names!=[] and nt_links!=[]:
        names = names + nt_names
        links = links + nt_links
    if names==[] and links==[]:
        clear()
        print("Nothing!")
        print()
        wait()
        continue
    print("Total results: ")
    for i in range(len(names)-1):
        print("[" + str(i) + "] " + names[i])
    ch = input("Download: ")
    download_link = links[int(ch)]
    if "doujinstyle.com/" in download_link: # doujinstyle download logic
        pass
    elif "9tensu.com/" in download_link: # 9tensu download logic
        pass
    # TODO: downloading (until just links :P )
    clear()
    print("Link: ")
    print(download_link)
    print(" ")
    wait()
