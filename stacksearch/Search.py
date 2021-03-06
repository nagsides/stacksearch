#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Bryan hu .

@Bryan hu .

Made with love by Bryan hu .

The primitive functions to use. # API
"""
import requests
from bs4 import BeautifulSoup as bs
from typing import Any
import httpx  # We probably should switch to aiohttp in the future
from time import sleep


def Search(
    Query: str,
    print_prog: bool = True,
    search_on_site: str = "stackoverflow",
    *args: Any,
    **kwargs: Any,
) -> dict:
    """Use this. This is the official API for the stacksearch module.

    Parameters
    ----------
    Query : str
        This is the query to search the stackexchange website for.
    print_prog : bool
        If True, prints the progress. Otherwise, it does not print the progress (the default is True).
    search_on_site : str
        The stackexchange website to search on (the default is "stackoverflow").
    *args : Any
        For backwards compatibility.
    **kwargs : Any
        For backwards compatibility.

    Returns
    -------
    dict
        In the format: {
        'question': ['answer1', 'answer2', ...], 'question2': ['answer1', ...]
        }

    """

    def rget(site):
        return requests.get(site, timeout=5,)

    def _remove_dot_com(string: str) -> str:
        string = str(string)
        # Maybe a regex is better here...
        if string.endswith(".com"):
            return string[0 : len(string) - 4]
        elif string.endswith(".org"):
            return string[0 : len(string) - 4]
        else:
            return string

    def _find_questions(soup):
        return {  # The raw ingredients
            question.string: question.get("href")
            for question in soup.find_all(
                attrs={"class": "question-hyperlink", "data-gps-track": None}
            )
        }

    def s(content):
        return bs(content.content, "lxml")

    search_on_site = _remove_dot_com(search_on_site)
    TEXT_REQUIREMENTS = {"class": "post-text", "itemprop": "text"}
    if print_prog:
        print(f"Requesting results from {search_on_site}...")
    r = rget(f"https://{search_on_site}.com/search?q={Query}")
    r.raise_for_status()
    if print_prog:
        print("Parsing response HTML...")
    soup = s(r)
    if print_prog:
        print("Collecting question links...")
    questions = _find_questions(soup)
    if print_prog:
        print("Requesting questions found (This may take a while)...")
    # _links_for_pages = (
    #     requests.get(link, timeout=5,)
    #     for link in map(
    #         lambda x: f"https://{search_on_site}.com" + x, iter(questions.values())
    #     )
    # )
    _links_for_pages = []
    for link in map(
        lambda x: f"https://{search_on_site}.com" + x, iter(questions.values())
    ):
        sleep(0.01)
        _links_for_pages.append(rget(link))
    if print_prog:
        print("Parsing questions found (This may take a while)...")
    pages = [  # Pages of all the questions related to Query
        s(link) for link in _links_for_pages
    ]
    if print_prog:
        print("Identifying question text...")
    full_questions = [page.find(attrs=TEXT_REQUIREMENTS).get_text() for page in pages]
    if print_prog:
        print("Identifying answers...")
    answers = [
        [
            answer.find(attrs=TEXT_REQUIREMENTS).get_text()
            for answer in page.find_all(attrs={"itemtype": "http://schema.org/Answer"})
        ]
        for page in pages
    ]
    if print_prog:
        print("Returning results...")
    return dict(zip(full_questions, answers))


async def fSearch(
    Query: str,
    print_prog: bool = True,
    search_on_site: str = "stackoverflow",
    *args: Any,
    **kwargs: Any,
) -> dict:
    """Use this. This is the async version of the Search API function.

    Parameters
    ----------
    Query : str
        This is the query to search the stackexchange website for.
    print_prog : bool
        If True, prints the progress. Otherwise, it does not print the progress (the default is True).
    search_on_site : str
        The stackexchange website to search on (the default is "stackoverflow").
    *args : Any
        For backwards compatibility.
    **kwargs : Any
        For backwards compatibility.

    Returns
    -------
    dict
        In the format: {
        'question': ['answer1', 'answer2', ...], 'question2': ['answer1', ...]
        }

    """

    async def _remove_dot_com(string: str) -> str:
        string = str(string)
        # Maybe a regex is better here...
        if string.endswith(".com"):
            return string[0 : len(string) - 4]
        elif string.endswith(".org"):
            return string[0 : len(string) - 4]
        else:
            return string

    async def findAnswers(pages):
        return [
            [
                answer.find(attrs=TEXT_REQUIREMENTS).get_text()
                for answer in page.find_all(
                    attrs={"itemtype": "http://schema.org/Answer"}
                )
            ]
            for page in pages
        ]

    async def findQuestions(soup):
        return {  # The raw ingredients
            question.string: question.get("href")
            for question in soup.find_all(
                attrs={"class": "question-hyperlink", "data-gps-track": None}
            )
        }

    async def rget(client, site):
        return await client.get(site, timeout=5,)

    async def s(content):
        return bs(content.content, "lxml")

    search_on_site = await _remove_dot_com(search_on_site)
    TEXT_REQUIREMENTS = {"class": "post-text", "itemprop": "text"}
    if print_prog:
        print(f"Requesting results from {search_on_site}...")
    async with httpx.AsyncClient() as client:
        r = await rget(client, f"https://{search_on_site}.com/search?q={Query}")
        r.raise_for_status()
        if print_prog:
            print("Parsing response HTML...")
        soup = bs(r.content, "lxml")
        if print_prog:
            print("Collecting question links...")
        questions = await findQuestions(soup)
        if print_prog:
            print("Requesting questions found (This may take a while)...")
        # _links_for_pages = [  # We cannot have a generator
        #     await client.get(link, timeout=5,)
        #     for link in map(
        #         lambda x: f"https://{search_on_site}.com" + x, iter(questions.values())
        #     )
        # ]
        _links_for_pages = []
        for link in map(
            lambda x: f"https://{search_on_site}.com" + x, iter(questions.values())
        ):
            sleep(0.01)
            _links_for_pages.append(await rget(client, link))
        if print_prog:
            print("Parsing questions found (This may take a while)...")
        pages = [  # Pages of all the questions related to Query
            bs(link.content, "lxml") for link in _links_for_pages
        ]
        if print_prog:
            print("Identifying question text...")
        full_questions = [
            page.find(attrs=TEXT_REQUIREMENTS).get_text() for page in pages
        ]
        if print_prog:
            print("Identifying answers...")
        answers = await findAnswers(pages)
        if print_prog:
            print("Returning results...")
        return dict(zip(full_questions, answers))
