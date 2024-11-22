
from .scraper import Backend

class gmap_Scraper:
    def __init__(self):
            self.outputFormatValue='.xlsx'
            self.headlessMode=False
            # self.startscraping()

    def startscraping(self,searchQuery,output_file):
            backend = Backend(
                searchQuery,
                self.outputFormatValue,
                healdessmode=self.headlessMode,
                output_file_name=output_file
            )

            backend.mainscraping()
            

