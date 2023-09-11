# -*- coding: utf-8 -*-
# -*- coding: iso-8859-1 -*-

import appdaemon.plugins.hass.hassapi as hass
import datetime
import cups
from PIL import Image
import zpl


class zebraControl(hass.Hass):
 
  def initialize(self): 
    self.listen_state(self.createZPL,"input_button.create_batch_label")

    cups.setServer(self.get_state("input_text.cups_server"))
    cups.setPort(int(float(self.get_state("input_number.cups_port"))))
    printer_list = []

    self.conn = cups.Connection()
    printers = self.conn.getPrinters()
    for printer_id, printer in printers.items():
      printer_list.append(
      printer_id
      )
    self.log(printer_list)
      
    self.call_service("input_select/set_options", entity_id="input_select.cups_printer",
            options= printer_list)

    self.log("initialized")
  def createZPL(self, entity, attribute, old, new, kwargs):
      self.log("Create ZPL")
      f = open("/config/appdaemon/apps/label.tmp", "w")
      queue = self.get_state("input_select.cups_printer")
      self.log(queue)

      l = zpl.Label(51,25)
      height = 1
      l.origin(0,1)
      l.write_text(self.get_state("input_select.stored_cheese").replace("Lager ", "") + " | " + self.get_state("input_select.cheese_variations"), char_height=3, char_width=2, line_width=55, justification='L')
      l.endorigin()
      l.origin(0,5)
      l.write_text("M: " + self.get_state("input_datetime.ystningsdatum").replace("-", "")+ " P: " + self.get_state("input_datetime.packing_date").replace("-", ""), char_height=2, char_width=2, line_width=55, justification='L')
      l.endorigin()
      l.origin(0,7)
      l.write_text("S: " + self.get_state("input_datetime.selling_date").replace("-", ""), char_height=2, char_width=2, line_width=55, justification='L')
      l.endorigin()
      l.origin(11,8)

      l.write_text("Weight: " + self.get_state("input_number.cheese_weight") , char_height=2, char_width=2, line_width=55, justification='L')
      l.endorigin()
      l.origin(0, 8)
      l.barcode('Q', self.get_state("input_text.permalink"), magnification=2)
      l.endorigin()

      label = bytes(l.dumpZPL(), 'utf-8')
      
      self.log(label)
      f.write(str(label))
      f.close()
      cups.setServer(self.get_state("input_text.cups_server"))
      cups.setPort(int(float(self.get_state("input_number.cups_port"))))
      conn = cups.Connection()
      job = conn.printFile (queue, "/config/appdaemon/apps/label.tmp", "", {})
      self.call_service("input_text/set_value", entity_id="input_text.status", value=job)



