from robocorp.tasks import task
from robocorp import browser

# from robocorp.browser import Browser
from RPA.Robocloud.Secrets import Secrets
from robocorp import vault
from RPA.Assistant import Assistant


assistant = Assistant()
# order_amount = 0
order_info = {}


@task
def fill_package_mailing_forms():
    # def check_orders_from_Holvi():

    """
    Chooses the right package size for each order,
    first at Holvi's webpage, then at Posti's.
    Copies orderers contact information from Holvi
    and fills Posti's mailing form.
    At some day, it might also  handle the payment...
    """
    browser.configure(
        slowmo=500,
    )
    
    open_holvi_website()
    log_in()
    go_to_orders()
    order_amount = check_how_many_orders()
    select_order(order_amount)
   # check_amount_of_ordered_products() #jos ok: copy_order_information(order_info) / jos ei ok: mene seuraavaan tilaukseen TEE TÄMÄ
    pageP = open_posti_website()
    log_in_to_posti(pageP)
    fill_the_form_and_clickety_click_everything(order_info, pageP, order_amount)

# @task
# def fill_package_mailing_forms_at_Posti():
    # pageP = open_posti_website()
    # log_in_to_posti(pageP)
    # fill_the_form_and_clickety_click_everything(order_info, pageP, order_amount)
# wait_for_payment()
# mark_order_as_done()


# check_how_many_orders()
# while orders < 0:

# select_order()
# check_amount_of_ordered_products()
# check_package_size()
# copy_contact_information()
# go_to_posti()
# log_in_to_posti()      Mihin väliin, jotta tekee vain kerran?
# fill_the_form_and_clickety_click_all()
# mark_order_done()
# check if more orders, start again

# inform user to pay to Posti


def open_holvi_website():
    """Navigates to the given URL"""
    browser.goto("https://login.app.holvi.com/")
    pageH = browser.page()
    pageH.click("#onetrust-accept-btn-handler")
    return pageH


def log_in():
    """Fills username and password and waits for users verification"""
    secret = vault.get_secret("credentials")
    username = secret["holviname"]
    password = secret["holviword"]

    pageH = browser.page()
    pageH.fill("#email", username)
    pageH.fill("#password", password)
    pageH.click("#submit")
    pageH.wait_for_selector("#page-loader")


def go_to_orders():
    """Navigates to order page"""
    pageH = browser.page()
    pageH.click("#sidebar-online-store")
    pageH.wait_for_selector("#sidebar-online-store-orders")
    pageH.click("#sidebar-online-store-orders")
    

def check_how_many_orders():
    """Counts how many orders are not processed"""
    pageH = browser.page()
    pageH.wait_for_load_state("domcontentloaded")
    order_amount = pageH.query_selector_all(".badge-outline-warning")
    return order_amount


def select_order(order_amount):  # amount_of_orders  
    """Selects (the last) order that is not processed"""
    pageH = browser.page()
    pageH.wait_for_load_state("domcontentloaded")
    
    if len(order_amount) > 1:
        selected_order = order_amount[-1]
        selected_order.click()
        order_amount.pop()
        check_amount_of_ordered_products()
    elif len(order_amount) == 1:
        selected_order = order_amount[0] 
        selected_order.click()
        order_amount.pop()
        check_amount_of_ordered_products()
    else:
        print("No unprocessed orders found.") #ilmoita assistantilla että kaikki on käsitelty?


def check_amount_of_ordered_products():
    """Counts the amount of products in the order.
    If there is more than one product in the order (+postage)
    informs user about it and continues to the next order"""

    pageH = browser.page()
    pageH.wait_for_load_state("domcontentloaded")

    ordered_products = pageH.query_selector_all(".text-linky")
    infos = pageH.query_selector_all(".form-control-plaintext")
    name = infos[2].text_content()
    receipt = infos[1].text_content()

    if len(ordered_products) == 2:
        copy_order_information(order_info)
    else:
        assistant.add_heading(f"Tilauksessa {name, receipt} on useampi tuote tai se on lahjakorttitilaus")
        assistant.add_text("Jätän tilauksen käsittelemättä")
        assistant.run_dialog() # valitse seuraava tilaus, lähetä spostilla tilauksen tiedot


