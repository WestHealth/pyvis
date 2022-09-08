import os
import unittest

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from ..network import Network


class GraphTests(unittest.TestCase):
    service = ChromeService(executable_path=ChromeDriverManager().install())

    def setUp(self):
        self.g = Network()

    def test_graph(self):
        self.g.add_nodes([1, 2, 3],
                         value=[10, 100, 400],
                         title=["I am node 1", "node 2 here", "and im node 3"],
                         x=[21.4, 21.4, 21.4], y=[100.2, 223.54, 32.1],
                         label=["NODE 1", "NODE 2", "NODE 3"],
                         color=["#00ff1e", "#162347", "#dd4b39"])
        file_name = "GraphTests.html"
        self.g.show(file_name)

        file_path = os.getcwd()
        file_path = "file:///" + file_path.replace(os.sep, '/') + "/" + file_name

        driver = webdriver.Chrome(service=self.service)
        driver.get(file_path)
        driver.implicitly_wait(0.1)

        self.assertIsNotNone(driver.find_element(By.ID, "mynetwork"))
        self.assertIsNotNone(driver.find_element(By.TAG_NAME, "canvas"))

        self.assertFalse(driver.find_elements(By.ID, "select-menu"))
        self.assertFalse(driver.find_elements(By.ID, "filter-menu"))

        driver.quit()
        os.remove("./"+file_name)


class SelectMenuTests(unittest.TestCase):
    service = ChromeService(executable_path=ChromeDriverManager().install())

    def setUp(self):
        self.g = Network(select_menu=True)

    def test_graph(self):
        self.g.add_nodes([1, 2, 3],
                         value=[10, 100, 400],
                         title=["I am node 1", "node 2 here", "and im node 3"],
                         x=[21.4, 21.4, 21.4], y=[100.2, 223.54, 32.1],
                         label=["NODE 1", "NODE 2", "NODE 3"],
                         color=["#00ff1e", "#162347", "#dd4b39"])
        file_name = "SelectMenuTests.html"
        self.g.show(file_name)

        file_path = os.getcwd()
        file_path = "file:///" + file_path.replace(os.sep, '/') + "/" + file_name

        driver = webdriver.Chrome(service=self.service)
        driver.get(file_path)
        driver.implicitly_wait(0.1)

        self.assertIsNotNone(driver.find_element(By.ID, "mynetwork"))
        self.assertIsNotNone(driver.find_element(By.TAG_NAME, "canvas"))
        self.assertIsNotNone(driver.find_element(By.ID, "select-menu"))
        self.assertIsNotNone(driver.find_element(By.ID, "select-node"))

        self.assertFalse(driver.find_elements(By.ID, "filter-menu"))

        driver.quit()
        if os.path.exists("./" + file_name):
            os.remove("./" + file_name)


class FilterMenuTests(unittest.TestCase):
    service = ChromeService(executable_path=ChromeDriverManager().install())

    def setUp(self):
        self.g = Network(filter_menu=True)

    def test_graph(self):
        self.g.add_nodes([1, 2, 3],
                         value=[10, 100, 400],
                         title=["I am node 1", "node 2 here", "and im node 3"],
                         x=[21.4, 21.4, 21.4], y=[100.2, 223.54, 32.1],
                         label=["NODE 1", "NODE 2", "NODE 3"],
                         color=["#00ff1e", "#162347", "#dd4b39"])
        file_name = "FilterMenuTests.html"
        self.g.show(file_name)

        file_path = os.getcwd()
        file_path = "file:///" + file_path.replace(os.sep, '/') + "/" + file_name

        driver = webdriver.Chrome(service=self.service)
        driver.get(file_path)
        driver.implicitly_wait(0.1)

        self.assertIsNotNone(driver.find_element(By.ID, "mynetwork"))
        self.assertIsNotNone(driver.find_element(By.TAG_NAME, "canvas"))

        self.assertIsNotNone(driver.find_element(By.ID, "filter-menu"))
        self.assertIsNotNone(driver.find_element(By.ID, "select-item"))
        self.assertIsNotNone(driver.find_element(By.ID, "select-value"))
        self.assertIsNotNone(driver.find_element(By.ID, "select-property"))

        self.assertFalse(driver.find_elements(By.ID, "select-menu"))
        self.assertFalse(driver.find_elements(By.ID, "select-node"))

        driver.quit()
        if os.path.exists("./" + file_name):
            os.remove("./" + file_name)


class FilterAndSelectMenuTests(unittest.TestCase):
    service = ChromeService(executable_path=ChromeDriverManager().install())

    def setUp(self):
        self.g = Network(filter_menu=True, select_menu=True)

    def test_graph(self):
        self.g.add_nodes([1, 2, 3],
                         value=[10, 100, 400],
                         title=["I am node 1", "node 2 here", "and im node 3"],
                         x=[21.4, 21.4, 21.4], y=[100.2, 223.54, 32.1],
                         label=["NODE 1", "NODE 2", "NODE 3"],
                         color=["#00ff1e", "#162347", "#dd4b39"])
        file_name = "FilterAndSelectMenuTests.html"
        self.g.show(file_name)

        file_path = os.getcwd()
        file_path = "file:///" + file_path.replace(os.sep, '/') + "/" + file_name

        driver = webdriver.Chrome(service=self.service)
        driver.get(file_path)
        driver.implicitly_wait(0.1)

        self.assertIsNotNone(driver.find_element(By.ID, "mynetwork"))
        self.assertIsNotNone(driver.find_element(By.TAG_NAME, "canvas"))
        self.assertIsNotNone(driver.find_element(By.ID, "select-menu"))
        self.assertIsNotNone(driver.find_element(By.ID, "select-node"))
        self.assertIsNotNone(driver.find_element(By.ID, "filter-menu"))
        self.assertIsNotNone(driver.find_element(By.ID, "select-item"))
        self.assertIsNotNone(driver.find_element(By.ID, "select-value"))
        self.assertIsNotNone(driver.find_element(By.ID, "select-property"))

        driver.quit()
        if os.path.exists("./" + file_name):
            os.remove("./" + file_name)
