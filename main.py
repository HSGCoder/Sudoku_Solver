"""
This project solves the weekly sudoku challenge from Tagesanzeiger.ch


Author: Jonathan Vontobel (15-604-853), Vasily Taran (20-624-987) and Péter Liszkai (20-624-730)
"""
from selenium import webdriver
from time import sleep
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from subprocess import check_output
import json
import requests
from browsermobproxy import Server
import base64
import brotli
import selenium
import solver
from pynput.keyboard import Key, Controller
import datetime
import warnings
import browser_cookie3
from selenium.webdriver.chrome.options import Options as COptions

#ignore warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

sudoku = [[0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0]]

def list_to_int(numList):
    s = ''.join(map(str, numList))
    return int(s)

def expand_shadow_element(element):
  shadow_root = driver.execute_script('return arguments[0].shadowRoot.children', element)
  return shadow_root

def get_url():
  """
  This function returns the current url uf the sudoku challenge.
  The is of the form: https://tagesanzeiger.raetsel.ch/sudoku-kwNUM where NUM is the current calender week
  """
  week = datetime.datetime.utcnow().isocalendar()[1]
  if int(week) < 10:
    week = "0" + week
  url = "https://tagesanzeiger.raetsel.ch/sudoku-kw{}".format(week)
  print("URL is: {}".format(url))
  return url

def get_browser_and_proxy():
  """
  This function returns a firefox slenium driver with a proxy in order to catch the data traffic.
  The proxy is needed because the sudoku data is not loaded in the website immediately, but after a GET request to the server.
  """

  #start proxy server to read out data traffic
  server = Server(r"browsermob\bin\browsermob-proxy")
  server.start()
  proxy = server.create_proxy()
  proxy.new_har("file_name", options={'captureHeaders': True, 'captureContent': True, 'captureBinaryContent': True})

  #init of selenium Firefox browser with above proxy
  options = Options()
  options.add_argument("--headless")
  profile  = webdriver.FirefoxProfile()
  profile.set_proxy(proxy.selenium_proxy())
  driver = webdriver.Firefox(firefox_profile=profile, options=options, executable_path=r'geckodriver.exe')

  return driver, proxy, server

def get_sudoku_data(log):
  """
  This function reads the json file where the sudoku data is stored in
  """
  _url = ""
  for ent in log:
    _url = ent['request']['url']
    _response = ent['response']
    if not 'text' in ent['response']['content']:
      continue
    data = _response['content']['text']
    if(_url.startswith("https://api.raetsel.ateleris.com/api")):
      data = base64.b64decode(data)
      data = brotli.decompress(data)
      data = data.decode('utf-8')
      r = json.loads(data)
  for hint in r["description"]['hints']:
    row = hint['row'] - 1
    col = hint['column'] - 1
    num = hint['number']
    sudoku[row][col] = num
  return r

def get_winning_fields(r):
  """
  This function returns the fields which are needed for formula in order to win
  """
  fields = []
  for field in r["description"]['prizeFields']:
    row = field['row']
    col = field['column']
    fields.append(sudoku[row - 1][col - 1])
  return fields

def fill_out_winning_formula(fields):
  """
  This function open the selenium firefox browser and fills out the formula to participate for the prize
  The captcha can not be filled out, this step has to be done manually
  Date of Birth has also be filled out manually
  """
  driver = webdriver.Firefox()
  driver.get("https://www.share-solution.ch/tagi/sudoku")
  driver.refresh()
  driver.find_element_by_css_selector("input[id='form_field_solution']").send_keys("{}".format(list_to_int(fields)))
  driver.find_element_by_css_selector("input[id='form_field_firstName']").send_keys("Max")
  driver.find_element_by_css_selector("input[id='form_field_lastName']").send_keys("Muster")
  driver.find_element_by_css_selector("input[id='form_field_street']").send_keys("Musterstrasse")
  driver.find_element_by_css_selector("input[id='form_field_postalCode']").send_keys("8006")
  driver.find_element_by_css_selector("input[id='form_field_city']").send_keys("Zürich")
  driver.find_element_by_css_selector("input[id='form_field_phone']").send_keys("000000000000")
  driver.find_element_by_css_selector("input[id='form_field_email']").send_keys("example@mail.com")
  driver.find_element_by_css_selector("div[class='input-group focus']").click()

"""
A Proxy is needed since the json file in which the sudoku is saved is not loaded immediately with the website. 
Thus we need to inspect the network traffic to catch the JSON file.
"""
driver, proxy, server = get_browser_and_proxy()
driver.get(get_url())
proxy.wait_for_traffic_to_stop(1000, 10000)
log = proxy.har['log']['entries']
r = get_sudoku_data(log)

solver.solve_sudoku(sudoku)
solver.print_sudoku(sudoku)

fields = get_winning_fields(r)
print("Winning fields are: {}".format(list_to_int(fields)))
fill_out_winning_formula(fields)

server.stop()
proxy.close()
driver.close()