def copy_order_information(order_info):
    """Copies the orders information"""
    pageH = browser.page()
    pageH.wait_for_load_state("domcontentloaded")

    infos = pageH.query_selector_all(".form-control-plaintext") #order and receipt nrs, name, email and number
    if len(infos) == 5:
        order_info["order_code"] = infos[0].text_content()
        order_info["receipt"] = infos[1].text_content()
        order_info["name"] = infos[2].text_content()
        order_info["email"] = infos[3].text_content()
        order_info["number"] = infos[4].text_content()
    else:                                               #ei toimi, tulee: 'number': 'Testaamotie 2 a04130 SipooSuomi KORJAA
        order_info["order_code"] = infos[0].text_content()
        order_info["receipt"] = infos[1].text_content()
        order_info["name"] = infos[2].text_content()
        order_info["email"] = infos[3].text_content()
        order_info["number"] = "0401234567"

    addresses = pageH.query_selector_all(".m-0") #address
    address_info = addresses[1].text_content() #postcode and city are on the same row
    parts = address_info.split()
    order_info["address"] = addresses[0].text_content()
    order_info["postcode"] = parts[0]
    order_info["city"] = parts[1]
    
    products = pageH.query_selector_all(".text-linky")  #ordered product  
    order_info["product"] = (products[0].text_content().replace("Kuvaus", ""))
    #Toimituskulu saattaa olla ekana -> miten tsekata asia ja reagoida siihen? -> if product == "Toimituskulu", tee jotain

    elements = pageH.query_selector_all("a.tr") #for finding products product code
    for element in elements:
        href = element.get_attribute("href")
        parts = href.split("/")
        product_code = parts[-2]
        if (product_code != "01455636f139251516278951e82ae2ec"):  # TestiToimituskulun koodi, oikea on "c50debf7d6fb2e8a3fc30cac076ac151"
            order_info["product_code"] = product_code
            break

    print(order_info)
    check_package_size(order_info)


def check_package_size(order_info):
    """Decides the needed package size based on the product that is ordered
    and chooses Posti's matching package size.
    Informs user about the package sizes."""

    # Ilmoita package userille

    find = order_info["product_code"]
    with open("Packets.csv") as file:
        for row in file:
            parts = row.strip().split(";")
            products_code = parts[0]
            package = parts[2]
            delivery = parts[3]

            if products_code == find:
                order_info["package"] = package
                order_info["delivery"] = delivery
        
        print(order_info)    
        return order_info
         


def open_posti_website():
    """Navigates to the given URL"""
    pageP = browser.context().new_page()
    pageP.goto("https://www.posti.fi/palvelutverkossa/lahettaminen/")
    pageP.click("#onetrust-accept-btn-handler")
    pageP.click(".top-bar__login-button")
    pageP.wait_for_selector("#username")
    return pageP


def log_in_to_posti(pageP):
    """Fills username and password"""
    secret = vault.get_secret("credentials")
    username = secret["postiname"]
    password = secret["postiword"]

    pageP.fill("#username", username)
    pageP.fill("#password", password)
    pageP.click("#posti_login_btn")


