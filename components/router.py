import streamlit as st
from pages.dashboard import dashboard
from pages.consultas import consultas



ROUTES = {
    "dashboard": dashboard,
    "consultas": consultas,
}


def render(page):

    ROUTES[page]()