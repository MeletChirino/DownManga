import urllib2
import requests
import Zip_files
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os
import wget_corroncho
import sys

ok_message = '''
         __
 _(\    |@@|
(__/\__ \--/ __
   \___|----|  |   __
       \ }{ /\ )_ / _\
       /\__/\ \__O (__
      (--/\--)    \__/
      _)(  )(_
     `---''---`
'''

#link = "https://tmofans.com/viewer/5af44698d3443/cascade"
def get_images_links(driver, link):
    try:
        #driver.get(link)
        page = 0
        flag = True
        list_link = []
        #mientras hallan imagenes sigue haciendolo
        while(flag):
            try:
                xpath = '//*[@id="viewer-container"]/div[' + str(page + 1) + ']/img'
                page += 1
                element_present = EC.presence_of_element_located((By.XPATH, xpath))
                href = driver.find_element_by_xpath(xpath)
                image = href.get_attribute('src').encode('ascii','ignore')
                #lsk
                print image
                list_link.append(image)
                print 'sjfhws'
                #lo siguiente es la descarga
            except Exception as e:
                #print image
                print "No hay mas imagenes"
                print e
                flag = False
    except Exception as e:
        print "Al parecer algo salio mal"
        print e
    return list_link

def make_dir(driver, link):
    print "buscando nombre del manga"
    link = link.replace("paginated","cascade")
    try:
        driver.get(link)
        xpath = '//*[@id="app"]/section[1]/div/div/h1'
        element_present = EC.presence_of_element_located((By.XPATH, xpath))
        name = driver.find_element_by_xpath(xpath).text.encode('ascii', 'ignore')
        print "nombre encontrado con exito: " + name
        xpath = '//*[@id="app"]/section[1]/div/div/h2'
        number_raw = driver.find_element_by_xpath(xpath).text.encode('ascii', 'ignore')
        number = number_raw[8:13]
        global lil_name
        lil_name = name + '-' + number
        print number
        global mother_path
        global full_path
        mother_path = os.getcwd()
        name = name + '-' + number_raw
        full_path = mother_path + '/' + name
        if(not os.path.isdir(full_path)):
            print "creando carpeta"
            os.mkdir(name)
        else:
            print "carpeta creada con anterioridad"
        return full_path

    except Exception as e:
        print "hubo un problema encontrando el nimbre del anime:\n"
        print e

def download(list):
            #filename = wget_corroncho.download(image, '01.jpg')
        global mother_path
        global full_path
        index = 0
        loop = len(list)
        while(loop > index):
            image = list[index]
            try:
                if(index < 9):
                    str_index = '0' + str(index + 1)
                else:
                    str_index = str(index + 1)
                name_path = full_path + '/' + str_index + '.jpg'
                print 'guardando imagen ' + str_index + ' en ' + name_path
                r = requests.get(image)
                with open(name_path, 'wb') as f:
                    f.write(r.content)
                    f.close()
                    index += 1
            except Exception as e:
                print "\nAl parecer hubo un error, intentando con wget:\n"
                print e;
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                os.system('wget ' + image)
                index += 1

def delete_folder():
    global full_path
    print "borrando carpeta " + full_path
    full_path = full_path.replace(' ','\ ')
    command = 'rm -r ' + full_path
    print command, '\n'
    os.system(command)

def send_playbook(playbook_ip):
    global lil_name, full_path

    lil_name = lil_name.replace(' ','-')
    lil_name = lil_name + '.cbz'

    #full_path = full_path.replace(' ','\ ')
    full_path = full_path + '.cbz'

    print 'copiando a playbook'

    command = "cp " + full_path + ' ' + playbook_ip + '/' + lil_name

    print command
    try:
        os.system(command)
        print 'copiado a playbook'
    except:

        print 'No se encuentra la playbok'

def next_page(driver):
    flag = True
    y = 500
    while(flag):
        try:
            driver.find_element_by_xpath('//*[@id="app"]/section[2]/div/div[3]/a').click()
            flag = False
        except NoSuchElementException:
            print 'se acabaron los capitulos'
            driver.quit()
            flag = False
        except:
            y += 500
            driver.execute_script("window.scrollTo(0, " + str(y) + ")")

def main():
    try:
        global link_del_capitulo
        link_del_capitulo = raw_input('Coloca el link del capitulo\n')
        browser = webdriver.Chrome(executable_path='/home/melet/Pictures/manga ex/chromedriver')
        #abrir el WebDriver
        #executable_path="C:/Utility/BrowserDrivers/chromedriver.exe"

        # chrome_options = Options()
        # chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--window-size=400x550")
        # browser = webdriver.Chrome(chrome_options=chrome_options, executable_path='/home/melet/Pictures/manga ex/chromedriver')
        flag = True
        while(flag):
            #flag = descarga_todo(browser)#si hay otro capitulo disponible flag tomara valor positivo y el loop continuara
            #crear carpeta donde se guarden las imagenes
            try:
                make_dir(browser, link_del_capitulo)
                link_del_capitulo = browser.current_url.encode('ascii','ignore')
                #futuro
                # ---------- Bucsar los links de cada capitulo -------------
                #buscar los links de cada capitulo
                links = get_images_links(browser, link_del_capitulo)
                print links
                #Descargar las imagenes
                download(links)
                #meterlas en un formato zip
                global full_path
                Zip_files.zip_full_path(full_path)
                #borrar imagenes
                delete_folder()
                send_playbook('/run/user/1000/gvfs/smb-share:server=192.168.1.91,share=media/books')
                print ok_message
                print "proximo capitulo"
                #next page
                next_page(browser)
                link_del_capitulo = browser.current_url.encode('ascii','ignore')
                print "capitulo proximo ", link_del_capitulo
                flag = True
            except NoSuchElementException:
                print "Se acabaron los capitulos"
                flag = False
            except:
                print "O se acabaron los capitulos o algo salio mal"
                flag =  False
        #os.system('clear')
        print ok_message
    except Exception as e:
        print 'Hubo un problema\n'
        print e

if __name__== "__main__":
    main()
