from robocorp.tasks import task
from robocorp import browser
from RPA.Robocloud.Secrets import Secrets
from robocorp import vault
from RPA.Assistant import Assistant


assistant = Assistant()
order_info = {}
unprocessed_orders = []
processed_orders = []
last_processed_order_index = None
order_amount = None
pageP = None
pageH = None

@task
def fill_package_mailing_forms():
    """Chooses the right package size for each order,
    first at Holvi's webpage, then at Posti's.
    Copies orderers contact information from Holvi
    and fills Posti's mailing form.
    At some day, it might also  handle the payment..."""
    browser.configure(
        slowmo=400,
    )
    open_posti_website()
    log_in_to_posti()
    
    open_holvi_website()
    log_in_to_Holvi()
    go_to_orders()
    orders = check_how_many_orders() #order_amount
    select_order(orders)
   # check_amount_of_ordered_products() 
   # if == 2 and country == "Suomi": 
   #    copy_order_information(order_info)  
   # else:
   #    pass_the_order(name, receipt)
   #    go_to_next_order() 
   #    -> check_amount_of_ordered_products() 
   # check_package_size(order_info)
    #fill_the_form(order_info)
    #and_clickety_click_everything()
    #Lähetätkö monta pakettia?
    # if len(order_amount) != 0
        # go_to_next_order(order_amount)
    #Haluatko käyttää sarjapaketti- tai alennuskoodin?
    #Syöttää käyttäjän tiedot
    #wait_for_payment(pageP)
    # Käyttäjä valitsee maksutavan ja hoitaa maksun
    # mark_order_as_done()
    
def pass_the_order(name, receipt):
    assistant.add_heading(f"Tilauksessa {name, receipt} on useampi tuote, se on lahjakorttitilaus tai tilattu ulkomaille.")
    assistant.add_text("Jätän tilauksen käsittelemättä")
    assistant.add_submit_buttons(buttons="Ok", default="Ok")
    assistant.run_dialog()                  #tallenna jonnekin nämä tiedot
        
def check_for_errors():
    """Checks that the Postis forms are filled correctly"""
    errors = pageP.query_selector('.text-input__error')
    if not errors:
        pageP.click("button.wizard-next-prev__button:nth-child(2)") #Seuraava (lisäpalvelut)
    else:
        assistant.add_heading("Jokin tieto on väärin, tarkista tiedot")
        assistant.add_text("Paina Ok kun tiedot on oikein")
        assistant.add_submit_buttons(buttons="Ok", default="Ok")
        assistant.run_dialog()
        
def serial_package_code():
    assistant.add_heading("Haluatko käyttää sarjapaketti- tai alennuskoodin?")
    assistant.add_heading("Valitse 'En', koska sarjakoodin käsittelyosuus ei ole vielä valmis.")
    assistant.add_submit_buttons(buttons="En, Haluan", default="Haluan")
    result = assistant.run_dialog()
    if result.submit == "Haluan":
        assistant.add_text_input("Sarjakoodi", label="Sarjakoodi", placeholder="Syötä koodi: ")
        assistant.add_submit_buttons("Ok", default="Ok")
            #robo siirtää koodin postin sivulle
            #   page.fill("#input-field-36", sarjakoodi)
            #   page.click(".summary__discount-code__form-submit-button")  vai   (".themed-button--text-only > span:nth-child(2)") #mitä täällä tapahtuu???
            # pageP.click("button.wizard-next-prev__button:nth-child(2)") #Seuraava -> Syötä omat tiedot

    else:
        pageP.click("button.wizard-next-prev__button:nth-child(2)") #Seuraava -> Syötä omat tiedot
        
def open_posti_website():
    """Navigates to the given URL"""
    global pageP
    browser.goto("https://www.posti.fi/palvelutverkossa/lahettaminen/")
    pageP = browser.page()
    pageP.click("#onetrust-accept-btn-handler")
    pageP.click(".top-bar__login-button")
    pageP.wait_for_selector("#username")


def log_in_to_posti():
    """Fills username and password"""
    secret = vault.get_secret("credentials")
    username = secret["postiname"]
    password = secret["postiword"]
    pageP = browser.page()
    pageP.fill("#username", username)
    pageP.fill("#password", password)
    pageP.click("#posti_login_btn")
    

def open_holvi_website():
    """Navigates to the given URL"""
    global pageH
    pageH = browser.context().new_page()
    pageH.goto("https://login.app.holvi.com/")
    pageH.click("#onetrust-accept-btn-handler")


