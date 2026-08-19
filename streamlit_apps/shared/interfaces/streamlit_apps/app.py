

from abc import ABC, abstractmethod
import streamlit as st


class AppInterface(ABC):
    
    @abstractmethod
    def run(self):
        pass