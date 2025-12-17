Webis - GUI Interface Usage
===================

Want to use Webis more conveniently through the GUI interface? This document will teach you how to use the GUI we designed for Webis. We assume you have already installed Webis. If not, please read README.md.

Starting the Frontend
--------

After starting the local model server, use the \ ``webis``\ command to start the frontend Vue3 project:

.. code:: bash

   # Start the frontend Vue3 project
   webis --gui

HOME Page
--------

After successful startup, the Web HOME page opens by default on port 5173

CLEAN Page
---------

On the CLEAN page, you can clean web pages and generate data formats suitable for LLM use. The following cleaning functions are provided:

-  Simple Crawling

-  Single Page Cleaning

-  Multiple Page Cleaning

Both Simple Crawling and Single Page Cleaning offer two ways to input web pages: \ ``Upload HTML File``\ and \ ``Input URL``\, 
with a preview of the web content below. Multiple Page Cleaning processes through \ ``Batch Upload HTML Files``\ in a folder

RESULTS Page
-----------

On the RESULTS page, you can view the web page cleaning results and export data for LLM use. The main features include:

-  Keyword search for cleaning results

-  Filter results by date

-  Export cleaning results in \ ``XML``\ or \ ``JSON format``\

-  Delete cleaning results

DOCS Page
--------

The DOCS page provides an introduction to the Webis project
