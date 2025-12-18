import os
import sys
import Orange
from Orange.widgets.widget import Input, Output
from AnyQt.QtWidgets import QApplication, QPushButton
from Orange.widgets.settings import Setting
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urlparse, urljoin, parse_qs
import unicodedata
import re

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.utils import thread_management, base_widget
    from Orange.widgets.orangecontrib.HLIT_dev.remote_server_smb import convert
else:
    from orangecontrib.AAIT.utils import thread_management, base_widget
    from orangecontrib.HLIT_dev.remote_server_smb import convert

class WebSearch(base_widget.BaseListWidget):
    name = "WebSearch"
    description = "Search url website from a query with DDG."
    icon = "icons/websearch.png"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/websearch.png"
    priority = 3000
    gui = ""
    want_control_area = False
    category = "AAIT - TOOLBOX"
    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/owwebsearch.ui")
    # Settings
    selected_column_name = Setting("content")

    class Inputs:
        data = Input("Data", Orange.data.Table)

    @Inputs.data
    def set_data(self, in_data):
        self.data = in_data
        if in_data is None:
            self.Outputs.data.send(None)
            return
        if self.data:
            self.var_selector.add_variables(self.data.domain)
            self.var_selector.select_variable_by_name(self.selected_column_name)
        self.run()

    class Outputs:
        data = Output("Data", Orange.data.Table)


    def __init__(self):
        super().__init__()
        # Qt Management
        self.setFixedWidth(480)
        self.setFixedHeight(450)

        self.pushButton_run =self.findChild(QPushButton, 'pushButton_send')
        self.pushButton_run.clicked.connect(self.run)


    def normaliser_texte(self, txt: str) -> str:
        """
        Met en minuscules, retire les accents et trim.
        """
        if not txt:
            return ""
        txt = txt.lower()
        txt = unicodedata.normalize("NFD", txt)
        txt = "".join(c for c in txt if not unicodedata.combining(c))
        return txt.strip()

    def extraire_mots_cles(self, requete: str):
        """
        Découpe la requête en mots-clés simples, en retirant
        les mots très fréquents (du, de, le, la, etc.).
        """
        stopwords = {"du", "de", "des", "le", "la", "les", "un", "une", "au", "aux", "et", "en", "pour", "sur", "a"}
        req_norm = self.normaliser_texte(requete)
        mots = re.findall(r"\w+", req_norm)
        mots_cles = [m for m in mots if m not in stopwords and len(m) > 2]
        return mots_cles or mots

    def recherche_duckduckgo(self, query, max_results=10):
        q = quote(query)
        url = f"https://duckduckgo.com/html/?q={q}"
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            r = requests.get(url, headers=headers, timeout=10)
            r.raise_for_status()
        except requests.RequestException as e:
            print(f"[ERREUR] Problème lors de la requête DuckDuckGo : {e}")
            return []

        soup = BeautifulSoup(r.text, "html.parser")
        resultats = []

        for a in soup.select("a.result__a")[:max_results]:
            titre = a.get_text(strip=True)
            lien = a.get("href", "")

            # Gestion des liens de redirection DuckDuckGo
            parsed = urlparse(lien)
            if parsed.netloc and "duckduckgo.com" in parsed.netloc and parsed.path.startswith("/l/"):
                qs = parse_qs(parsed.query)
                if "uddg" in qs:
                    lien = qs["uddg"][0]

            # Lien relatif -> absolu
            if lien.startswith("/"):
                lien = urljoin("https://duckduckgo.com", lien)

            resultats.append((titre, lien))

        return resultats

    def extraire_domaines(self, resultats_search):
        domaines = set()
        for _titre, url in resultats_search:
            try:
                parsed = urlparse(url)
                scheme = parsed.scheme or "https"
                if not parsed.netloc:
                    continue
                domaine = f"{scheme}://{parsed.netloc}"
                domaines.add(domaine)
            except Exception:
                pass
        return list(domaines)

    def trouver_flux_rss(self, url_site):
        try:
            r = requests.get(url_site, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            r.raise_for_status()
        except requests.RequestException as e:
            print(f"[ERREUR] Impossible d'accéder à {url_site} : {e}")
            return []

        soup = BeautifulSoup(r.text, "html.parser")
        flux = []

        for link in soup.find_all("link", type="application/rss+xml"):
            href = link.get("href")
            if href:
                href = urljoin(url_site, href)
                flux.append(href)

        for link in soup.find_all("a"):
            href = link.get("href", "")
            if not href:
                continue
            href_norm = href.lower()
            if "rss" in href_norm or "feed" in href_norm:
                flux.append(urljoin(url_site, href))

        return list(set(flux))

    def rechercher_articles_dans_flux(self, requete, flux_list, max_results=20):
        mots_cles = self.extraire_mots_cles(requete)
        articles = []

        headers = {"User-Agent": "Mozilla/5.0"}

        for flux in flux_list:
            try:
                r = requests.get(flux, headers=headers, timeout=10)
                r.raise_for_status()
                # Parse du flux en XML
                soup = BeautifulSoup(r.content, "xml")
            except requests.RequestException as e:
                print(f"[ERREUR] Problème lors de la lecture du flux {flux} : {e}")
                continue

            # Gestion RSS (<item>) et Atom (<entry>)
            for entry in soup.find_all(["item", "entry"]):
                # Titre
                titre_tag = entry.find("title")
                titre = titre_tag.get_text(strip=True) if titre_tag else ""

                # Résumé / description
                resume_tag = entry.find("description") or entry.find("summary")
                resume = resume_tag.get_text(strip=True) if resume_tag else ""

                # Lien
                lien_tag = entry.find("link")
                lien = ""
                if lien_tag:
                    # Atom : <link href="...">
                    if lien_tag.has_attr("href"):
                        lien = lien_tag["href"]
                    else:
                        # RSS : <link>https://...</link>
                        lien = lien_tag.get_text(strip=True)

                # Date
                date_tag = (
                        entry.find("pubDate")
                        or entry.find("published")
                        or entry.find("updated")
                )
                date = date_tag.get_text(strip=True) if date_tag else "Date inconnue"

                texte_complet = self.normaliser_texte(titre + " " + resume)

                # Condition : au moins un mot-clé présent dans titre+résumé
                if any(mot in texte_complet for mot in mots_cles):
                    articles.append(
                        {
                            "titre": titre,
                            "url": lien,
                            "date": date,
                            "source_flux": flux,
                        }
                    )
                    if len(articles) >= max_results:
                        return articles

        return articles

    def pipeline_veille_requete(self,requete):
        resultats = self.recherche_duckduckgo(requete)
        if not resultats:
            print("Aucun résultat trouvé sur DuckDuckGo.")
            return []
        print(resultats)
        domaines = self.extraire_domaines(resultats)

        flux = []
        for d in domaines:
            found = self.trouver_flux_rss(d)
            if found:
                print(f"Flux trouvés sur {d}:")
                for f in found:
                    print(" ->", f)
                flux.extend(found)

        flux = list(set(flux))

        if not flux:
            return [
                {"titre": t, "url": u, "date": None, "source_flux": None, "source": "web"}
                for t, u in resultats
            ]
        articles = self.rechercher_articles_dans_flux(requete, flux)

        if not articles:
            return [
                {"titre": t, "url": u, "date": None, "source_flux": None, "source": "web"}
                for t, u in resultats
            ]
        return articles


    def run(self):
        self.error("")
        self.warning("")
        if self.data is None:
            self.Outputs.data.send(None)
            return

        if not self.selected_column_name in self.data.domain:
            self.warning(f'Previously selected column "{self.selected_column_name}" does not exist in your data.')
            return

        self.query = self.data.get_column(self.selected_column_name)[0]

        self.progressBarInit()
        self.thread = thread_management.Thread(self.pipeline_veille_requete, self.query)
        self.thread.progress.connect(self.handle_progress)
        self.thread.result.connect(self.handle_result)
        self.thread.finish.connect(self.handle_finish)
        self.thread.start()

    def handle_progress(self, progress) -> None:
        value = progress[0]
        text = progress[1]
        if value is not None:
            self.progressBarSet(value)
        if text is None:
            self.textBrowser.setText("")
        else:
            self.textBrowser.insertPlainText(text)

    def handle_result(self, result):
        if result is None or len(result) == 0:
            self.Outputs.data.send(None)
            return
        data = convert.convert_json_implicite_to_data_table(result)
        self.Outputs.data.send(data)

    def handle_finish(self):
        self.progressBarFinished()

    def post_initialized(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_widget = WebSearch()
    my_widget.show()

    if hasattr(app, "exec"):
        sys.exit(app.exec())
    else:
        sys.exit(app.exec_())