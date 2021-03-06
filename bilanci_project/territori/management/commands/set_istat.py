# coding=utf-8
import StringIO
from pprint import pprint
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.management.base import BaseCommand
from unidecode import unidecode
from optparse import make_option
import requests
import zipfile
import csv
import logging
from territori.models import Territorio, Contesto

__author__ = 'stefano'


class Command(BaseCommand):
    """
    Import Istat inhabitants data from Istat files into Contesto model
    """

    help = "Import Istat inhabitants data from Istat files into Contesto model"

    option_list = BaseCommand.option_list + (
        make_option('--years',
            dest='years',
            default='',
            help='Years to fetch. From 2002 to 2012. Use one of this formats: 2012 or 2003-2006 or 2002,2004,2006'),
        make_option('--dry-run',
            dest='dryrun',
            action='store_true',
            default=False,
            help='Set the dry-run command mode: no actual import is made'),
        make_option('--limit',
            dest='limit',
            default=0,
            help='Limit of records to import'),
        make_option('--offset',
            dest='offset',
            default=0,
            help='Offset of records to start from'),
    )

    logger = logging.getLogger('management')
    dryrun = None



    def handle(self, *args, **options):

        verbosity = options['verbosity']
        if verbosity == '0':
            self.logger.setLevel(logging.ERROR)
        elif verbosity == '1':
            self.logger.setLevel(logging.WARNING)
        elif verbosity == '2':
            self.logger.setLevel(logging.INFO)
        elif verbosity == '3':
            self.logger.setLevel(logging.DEBUG)

        offset = int(options['offset'])
        limit = int(options['limit'])
        dryrun = options['dryrun']


        ###
        # years
        ###
        years = options['years']
        if not years:
            self.logger.error("Missing years parameter")
            return

        if "-" in years:
            (start_year, end_year) = years.split("-")
            years = range(int(start_year), int(end_year)+1)
        else:
            years = [int(y.strip()) for y in years.split(",") if 2001 < int(y.strip()) < 2013]

        if not years:
            self.logger.error("No suitable year found in {0}".format(years))
            return

        self.logger.info("Considering years: {0}".format(years))
        self.years = years
        self.get_istat_data(years, offset, limit, dryrun)



    def get_istat_data(self, years, offset, limit, dryrun):

        file_url_format = "http://demo.istat.it/bil{0}/dati/comuni.zip"

        missing_istat_id = []
        missing_territori = []

        for year in years:
            self.logger.error("Considering yr:{0}".format(year))
            if year != 2011:
                file_url = file_url_format.format(year)
            else:
                file_url ="http://demo.istat.it/bil20111009/dati/comuni.zip"

            self.logger.debug("Getting {0} file".format(file_url))
            response = requests.get(file_url)
            zip_file = zipfile.ZipFile(StringIO.StringIO(response.content))
            csv_file = zip_file.open('dati/comuni.csv')
            csv_reader = csv.reader(csv_file, delimiter=',', quoting=csv.QUOTE_NONE)

            istat_denominazione_col = None
            istat_abitanti_col = None
            istat_femmine_col = None
            istat_maschi_col = None

            # identifies the header line
            for line in csv_reader:
                if len(line):
                    if line[0] == 'Codice Comune':
                        
                        # creates lower case list of string
                        line_lowercase = [x.lower() for x in line]
                        # identifies the interesting cols in the header based on column header text
                        try:
                            istat_denominazione_col = line_lowercase.index('Descrizione Comune'.lower())
                            istat_abitanti_col = line_lowercase.index('Popolazione al 31 Dicembre - Totale'.lower())
                            istat_femmine_col = line_lowercase.index('Popolazione al 31 Dicembre - Femmine'.lower())
                            istat_maschi_col = line_lowercase.index('Popolazione al 31 Dicembre - Maschi'.lower())
                            break
                        except ValueError:
                            self.logger.error("Data columns not found in table heading:{0}. Quitting".format(line))

                            return


            # reads the table data skipping the header
            for line in csv_reader:

                # removes zero-padding from istat_code
                istat_id = line[0].lstrip("0")

                # removes trailing spaces from comune name
                # replaces vowels followed by apostrophe with accented vowel
                istat_denominazione = line[istat_denominazione_col].strip().\
                    replace("a'","à").replace("e'","è").\
                    replace("i'","ì").replace("o'","ò").replace("u'","ù")

                istat_abitanti = int(line[istat_abitanti_col])
                istat_femmine = int(line[istat_femmine_col])
                istat_maschi = int(line[istat_maschi_col])
                territorio = None

                # get territorio with istat_id
                try:
                    territorio = Territorio.objects.get(istat_id=istat_id)
                except ObjectDoesNotExist:
                    if istat_id not in missing_istat_id:
                        missing_istat_id.append(istat_id)

                    # try to get the territorio using the Territorio name
                    try:
                        territorio = Territorio.objects.get(
                            territorio = Territorio.TERRITORIO.C,
                            denominazione__iexact = istat_denominazione
                        )
                    except ObjectDoesNotExist:
                        self.logger.error(u"Territorio with istat name {0} not found".format(istat_denominazione))
                        if istat_denominazione not in missing_territori:
                            missing_territori.append(istat_denominazione)
                        continue
                    except MultipleObjectsReturned:
                        self.logger.error(u"Multiple territorio returned for istat name {0}".format(istat_denominazione))
                        if istat_denominazione not in missing_territori:
                            missing_territori.append(istat_denominazione)
                        continue



                if territorio:
                    contesto, create_obj = Contesto.objects.get_or_create(territorio=territorio, anno = year)
                    if create_obj:
                        self.logger.debug(u'Contesto for territorio: {0}, yr:{1} not found, creating it.'.format(territorio,year))

                    if not dryrun:
                        contesto.istat_abitanti = istat_abitanti
                        contesto.istat_femmine = istat_femmine
                        contesto.istat_maschi = istat_maschi
                        contesto.save()


        self.logger.info("== END ==")

        # logs the list of missing_istat_id
        if len(missing_istat_id):
            self.logger.error("Missing territori with following istat id:")
            self.logger.error(",".join(missing_istat_id))

        # logs the list of missing_istat_id
        if len(missing_territori):
            self.logger.error("Missing territori with following name could not get istat context:")
            self.logger.error(",".join(missing_territori))