def log_in_to_Holvi():
    """Fills username and password and waits for users verification"""
    secret = vault.get_secret("credentials")
    username = secret["holviname"]
    password = secret["holviword"]

    pageH.fill("#email", username)
    pageH.fill("#password", password)
    pageH.click("#submit")
    pageH.wait_for_selector("#page-loader")


def go_to_orders():
    """Navigates to order page"""
    pageH.click("#sidebar-online-store")
    pageH.wait_for_selector("#sidebar-online-store-orders")
    pageH.click("#sidebar-online-store-orders")
    pageH.wait_for_load_state("domcontentloaded")
    

def check_how_many_orders():
    """Counts how many orders are not processed"""
    global last_processed_order_index
    pageH.wait_for_load_state("domcontentloaded")
    pageH.wait_for_selector(".badge-outline-warning")
    orders = pageH.query_selector_all(".badge-outline-warning")
    
    print(len(orders))
    return orders


def select_order(orders):  # amount_of_orders  
    """Selects (the last) order that is not processed"""
    global last_processed_order_index, order_amount
    if last_processed_order_index is None:
        last_processed_order_index = len(orders) - 1
        order_amount = len(orders)
    else:
        last_processed_order_index -= 1
    if last_processed_order_index >= 0:
        selected_order = orders[last_processed_order_index]
        selected_order.click()
        order_amount -= 1
        check_amount_of_ordered_products()   

    else:
        print("No unprocessed orders found.") #ilmoita assistantilla että kaikki on käsitelty?
        print(len(orders), order_amount)
        assistant.add_heading("En löydä tilauksia")
        assistant.add_submit_buttons(buttons="Ok", default="Ok")
        assistant.run_dialog() 
        
        
def go_to_next_order():
    pageH.click("#sidebar-online-store")
    pageH.wait_for_selector("#sidebar-online-store-orders")
    pageH.click("#sidebar-online-store-orders")
    pageH.wait_for_selector(".badge-outline-warning")
    orders = check_how_many_orders()
    if order_amount > 0:
        print(order_amount)
        select_order(orders)
    else:
        print(order_amount)
        assistant.add_heading("En löydä tilauksia")
        assistant.add_submit_buttons(buttons="Ok", default="Ok")
        assistant.run_dialog()    
        

def check_amount_of_ordered_products():
    """Counts the amount of products in the order.
    If there is more than one product in the order (+postage)
    or the orderers country is not Suomi
    informs user about it and continues to the next order"""
    pageH.wait_for_load_state("domcontentloaded")

    ordered_products = pageH.query_selector_all(".text-linky")
    addresses = pageH.query_selector_all(".m-0")
    country = addresses[2].text_content()
    
    infos = pageH.query_selector_all(".form-control-plaintext")
    name = infos[2].text_content()
    receipt = infos[1].text_content()

    if len(ordered_products) == 2 and country == "Suomi":
        copy_order_information(order_info)
    else:
        unprocessed_orders.append(receipt)
        print(name, receipt)
        pass_the_order(name, receipt)
        go_to_next_order()


def copy_order_information(order_info):
    """Copies the orders information"""
    pageH.wait_for_load_state("domcontentloaded")

    infos = pageH.query_selector_all(".form-control-plaintext") #order and receipt nrs, name, email and number
    if len(infos) == 6:
        order_info["order_code"] = infos[0].text_content()
        order_info["receipt"] = infos[1].text_content()
        order_info["name"] = infos[2].text_content()
        order_info["email"] = infos[3].text_content()
        order_info["number"] = infos[4].text_content()
    else:                       
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
    if order_info["product"] == "Toimituskulu":
        order_info["product"] = (products[1].text_content().replace("Kuvaus", ""))

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


def check_package_size(order_info,):
    """Decides the needed package size based on the product that is ordered."""
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
        processed_orders.append(order_info.copy())
        fill_the_form(order_info)   
        

