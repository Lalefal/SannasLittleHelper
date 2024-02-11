# Mailing assistant robot

This is a school project for Robotic Process Automation course: Mailing Assistant Robot for my friend [Sanna Hellikki's](https://holvi.com/shop/sannahellikkiturunen/) online store to process the orders. [Process Definition in pictures](https://github.com/Lalefal/SannasLittleHelper-Robot/blob/main/ToimintaprosessinKuvaus.pdf).


![Blank board2](https://github.com/Lalefal/SannasLittleHelper-Robot/assets/94318146/ce8d75fc-8f1d-494b-9d1f-bb4c1dae52b4) 

Robot 
- logs in to Holvi and to Posti pages
- checks the amount of unprocessed orders at Holvi
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

There is still many things to add and fix (Sanna decided to move her store to another platform...)
  - Adding some classes and all the other things I have learned after doing this
  - Robot to send an email about processed and unprocessed orders
  - How to exit from the loop 'select next order' if the last order to process doesn't fill the conditions to process the order
  - Robot should ask from the user about the serial code even though the last order it processed was a Plus-size-delivery
  - Handling the users serial code input
  - Check that everything works without the slowmo-configuration
  - installation guide
  




Robot is made with Robocorps Minimal Template and it works from Robocorp Control Room as an Assistant.
Many thanks to Robocorp and to ReMark <3
