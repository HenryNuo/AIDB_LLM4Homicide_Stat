# Homicide Statistics LLM Web Application

Task:
Design an LLM agent that does the following task:

1. Looks up the pages for homicide statistics for the cities of New York, New Orleans, and Los Angeles.
2. Extracts the homicide numbers for each year for the past 5 years.
3. Dumps them in a structured table.
You may give the agent extremely specific instructions if necessary.

Send the code and a short writeup of your findings.

## Overview

This repository contains a Dash-based web application that uses an OpenAI-powered language model to extract homicide statistics from the web for various cities. Users can request specific data, and the application will return the extracted data in structured tables for each city.

![Los Angeles Homicide Data](assets/los%20angeles%20web.png)

## Usage

Type prompt into input field.

```bash
look for {City} homicide data from {year} to {year} and extract in a table.
```

## Features

- **Interactive Web Interface**: Enter queries in a search bar to request homicide data.
- **Structured Responses**: The app uses an LLM (powered by GPT-3.5-turbo or GPT-4) to retrieve and format homicide data in a consistent, structured format.
- **Dynamic Tables**: For each city, a separate table is displayed with the homicide data, including year and the number of murders for that year.
- **Bootstrap UI**: The application uses Bootstrap for styling, providing a responsive and clean user interface.

## Components

- **LangChain**: The app uses the `LangChain` framework to integrate with the OpenAI LLM and the Tavily API for processing search queries and generating responses.
- **Tavily API**: Provides real time web search results to feed into the LLM, allowing it to fetch relevant data from across the web.
- **Dash**: A web framework for Python that allows interactive web applications to be created quickly and efficiently.
- **OpenAI API**: Used for querying the language model (GPT-3.5-turbo) and processing the natural language queries.
- **Pandas**: For processing structured data (years and murder counts) and displaying it in a tabular format.
