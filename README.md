# Mailing assistant robot

This is a school project for Robotic Process Automation course: Mailing Assistant Robot for my friend [Sanna Hellikki's](https://holvi.com/shop/sannahellikkiturunen/) online store to process the orders.

Robot 
- checks the amount of unprocessed orders
- chooses the last unprocessed order
- checks how many items are on the order and to which country it is ordered to
  - if one product + delivery fee and to Finland:
     - chooses the right package size (to which to wrap the ordered product)
     - chooses the right delivery size (to what to pay to Posti)
     - fills the customers contact information Posti's form (as many times as there is unprocessed orders)
     - checks for errors in Posti's forms and informs the user to correct the errors
  - else:
     - informs the user that the order won't be processed
     - goes to the next unprocessed order
- asks if the user wants to use serial or discount code for paying the delivery
- informs the user when it is time to pay for the delivery and waits until it is done
- marks the processed orders as processed

There is still many things to add and fix
  - Robot to send an email about processed and unprocessed orders
  - How to exit from the loop 'select next order' if the last order to process doesn't fill the conditions to process the order
  - Robot should ask from the user about the serial code even though the last order it processed was a Plus-size-delivery
  - Handling the users serial code input
  - Check that everything works without the slowmo-configuration (Scary!)
  - Adding some classes...


Robot is made with Minimal Template and it works from Control Room as an Assistant.

Many thanks to Robocorp and to ReMark <3

![image](https://github.com/Lalefal/SannasLittleHelper/assets/94318146/ffb77c0b-33f9-4bd1-a778-dbaecd1ce487)


# Template: Python - Minimal

This template leverages the new Python open-source structure [robo](https://github.com/robocorp/robo), the [libraries](https://github.com/robocorp/robo#libraries) from to same project as well.
The full power of [rpaframework](https://github.com/robocorp/rpaframework) is also available for you on Python as a backup while we implement new Python libraries.

The template provides you with the basic structure of a Python project: logging out of the box and controlling your tasks without fiddling with the base Python stuff. The environment contains the most used libraries, so you do not have to start thinking about those right away. 

👉 After running the bot, check out the `log.html` under the `output` -folder.

The template here is essentially empty, leaving you with a canvas to paint on.

Do note that with Robocorp tooling you:
- Do NOT need Python installed
- Should NOT be writing `pip install..`; the [conda.yaml](https://github.com/robocorp/template-python/blob/master/conda.yaml) is here for a reason.
- You do not need to worry about Python's main -functions and, most importantly, the logging setup

🚀 Now, go get'em

For more information, do not forget to check out the following:
* [Robocorp Documentation -site](https://robocorp.com/docs)
* [Portal for more examples](https://robocorp.com/portal)
* [robo repo](https://github.com/robocorp/robo) as this will developed a lot...
