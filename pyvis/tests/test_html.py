import os
import unittest
import networkx as nx

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.select import Select

from ..network import Network


class GraphTests(unittest.TestCase):
    """
    Tests to check the basic rendering of the basic network HTML and canvas
    """
    # setup service for the chrome driver to be used in test
    service = ChromeService(executable_path=ChromeDriverManager().install())

    def setUp(self):
        self.g = Network()

    def test_graph(self):
        # create simple network and save it in a file
        self.g.add_nodes([1, 2, 3],
                         value=[10, 100, 400],
                         title=["I am node 1", "node 2 here", "and im node 3"],
                         x=[21.4, 21.4, 21.4], y=[100.2, 223.54, 32.1],
                         label=["NODE 1", "NODE 2", "NODE 3"],
                         color=["#00ff1e", "#162347", "#dd4b39"])
        file_name = "GraphTests.html"
        self.g.show(file_name)

        # get the saved file path and change it into required format for the driver to read it
        file_path = os.getcwd()
        file_path = "file:///" + file_path.replace(os.sep, '/') + "/" + file_name

        # start the web driver, load the file and wait for a few seconds in precaution
        driver = webdriver.Chrome(service=self.service)
        driver.get(file_path)
        driver.implicitly_wait(0.1)

        # test for the main html container and then canvas
        self.assertIsNotNone(driver.find_element(By.ID, "mynetwork"))
        self.assertIsNotNone(driver.find_element(By.TAG_NAME, "canvas"))

        # make sure the filter menu and select menu divs are not rendered
        self.assertFalse(driver.find_elements(By.ID, "select-menu"))
        self.assertFalse(driver.find_elements(By.ID, "filter-menu"))

        # close the driver and delete the testing file
        driver.quit()
        if os.path.exists("./" + file_name):
            os.remove("./" + file_name)


class SelectMenuTests(unittest.TestCase):
    """
    Tests to check the rendering of the network HTML and select menu option
    """
    # setup service for the chrome driver to be used in test
    service = ChromeService(executable_path=ChromeDriverManager().install())

    def setUp(self):
        self.g = Network(select_menu=True)

    def test_graph(self):
        # create simple network with select-menu and save it in a file
        nx_graph = nx.cycle_graph(10)
        nx_graph.nodes[1]['title'] = 'Number 1'
        nx_graph.nodes[1]['group'] = 1
        nx_graph.nodes[3]['title'] = 'I belong to a different group!'
        nx_graph.nodes[3]['group'] = 10
        nx_graph.add_node(20, size=20, title='couple', group=2)
        nx_graph.add_node(21, size=15, title='couple', group=2)
        nx_graph.add_edge(20, 21, weight=5)
        nx_graph.add_node(25, size=25, label='lonely', title='lonely node', group=3)

        self.g.from_nx(nx_graph)
        file_name = "SelectMenuTests.html"
        self.g.show(file_name)

        # get the saved file path and change it into required format for the driver to read it
        file_path = os.getcwd()
        file_path = "file:///" + file_path.replace(os.sep, '/') + "/" + file_name

        # start the web driver, load the file and wait for a few seconds in precaution
        driver = webdriver.Chrome(service=self.service)
        driver.get(file_path)
        driver.implicitly_wait(0.1)

        # test for the main html container and then canvas
        self.assertIsNotNone(driver.find_element(By.ID, "mynetwork"))
        self.assertIsNotNone(driver.find_element(By.TAG_NAME, "canvas"))
        self.assertIsNotNone(driver.find_element(By.ID, "select-menu"))
        self.assertIsNotNone(driver.find_element(By.ID, "select-node"))

        # make sure the filter menu and select menu divs are not rendered
        self.assertFalse(driver.find_elements(By.ID, "filter-menu"))

        # close the driver and delete the testing file
        driver.quit()
        if os.path.exists("./" + file_name):
            os.remove("./" + file_name)


class FilterMenuTests(unittest.TestCase):
    service = ChromeService(executable_path=ChromeDriverManager().install())

    def setUp(self):
        self.g = Network(filter_menu=True)

    def test_graph(self):
        nx_graph = nx.cycle_graph(10)
        nx_graph.nodes[1]['title'] = 'Number 1'
        nx_graph.nodes[1]['group'] = 1
        nx_graph.nodes[3]['title'] = 'I belong to a different group!'
        nx_graph.nodes[3]['group'] = 10
        nx_graph.add_node(20, size=20, title='couple', group=2)
        nx_graph.add_node(21, size=15, title='couple', group=2)
        nx_graph.add_edge(20, 21, weight=5)
        nx_graph.add_node(25, size=25, label='lonely', title='lonely node', group=3)

        self.g.from_nx(nx_graph)
        file_name = "FilterMenuTests.html"
        self.g.show(file_name)

        # get the saved file path and change it into required format for the driver to read it
        file_path = os.getcwd()
        file_path = "file:///" + file_path.replace(os.sep, '/') + "/" + file_name

        # start the web driver, load the file and wait for a few seconds in precaution
        driver = webdriver.Chrome(service=self.service)
        driver.get(file_path)
        driver.implicitly_wait(0.1)

        # test for the main html container and then canvas
        self.assertIsNotNone(driver.find_element(By.ID, "mynetwork"))
        self.assertIsNotNone(driver.find_element(By.TAG_NAME, "canvas"))

        self.assertIsNotNone(driver.find_element(By.ID, "filter-menu"))
        self.assertIsNotNone(driver.find_element(By.ID, "select-item"))
        self.assertIsNotNone(driver.find_element(By.ID, "select-value"))
        self.assertIsNotNone(driver.find_element(By.ID, "select-property"))

        # make sure the filter menu and select menu divs are not rendered
        self.assertFalse(driver.find_elements(By.ID, "select-menu"))
        self.assertFalse(driver.find_elements(By.ID, "select-node"))

        select_element = driver.find_element(By.ID, "select-item")
        select_object = Select(select_element)
        self.assertTrue(select_object.options[0].text, "Select a network item")
        self.assertTrue(select_object.options[1].text, "edge")
        self.assertTrue(select_object.options[2].text, "node")

        # close the driver and delete the testing file
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

        # get the saved file path and change it into required format for the driver to read it
        file_path = os.getcwd()
        file_path = "file:///" + file_path.replace(os.sep, '/') + "/" + file_name

        # start the web driver, load the file and wait for a few seconds in precaution
        driver = webdriver.Chrome(service=self.service)
        driver.get(file_path)
        driver.implicitly_wait(0.1)

        # test for the main html container and then canvas
        self.assertIsNotNone(driver.find_element(By.ID, "mynetwork"))
        self.assertIsNotNone(driver.find_element(By.TAG_NAME, "canvas"))
        self.assertIsNotNone(driver.find_element(By.ID, "select-menu"))
        self.assertIsNotNone(driver.find_element(By.ID, "select-node"))
        self.assertIsNotNone(driver.find_element(By.ID, "filter-menu"))
        self.assertIsNotNone(driver.find_element(By.ID, "select-item"))
        self.assertIsNotNone(driver.find_element(By.ID, "select-value"))
        self.assertIsNotNone(driver.find_element(By.ID, "select-property"))

        # close the driver and delete the testing file
        driver.quit()
        if os.path.exists("./" + file_name):
            os.remove("./" + file_name)
