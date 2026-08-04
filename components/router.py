import streamlit as st

from pages.dashboard import dashboard

from pages.consultas import consultas

from pages.orcamentos import orcamentos


ROUTES = {

    "dashboard": dashboard,

    "consultas": consultas,

    "orcamentos": orcamentos

}


def render(page):

    ROUTES[page]()