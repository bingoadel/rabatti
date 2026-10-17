from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Basisklasse für alle Agenten.

    Summary:
        Diese Klasse definiert das gemeinsame Interface. Jeder Agent muss
        eine Methode 'answer' besitzen. Das ist nützlich, weil alle Agenten
        dieselbe Weise benutzen, um eine Frage zu beantworten.
    """

    @abstractmethod
    def answer(self, question: str) -> str:
        """Beantworte eine Frage und gebe eine Antwort als String zurück.

        Summary:
            'abstractmethod' bedeutet: Diese Methode muss in jeder konkreten
            Unterklasse implementiert werden. So erzwingt Python einen klaren Vertrag.
        """
        raise NotImplementedError
