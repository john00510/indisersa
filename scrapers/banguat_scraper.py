import requests, time, traceback, pyodbc
from lxml import html
from datetime import datetime


url = 'http://banguat.gob.gt/default.asp'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0',
}

def get_rate():
    date = datetime.now().strftime('%m/%d/%Y')
    
    r = requests.get(
        url,
        headers=headers,
        )
    tree = html.fromstring(r.content)
    
    element = tree.xpath('.//tr[@class="txt-resumen"]/td[./strong/a[contains(@href, "cambio/default.asp")]]/following-sibling::td/text()')
    sql = "INSERT INTO banguat (date_scraped, banguate_rate) values ('%s', '%s')" % (date, element[0].strip())
    cur.execute(sql)
    conn.commit()


if __name__ == "__main__":
    global conn
    global cur

    conn = pyodbc.connect(r'DRIVER={SQL SERVER};SERVER=(local);DATABASE=hotels;Trusted_Connection=Yes;')
    cur = conn.cursor()
    
    fh = open('C:\\users\\indisersa\\Desktop\hotels\\logs\\banguat.log', 'w')
    
    try:
        get_rate()
    except Exception:
        traceback.print_exc(file=fh)
        
    fh.close()    