def fill_the_form(order_info):
    """Chooses the right delivery package and option, fills the form"""
    global pageP
    pageP.bring_to_front()
    try:
        pageP.click("text=Näytä isot pakettikoot")
    except:
        pass
    
    this = order_info["delivery"] #chooses the right delivery package size
    pageP.click(f"text={this}")
    if this == "Pikkupaketti-lähetys": #seuraava sivu on Onhan tiedot oikein?
        pageP.get_by_text("Vastaanottajan nimi").fill(order_info["name"])
        pageP.get_by_text("Katuosoite").fill(order_info["address"])
        pageP.get_by_text("Postinumero").fill(order_info["postcode"])
        pageP.get_by_text("Postitoimipaikka").fill(order_info["city"])
        pageP.get_by_text("Vastaanottajan matkapuhelin").fill(order_info["number"])

        check_for_errors() #siirtyy sivulle Onhan tiedot oikein

    if this != "Pikkupaketti-lähetys": # seuraava sivu on Tarvitsetko lisäpalveluja?
        pageP.get_by_text("Vastaanottajan nimi").fill(order_info["name"])
        pageP.check("#send-to-office") #Toimitus Postiin 

        pageP.get_by_text("Katuosoite").fill(order_info["address"])
        pageP.get_by_text("Postinumero").fill(order_info["postcode"])
        pageP.get_by_text("Postitoimipaikka").fill(order_info["city"])
        pageP.get_by_text("Vastaanottajan matkapuhelin").fill(order_info["number"])
        try:                                                  
            new_contact = pageP.query_selector('input[type="radio"][name="contact-update-select"][value="save_new"]') #Tallenna kokonaan uusi kontakti
            if new_contact:
                pageP.check('input[type="radio"][name="contact-update-select"][value="save_new"]')
        except:
            pass
        
        check_for_errors()    #siirtyy sivulle Tarvitsetko lisäpalveluja?
        pageP.click("button.wizard-next-prev__button:nth-child(2)") #Siirtyy sivulle Onhan tiedot oikein
        and_clickety_click_everything()
    
    
def and_clickety_click_everything():
    """Chooses if there are many packages to send
    Asks if the user wants to use serial packet or discount code
    Checks that the 'Senders information' form is filled correctly"""
    if order_amount > 0:
        pageP.click(".add-new-parcel__button") #Lisää uusi lähetys
        pageH.bring_to_front()  
        go_to_next_order() #takaisin Holviin, seuraava tilaus  
            
#tämä kohta ei toimi, jos viimeinen tsekattava tilaus ei täytä ehtoja
#copy_order_information(order_info, orders)
        #käy ensin katsomassa, onko käsiteltävää tilausta
        #ja sitten päätä, mitä tehdä....
    else:   #Haluatko käyttää sarjapaketti- tai alennuskoodin?
        #tämä taitaa tsekata vain yhden. Mitä jos ensin on mennyt ei-Plus-paketti
        #ja paketti jonka jälkeen tämä tulisi kysyä, onkin 
        if order_info["delivery"] not in ["M-Plus-Paketti", "S-Plus-paketti"]:
            serial_package_code() # Siirtyy sivulle Syötä omat tiedot                
        check_for_errors() # Syötä omat tiedot: tulee automaattisesti #if not: Siirtyy sivulle Valitse maksutapa
        wait_for_payment()


def wait_for_payment():
    """Waits for the user to pay to Posti""" #Sivulla Valitse maksutapa
    assistant.add_heading("Voit nyt maksaa postimaksut")
    assistant.add_text("Paina ok kun maksu on suoritettu")
    assistant.add_submit_buttons("ok", default="ok")
    assistant.run_dialog()
    mark_order_as_done()
    # page.wait_for_selector("button.wizard-next-prev__button:nth-child(2)") #"Maksa (€)"


def mark_order_as_done():
    """Marks the order as processed in on at Holvi orders-page"""
    global pageH
    pageH.bring_to_front()  # takaisin Holviin
    #tilaukset sivulle
    tell = []
    #valitse tilaus order id:n perusteella
    for order_info in processed_orders:
        pageH.click("#sidebar-online-store")
        pageH.wait_for_selector("#sidebar-online-store-orders")
        pageH.click("#sidebar-online-store-orders")
        pageH.wait_for_selector(".badge-outline-warning")    
        
        this = order_info["order_code"]
        link_selector = f'a[href$="{this}/"]'
        pageH.click(link_selector)
        pageH.click("#dropdownOderOptions")
        pageH.wait_for_selector("#order-mark-as-processed-btn")
        pageH.click("#order-mark-as-processed-btn")
        these = order_info["receipt"]
        tell.append(these)    

    assistant.add_heading("Oletko tyytyväinen?")
    assistant.add_text(f"Käsitellyt tilaukset: {tell}")
    assistant.add_submit_buttons("Kyllä", default="Kyllä")
    assistant.run_dialog()
    

