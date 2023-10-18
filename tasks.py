from robocorp.tasks import task
from robocorp import browser
from RPA.Robocloud.Secrets import Secrets
from robocorp import vault
from RPA.Assistant import Assistant
import re


@task
def fill_package_mailing_forms():
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
    order_info = {}
    open_holvi_website()
    log_in()
    go_to_orders()
    select_order()
    #copy_contact_information(order_info)
    order_info = copy_order_information(order_info)
    
    # open_posti_website()
    # log_in_to_posti()
    # fill_the_form_and_clickety_click_everything(order_info)
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
    """
    Input username and password
    Wait for users verification
    """
    browser.goto("https://login.app.holvi.com/")
    page = browser.page()
    page.click("#onetrust-accept-btn-handler")


def log_in():
    secret = vault.get_secret("credentials")
    username = secret["holviname"]
    password = secret["holviword"]

    page = browser.page()
    page.fill("#email", username)
    page.fill("#password", password)
    page.click("#submit")
    page.wait_for_selector("#page-loader")


def go_to_orders():
    page = browser.page()
    page.click("#sidebar-online-store")
    page.wait_for_selector("#sidebar-online-store-orders")
    page.click("#sidebar-online-store-orders")
    
    #Nämäkin toimii:
    # page.get_by_role("menuitem", name="Verkkokauppa").click()
    # page.get_by_role("menuitem", name="Kauppa Tilaukset").click()



# def check_how_many_orders():
    # tsekkaa koko lista läpi, montako "käsitelty" not True

    #    order = page.get_by_role("listitem").filter(has_not_text="Processed") VAI has_not_text="Käsitelty"
    #    orders = order.count()
    #   order =page.get_by_role("listitem").filter(has_text="Pending")

    # amount_of_orders = 0
    # == "Käsitelty" / True
    # kaikki ok
    # else: orders += 1
    # return amount_of_orders

    """
    <div class="badge badge-pill badge-outline-warning" ng-if="!order.isProcessed()" translate>Pending</div>
    <div class="badge badge-pill badge-success" ng-if="order.isProcessed()" translate>Processed</div>

# element:  <div class="badge badge-pill badge-success" ng-if="order.isProcessed()" translate=""><span>Käsitelty</span></div>
# selector: #order-list-items > li:nth-child(1) > order-list-item > a > div.tr-right > div > div > div
    
    
    , function(e, t) {
    var n = "scripts/appvault/account/store/orders/order-list-item.ng.html";
    window.angular.module("app.templates").run(["$templateCache", function(e) {
        e.put(n, '<!DOCTYPE html><a class="tr empty" ui-sref="app.account.store.orders.detail({ code: order.id })"><div class="tr-center" data-hj-suppress><div class="tr-top"><div class="td td-main"><div>{{ order.get(\'events\')[0].content }}</div><div>{{ created | date:\'short\' }}</div></div></div><div class="tr-middle"><div class="td td-xxl"><div>{{ \'Buyer\' | translate }}: {{ fullname }}</div><div ng-if="sequence_number"><span class="sr-only">{{ \'Receipt number\' | translate }}:</span><span>{{ ::sequence_number }}</span></div></div></div></div><div class="tr-right"><div class="tr-top"><div class="td ml-auto td-xl text-right"><div class="badge badge-pill badge-outline-warning" ng-if="!order.isProcessed()" translate>Pending</div><div class="badge badge-pill badge-success" ng-if="order.isProcessed()" translate>Processed</div></div></div></div></a>')
    }
    ]),
    e.exports = n
}
    """



# #order-list-items

# selector: #order-list-items > li:nth-child(1)
# selector: #order-list-items > li:nth-child(3)


def select_order():  # amount_of_orders   #Tee ensin yhdellä tilauksella
    """
    Selects order that is not processed
    """

    page = browser.page()
    

    
    #page.get_by_role("link", name=).click()
    
    #page.get_by_role("link").filter(has_not_text="Käsitelty").click
  
    #page.wait_for_load_state("domcontentloaded")
    #page.get_by_role("listitem").filter(has_text="Processed").click
    #page.get_by_role("listitem").filter(has_not_text="Processed").click

    # order = page.get_by_role("listitem").filter(has_not_text="Processed").click
    # orders = order.count()
    # page.content

    # page.get_by_text("Pending").click()
    # page.get_by_role("listitem").filter(has_text="Pending").click
    # page.get_by_role("listitem").filter(has_not_text="Processed").click


def check_amount_of_ordered_products():
    page = browser.page()
    ordered_products = page.query_selector_all(".text-linky")
    
    infos = page.query_selector_all(".form-control-plaintext")
    name = infos[2].text_content()
    receipt = infos[1].text_content()
    
    if len(ordered_products) == 2:
        #copy_order_information(order_info={})
        order_info = copy_order_information(order_info)
    else:
        assistant = Assistant()
        assistant.add_heading(f"Tilauksessa {name, receipt} on useampi tuote")
        assistant.add_text("Jätän tilauksen käsittelemättä")
        assistant.run_dialog()
        #valitse seuraava tilaus, lähetä spostilla tilauksen tiedot



