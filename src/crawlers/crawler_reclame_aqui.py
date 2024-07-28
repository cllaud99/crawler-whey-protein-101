import sys

import requests
from loguru import logger
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from config_logger import configure_logger

configure_logger()

# https://iosearch.reclameaqui.com.br/raichu-io-site-search-v1/segments/ranking/best/bancos-tradicionais-e-digitais/1/50 -> link test


class ReclameAquiScraper:
    """
    Scraper para buscar dados de empresas no Reclame Aqui.

    Atributos:
        page (int): Número da página atual da busca.
        results_per_page (int): Número de resultados por página.
        keyword (str): Palavra-chave para a busca.
        type_rank (str): Tipo de ranking a ser buscado.
        http (requests.Session): Sessão HTTP configurada com estratégias de retry.
        content (dict): Conteúdo da última resposta obtida.
    """

    def __init__(self):
        """
        Inicializa a instância do ReclameAquiScraper com valores padrão.
        """
        self.page = 1
        self.results_per_page = 50
        self.keyword = ""
        self.type_rank = "best"
        self.http = self._configure_session()
        self.content = None

    def start(self, keyword):
        """
        Inicia a busca pelas empresas com base na palavra-chave fornecida.

        Args:
            keyword (str): Palavra-chave para a busca.

        Returns:
            list: Lista de empresas encontradas.
        """
        logger.info("Iniciando busca para a palavra-chave: {}", keyword)
        self.keyword = keyword
        return self.paginated_search()

    def _configure_session(self):
        """
        Configura a sessão HTTP com uma estratégia de retry.

        Returns:
            requests.Session: Sessão HTTP configurada.
        """
        retry_strategy = Retry(total=3, status_forcelist=[403, 429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session = requests.Session()
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def search_companies(self):
        """
        Realiza a busca por empresas na página atual.

        Returns:
            dict: Conteúdo da resposta JSON.
        """
        url = f"https://iosearch.reclameaqui.com.br/raichu-io-site-search-v1/segments/ranking/{self.type_rank}/{self.keyword}/{self.page}/{self.results_per_page}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }
        try:
            response = self.http.get(url, headers=headers)
            if response.status_code == 200:
                self.content = (
                    response.json()
                )  # Armazenando a resposta no atributo content
                logger.info("Busca na página {} bem-sucedida", self.page)
                return self.content
            else:
                logger.error(
                    "Falha na requisição com código de status {}", response.status_code
                )
                logger.error(response.text)
        except requests.RequestException as e:
            logger.error("Falha na requisição: {}", e)

    def get_companies_data(self):
        """
        Extrai os dados das empresas do conteúdo da resposta.

        Returns:
            list: Lista de empresas.
        """
        if self.content:
            companies = self.content.get("companies", [])
            logger.info("Dados das empresas extraídos com sucesso")
            return companies
        else:
            logger.warning("Nenhum conteúdo disponível para extração")
            return []

    def get_total_pages(self):
        """
        Obtém o número total de páginas da busca.

        Returns:
            int: Número total de páginas.
        """
        if self.content and "pagination" in self.content:
            pagination = self.content["pagination"]
            total_pages = pagination.get("pages", 1)
            logger.info("Número total de páginas: {}", total_pages)
            return total_pages

        logger.warning("Nenhuma informação de paginação encontrada")
        return 1

    def paginated_search(self):
        """
        Realiza a busca paginada por empresas, combinando os resultados de todas as páginas.

        Returns:
            list: Lista de todas as empresas encontradas em todas as páginas.
        """
        all_companies = []
        self.search_companies()
        total_pages = self.get_total_pages()

        for page in range(1, total_pages + 1):
            self.page = page
            self.search_companies()
            all_companies.extend(self.get_companies_data())

        logger.info(
            "Busca paginada concluída. Total de empresas encontradas: {}",
            len(all_companies),
        )
        return all_companies


# Uso
if __name__ == "__main__":
    keyword = "bancos-tradicionais-e-digitais"
    scraper = ReclameAquiScraper()
    data = scraper.start(keyword=keyword)
    print(data)
    logger.info("Dados coletados: {}")