def fill_the_form_and_clickety_click_everything(order_info, pageP, order_amount):
    """Chooses the right package, fills the form and gives all the needed information"""
    pageP.click("text=Näytä isot pakettikoot")

    this = order_info["delivery"] #chooses the right delivery package size
    pageP.click(f"text={this}")

    pageP.get_by_text("Vastaanottajan nimi").fill(order_info["name"])
    pageP.check("#send-to-office") #Toimitus Postiin 

    pageP.get_by_text("Katuosoite").fill(order_info["address"])
    pageP.get_by_text("Postinumero").fill(order_info["postcode"])
    pageP.get_by_text("Postitoimipaikka").fill(order_info["city"])
    pageP.get_by_text("Vastaanottajan matkapuhelin").fill(order_info["number"])

    try: #tämä ei toimi
        new_contact = pageP.query_selector('input[type="radio"][name="contact-update-select"][value="save_new"]') #Tallenna kokonaan uusi kontakti
        if new_contact:
            pageP.check(new_contact)
    except:
        pass
            
    errors = pageP.query_selector('.text-input__error') #onko kaikki rivit täytetty oikeilla tiedoilla
    if not errors:
        pageP.click("button.wizard-next-prev__button:nth-child(2)") #Seuraava
    else:
        assistant.add_heading("Jokin tieto on väärin, tarkista tiedot")
        assistant.add_text("Paina Submit kun tiedot on oikein") #tänne robolle ohje odottaa, että submit on painettu
        assistant.add_submit_buttons("Submit", default="Submit")
        assistant.run_dialog()

    # Tarvitsetko lisäpalveluja?
    pageP.click("button.wizard-next-prev__button:nth-child(2)") #Seuraava

    #Onhan tiedot oikein? #Lähetykset(määrä)
    
    if len(order_amount) != 0:
        pageP.click(".add-new-parcel__button")
        pageH = browser.page()
        pageH.bring_to_front()  # takaisin Holviin
        go_to_orders()
        select_order(order_amount)
        check_amount_of_ordered_products()
        fill_the_form_and_clickety_click_everything(order_info, pageP, order_amount)
                #takaisin Holviin, seuraava tilaus  
    else:    #sarjakoodi tulisi syöttää tässä vaiheessa
        assistant.add_heading("Haluatko käyttää sarjapaketti- tai alennuskoodin?")
        assistant.add_submit_buttons("Submit", default="Submit") #kyllä tai ei
        #jos ei 
            #pageP.click("button.wizard-next-prev__button:nth-child(2)") #Seuraava
        #jos kyllä / If sarjakoodi:
        assistant.add_text("Syötä koodi: ") #tee tästä input
        assistant.add_submit_buttons("Submit", default="Submit") #robo siirtää koodin postin sivulle
            #   page.fill("#input-field-36", sarjakoodi)
            #   page.click(".summary__discount-code__form-submit-button")  vai   (".themed-button--text-only > span:nth-child(2)") #mitä täällä tapahtuu???
            #pageP.click("button.wizard-next-prev__button:nth-child(2)") #Seuraava
        assistant.run_dialog()

    # Syötä omat tiedot
    # tulee automaattisesti -> robo tsekkaa, että on. Jos ei ole, robo ilmoittaa asiasta
    errors = pageP.query_selector('.text-input__error') #onko kaikki rivit täytetty oikeilla tiedoilla
    if not errors:
        pageP.click("button.wizard-next-prev__button:nth-child(2)") #Seuraava
    else:
        assistant.add_heading("Jokin tieto on väärin, tarkista tiedot")
        assistant.add_text("Paina Submit kun tiedot on oikein") #tänne robolle ohje odottaa, että submit on painettu
        assistant.add_submit_buttons("Submit", default="Submit")
        assistant.run_dialog()

    pageP.click("button.wizard-next-prev__button:nth-child(2)") #Seuraava

    # Valitse maksutapa
    assistant.add_heading("Voit nyt maksaa postimaksut")
    assistant.add_text("Paina Submit kun maksu on suoritettu")
    assistant.add_submit_buttons("Submit", default="Submit")
    assistant.run_dialog()

    # page.wait_for_selector("button.wizard-next-prev__button:nth-child(2)") #"Maksa (€)"


def wait_for_payment():
    """Waits for the user to pay to Posti"""
    pass


def mark_order_as_done(pageH):
    """Marks the order as processed in on at Holvi orders-page"""

    pageH.bring_to_front()  # takaisin Holviin

    # merkkaa tilaus/tilaukset käsitellyksi

    pass