def copy_order_information(order_info):   
    page = browser.page()
    
    infos = page.query_selector_all(".form-control-plaintext")
    addresses = page.query_selector_all(".m-0")
    products = page.query_selector_all(".text-linky")

    order_info["order_code"] = infos[0].text_content()
    order_info["receipt"] = infos[1].text_content()
    order_info["name"] = infos[2].text_content()
    order_info["email"] = infos[3].text_content()
    order_info["number"] = infos[4].text_content()
        
    order_info["address"] = addresses[0].text_content()
    order_info["postcode"] = addresses[1].text_content()
    order_info["city"] = addresses[2].text_content()
    
    order_info["product"] = products[0].text_content() #'KuvausTalvipuutarha - Winter Garden'
    order_info["product."] = products[0].inner_text()  #'''Kuvaus\nTalvipuutarha - Winter Garden'''
    
    
    return order_info
    





def check_package_size():
    
    #product = order_info["product"]
    #SannasPackets =  {"putkiS": [x, y, z], "putkiM" : [l, m, n], "kuori" : [a, b, c]}
    #for pakettikoot, tuotteet in SannasPacket.items():
        #tsekkaa mistä löytyy product
    
    # keksi, miten listata koot?!
    # product, package, packagesize
    # if product == y, then package == x and packagesize == x

    # Ilmoita package userille
    # return packagesize
    pass



def open_posti_website():
    browser.goto("https://www.posti.fi/palvelutverkossa/lahettaminen/")

    page = browser.page()
    page.click("#onetrust-accept-btn-handler")
    page.click(".top-bar__login-button")
    # page.get_by_text("Kirjaudu sisään").click

    page.wait_for_selector("#username")


def log_in_to_posti():
    secret = vault.get_secret("credentials")
    username = secret["postiname"]
    password = secret["postiword"]

    page = browser.page()
    page.fill("#username", username)
    page.fill("#password", password)
    page.click("#posti_login_btn")


def fill_the_form_and_clickety_click_everything(order_info):
    page = browser.page()
    
    #valitse paketin koko check_package_size() mukaisesti
    
    """
    pikkupaketti        has_text("Pikkupaketti-lähetys) 
    div.size-selection__parcel-size-list__item-outer-container:nth-child(1)
    
    has_text("S-paketti"
    div.size-selection__parcel-size-list__item-outer-container:nth-child(2)
    
    has_text("M-paketti"
    div.size-selection__parcel-size-list__item-outer-container:nth-child(3)
    
    has_text("L-paketti"
    div.size-selection__parcel-size-list__item-outer-container:nth-child(4)
    
    has_text("XL-paketti"
    div.size-selection__parcel-size-list__item-outer-container:nth-child(5)
    
    "Näytä isot pakettikoot"
    .show-all-button
    
    has_text(S-Plus-paketti
    div.size-selection__parcel-size-list__item-outer-container:nth-child(6)
    
    has_text(M-Plus-paketti
    div.size-selection__parcel-size-list__item-outer-container:nth-child(7)
    
    has_text(L-Plus-paketti
    div.size-selection__parcel-size-list__item-outer-container:nth-child(8)
    """
    
    #valitsee S-paketin:
    page.click(
        "div.size-selection__parcel-size-list__item-outer-container:nth-child(2)"
    )  
    # page.click("button:text('Seuraava')")

    page.get_by_text("Vastaanottajan nimi").fill(order_info["name"])
    page.check("#send-to-office")

    page.get_by_text("Katuosoite").fill(order_info["address"])
    page.get_by_text("Postinumero").fill(order_info["postcode"])
    page.get_by_text("Postitoimipaikka").fill(order_info["city"])
    page.get_by_text("Vastaanottajan matkapuhelin").fill(order_info["number"])

    # page.check("") "Tallenna kokonaan uusi kontakti"
    page.click("button.wizard-next-prev__button:nth-child(2)")

    # Tarvitsetko lisäpalveluja?
    page.click("button.wizard-next-prev__button:nth-child(2)")

    # Onhan tiedot oikein?
    # If useampi paketti: page.click(".add-new-parcel__button")
    # If sarjakoodi:
    #   page.fill("#input-field-36", sarjakoodi)
    #   page.click(".summary__discount-code__form-submit-button")  vai   (".themed-button--text-only > span:nth-child(2)")
    # else:
    page.click("button.wizard-next-prev__button:nth-child(2)")

    # Syötä omat tiedot
    # tulee automaattisesti -> robo tsekkaa, että on. Jos ei ole, robo täyttää

    page.click("button.wizard-next-prev__button:nth-child(2)")

    assistant = Assistant()
    assistant.add_heading("Voit nyt maksaa postimaksut")
    assistant.add_text("Paina Submit kun maksu on suoritettu")
    assistant.add_submit_buttons("Submit", default="Submit")
    assistant.run_dialog()

    # page.wait_for_selector("button.wizard-next-prev__button:nth-child(2)") #"Maksa (€)"


def wait_for_payment():
    pass
    """
    Waits for the user to pay for Posti
    """



def mark_order_as_done():
    # takaisin Holviin
    # merkkaa tilaus käsitellyksi

    pass

    # amount_of_orders -=1


# def  check if more orders, start again

