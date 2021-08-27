import schedule
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import date

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Website's url
url = "https://www.marchespublics.gov.ma/index.php?page=entreprise.EntrepriseAdvancedSearch&AllCons&EnCours&searchAnnCons"

#Configuration of mail cordinates and city (target)
sender_address = 'sender address here'
sender_pass = 'sender password here '
receiver_address = 'receiver address here'
ville_rech = "khouribga"

corps_mail = []
corps_mailAll = []

options = Options()
options.headless = True

def main():  
    print("Recherche en cours ...")
    # Getting today's date
    Auj = date.today()
    dateAuj = Auj.strftime('%d')+"/"+Auj.strftime('%m')+"/"+Auj.strftime('%Y')

    # Link the driver of the browser
    driver = webdriver.Chrome("C://chromedriver.exe",chrome_options=options)

    villes = []
    objets = []
    acheteurs = []
    liens = []

    # Open the website  using url
    driver.get(url)

    def getData():
        j = 1
        flag = True
        while True:
            if flag == True:
                # Sorting the projects by date
                while j <= 2:
                    target = driver.find_element_by_id('ctl0_CONTENU_PAGE_resultSearch_tableauResultSearch_ctl0_ctl5')
                    target.click()
                    j = j + 1
            
            flag = False

            # Getting projetcs in khouribga city
            for i in [1,2,3,4,5,6,7,8,9,10]:
                idBalise = "ctl0_CONTENU_PAGE_resultSearch_tableauResultSearch_ctl"+str(i)+"_panelBlocCategorie"
                date = driver.find_element_by_css_selector("div[id*="+idBalise+"]+div").text.strip()
                if date != dateAuj:
                    break
                idBalise = "ctl0_CONTENU_PAGE_resultSearch_tableauResultSearch_ctl"+str(i)+"_panelBlocLieuxExec"
                ville = driver.find_element_by_css_selector("div[id*="+idBalise+"]").text.replace("...", "").strip().lower()
                if ville.rfind(ville_rech) != -1:
                    villes.append(ville)
                    idBalise = "ctl0_CONTENU_PAGE_resultSearch_tableauResultSearch_ctl"+str(i)+"_panelBlocObjet"
                    objet = driver.find_element_by_css_selector("div[id*="+idBalise+"]").text.strip()
                    objets.append(objet)
                    idBalise = "ctl0_CONTENU_PAGE_resultSearch_tableauResultSearch_ctl"+str(i)+"_panelBlocDenomination"
                    acheteur = driver.find_element_by_css_selector("div[id*="+idBalise+"]").text.strip()
                    acheteurs.append(acheteur)
                    idBalise = "ctl0_CONTENU_PAGE_resultSearch_tableauResultSearch_ctl"+str(i)+"_panelAction"
                    lien = driver.find_element_by_css_selector("div[id*="+idBalise+"]>a")
                    liens.append(lien.get_attribute("href"))

            if date != dateAuj:
                    break

            target = driver.find_element_by_id('ctl0_CONTENU_PAGE_resultSearch_PagerTop_ctl2')
            # Click the target to naviagate to destination (next page in pagination list)
            target.click()

    flag = False
    getData()

    j = 0
    # Building the body of the email
    while j < len(villes):
        flag = True
        temp = "projet N"+str(j+1)+" => "+objets[j]+"\n"+acheteurs[j]+"\nConsulter le projet ici : "+liens[j]+"\n\n"
        if corps_mail.count(temp) == 0 and corps_mailAll.count(temp) == 0:
            corps_mail.append(temp)
            corps_mailAll.append(temp)
        elif corps_mail.count(temp): 
            corps_mail.remove(temp)
        j = j + 1

    driver.close()

    # Sending the email
    if flag and len(corps_mail):
        mail_content ="Bonjour,\nnouveau(x) projet(s) dans khouribga est publié le : "+dateAuj+"\n\n"
        for elem in corps_mail:
            mail_content += elem
        #Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = receiver_address
        message['Subject'] = 'Nouveau projet'   #The subject line
        #The body and the attachments for the mail
        message.attach(MIMEText(mail_content, 'plain'))
        #Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
        session.starttls() #enable security
        session.login(sender_address, sender_pass) #login with mail_id and password
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()
        print('Mail Envoyée !!')

# Function main will be called every 30 second to check if there is any new projects published in khouribga city
schedule.every(30).seconds.do(main)

while True:
    schedule.run_pending()
    time.sleep(1)
