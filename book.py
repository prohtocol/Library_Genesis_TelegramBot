from bs4 import BeautifulSoup as bs
import requests
import demoji

import config


def link_to_get(link):
    """This function retrieves the direct download link
    and image link for a given book download link"""
    response = requests.get(link)
    th_html = bs(response.text, "html.parser")
    td_all = th_html.find("td", id="info")
    td_a = td_all.find_all("a")
    link_href = td_a[1].get("href")
    img_link_td = td_all.find("img", alt="cover")
    img_link_src = img_link_td.get("src")
    img_link = f"http://library.lol{img_link_src}"
    return [link_href, img_link]


def book_get(name, mainres=25, results=5):
    """This function returns a list of
    books based on the given search criteria"""
    books = []
    name = demoji.replace(name, "")
    if name == "":
        return "Error: enter name"
    name = name.replace(" ", "+")
    url = f"http://libgen.is/search.php?req={name}\
    &lg_topic=libgen&open=0&view=simple&res={mainres}&phrase=1&column=def"
    response = requests.get(url)
    bs_html = bs(response.text, "html.parser")

    if "Search string must contain minimum 3 characters.." in bs_html.body:
        return "Error: Title Too Short"

    table = bs_html.find_all("table")[2]
    table_rows = table.find_all("tr")[1:]
    counter = 0
    for row in table_rows:
        if counter > results:
            break
        book_lst = []
        table_datas = row.find_all("td")
        book_name = table_datas[2].get_text()
        author = table_datas[1].get_text()
        publisher = table_datas[3].get_text() or "unknown"
        if publisher in config.RED_Publishers or author in config.RED_Authors:
            break
        link_row = table_datas[9]
        link = link_row.find("a", href=True).get("href")
        link_all = link_to_get(link)
        language = table_datas[6].get_text()
        size = table_datas[7].get_text()
        type_ofit = table_datas[8].get_text()
        book_lst.extend(
            [
                book_name,
                author,
                publisher,
                size,
                type_ofit,
                link_all[0],
                link_all[1],
                language,
            ]
        )
        books.append(book_lst)
        counter += 1

    if len(books) >= 1:
        return books
    else:
        return "Error: no results found"


def debug():
    res = book_get("Python", 25, 5)
    if "Error" in res:
        print(res)
        return

    for book in res:
        print(
            f"\n\nName : {book[0]}\nAuthor : {book[1]}\n "
            f"Publisher : {book[2]}\nSize : {book[3]}\n"
            f"Format : {book[4]}\n Link : {book[5]}\nImage : {book[6]}\n\n"
        )


if __name__ == "__main__":
    debug()
