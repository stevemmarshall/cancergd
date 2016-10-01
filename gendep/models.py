from django.db import models
#from django.core.urlresolvers import reverse
from django.conf.urls import url
from django.utils import timezone # For Comment() table, with USE_TZ=True in settings.py, and "pip install pytz" https://docs.djangoproject.com/en/1.9/topics/i18n/timezones/

# NOTE: always use lower case for field names, as MySQL expects lower case.
# See the end of this models.py file for some additional useful notes.

# The Django 'migration' command line tool should alter any changed fields ok. However if that fails then to manually modify field in MySQL to match the changed Gene gene_name, eg driver increased from 20 to 25 characters:
#   mysql -u sbridgett -h sbridgett.mysql.pythonanywhere-services.com
#   use sbridgett$gendep
# OR:
#   mysql -u cgenetics -h cgenetics.mysql.pythonanywhere-services.com
#   use cgenetics$gendep
# THEN:
#   describe gendep_dependency;
#   ALTER TABLE gendep_dependency MODIFY driver varchar(20) NOT NULL;

# To manually remove migrations from the Django migrations table, can use:
#   delete from django_migrations where app='gendep'; 


class Gene(models.Model):
    """ Information about each gene """
    # Old Primary key:  gene_name   = models.CharField('Gene name', max_length=25, primary_key=True, db_index=True)  # This is a ForeignKey for both driver AND target in the Dependenct table. Needs to be 25 charactes to cope with eg: 'LOC100499484.C9ORF174' which is 21 characters
    entrez_id   = models.CharField('Entrez Id', max_length=10, primary_key=True, db_index=True) # This is now a foreign key. Entrez gene. Was: blank=True
    gene_name   = models.CharField('Gene name', max_length=25, unique=True, db_index=True)  # This is a ForeignKey for both driver AND target in the Dependenct table. Needs to be 25 charactes to cope with eg: 'LOC100499484.C9ORF174' which is 21 characters
    original_name = models.CharField('Original name', max_length=30) # As some gene_names are changed, especially needed for the Achilles and Colt studies.
    is_driver   = models.BooleanField('Is driver', db_index=True, default=False) # So will know for driver search menu/webpage which to list in the dropdown menu
    is_target   = models.BooleanField('Is target', db_index=True, default=False) # So will know for target search menu/webpage which to list in the dropdown menu
    alteration_considered = models.TextField('Alteration_considered', blank=True) # Type of alteration considered for this driver gene.
    full_name   = models.CharField('Full name', max_length=200)
    ensembl_id  = models.CharField('Ensembl Gene Id', max_length=20, blank=True) # Ensembl gene
    ensembl_protein_id  = models.CharField('Ensembl Protein Id', max_length=20, blank=True) # Ensembl protein for String-db

    cosmic_id   = models.CharField('COSMIC Id', max_length=25, blank=True) # Same as gene_name, or empty if not in COSMIC, so can be 25 or more charactes long, eg: "TNFSF12-TNFSF13"
    cancerrxgene_id = models.CharField('CancerRxGene Id', max_length=10, blank=True) # CancerRxGene
    omim_id     = models.CharField('OMIM Id', max_length=10, blank=True) # Online Mendelian Inheritance in Man
    uniprot_id  = models.CharField('UniProt Ids', max_length=20, blank=True) # UniProt protein Ids.
    vega_id     = models.CharField('Vega Id', max_length=25, blank=True) # Vega Id.
    hgnc_id     = models.CharField('HGNC Id', max_length=10, blank=True) # HGNC Id.    
    # prevname_synonyms = models.CharField('Synonyms and previous names for gene name', max_length=250, blank=True) # contains previous names and synonyms.
    prevname_synonyms = models.TextField('Synonyms and previous names for gene name', blank=True, default='') # contains previous names and synonyms.    
    inhibitors     = models.TextField('Inhibitors', blank=True, default='') # List of drugs separated by semi-colons or commas
    ncbi_summary   = models.TextField('Entrez Gene Sumary', blank=True, default='') # Summary text of gene from NCBI

    # The following are pre-calculated fields that can be removed if data is cached by Django:
    #driver_num_studies = models.PositiveSmallIntegerField('Number of studies', default=0, blank=True) # PositiveSmallInteger is 0 to 32767; cached number of studies that have this as a driver, generated by SQL query after loading data.
    #driver_study_list = models.CharField('Tissues this driver has been tested on', max_length=250, blank=True) # This should match the 'driver_num_studies'

    # driver_num_histotypes = models.PositiveSmallIntegerField('Number of histotypes for this driver', default=0, blank=True)
    # driver_histotype_list = models.CharField('Tissues this driver has been tested on', max_length=250, blank=True) # This should match the 'driver_num_histotypes'

    # driver_num_targets = models.PositiveIntegerField('Number of targetted genes for this driver', default=0, blank=True) # positiveinteger 0 to 2147483647; cached number of targets, generated by SQL query after loading data.

    # target_num_drivers = models.PositiveIntegerField('Number of driver genes for this target', default=0, blank=True) # PositiveInteger 0 to 2147483647; cached number of targets, generated by SQL query after loading data.
    # target_num_histotypes = models.PositiveIntegerField('Number of histotypes for this target', default=0, blank=True) # Cached number of histotypes, generated by SQL query after loading data.

     
    def __str__(self):
        # return self.gene_name+' '+self.entrez_id+' '+self.ensembl_id
        return self.gene_name
        
    # def prev_names_and_synonyms_spaced(self):
    #    # To dispay in the template for the driver search box - but now are stored spaced in the database.
    #    return self.prevname_synonyms.replace('|',' | ')
        
    def driver_histotype_list_full_names(self):
        result = ''
        for h in self.driver_histotype_list.split(';'):
            if result != '': result += ", " # Just using a comma as newline doesn't work in html, would need <br/>
            result += Dependency.histotype_full_name(h)
        return result

    def driver_histotype_list_full_names2(histotype_list):
        result = ''
        for h in histotype_list.split(','):
            if result != '': result += ", " # Just using a comma as newline doesn't work in html, would need <br/>
            result += Dependency.histotype_full_name(h)
        return result



class Study(models.Model):
    """ Details for the research study papers """
    EXPERIMENTTYPE_CHOICES = (
    ('kinome siRNA', 'kinome siRNA'),
    ('genome-wide shRNA', 'genome-wide shRNA'),
    )
    class Meta:
        verbose_name_plural = "Studies" # Otherwise the Admin page just adds a 's', ie. 'Studys'
        
    pmid        = models.CharField('PubMed ID', max_length=30, primary_key=True, db_index=True)   # Can add: help_text="Please use the following format: <em>YYYY-MM-DD</em>."
    code        = models.CharField('Code', max_length=1, default=' ') # eg. 'A' for Achilles, for faster transfer to webbrowser.
    short_name  = models.CharField('Short Name', max_length=50) # eg. 'Campbell (2016)'
    title       = models.CharField('Title', max_length=250)
    authors     = models.TextField('Authors')
    experiment_type = models.CharField('Experiment type', max_length=20, choices=EXPERIMENTTYPE_CHOICES, db_index=True)
    abstract    = models.TextField('Abstract')
    summary     = models.TextField('Summary') # Short summary line to use on the results table
    journal     = models.CharField('Journal', max_length=100)
    pub_date    = models.CharField('Date published', max_length=30)  # OR: models.DateTimeField('Date published')
    
    # The following pre-computed fields could instead be caclulated and cached by Django:
    # num_drivers = models.PositiveIntegerField('Number of driver genes', default=0, blank=True) # PositiveInteger 0 to 2147483647; cached number of drivers, generated by SQL query after loading data.
    # num_histotypes = models.PositiveSmallIntegerField('Number of histotypes', default=0, blank=True) # SmallInteger is 0 to 32767; cached number of histotypes that have this as a study, generated by SQL query after loading data.
    num_targets = models.PositiveIntegerField('Number of targetted genes', default=0, blank=True)

        
    def __str__(self):
        return self.pmid
        
    # These url() and weblink() functions could be moved to "cgdd_functions.js" javascript.
    # This weblink (and url) function is still used in the studies.html template and in view.py for downloading as excel file:
    def url(self_or_studyid): # Using optional pmid as a parameter so can be called as: Study.url('1234') without needing the study instance
        #        if self.pmid[0:7] == 'Pending': href = reverse('gendep:study', kwargs={'pmid': self.pmid})
        #if self.pmid[0:7] == 'Pending': href = reverse('gendep:study')
        # Fix the problem with reverse() later.
        pmid = self_or_studyid if isinstance(self_or_studyid, str) else self_or_studyid.pmid        
        return ('/gendep/study/%s/' if pmid[0:7]=='Pending' else 'http://www.ncbi.nlm.nih.gov/pubmed/%s') %(pmid)
        
    def weblink(self):
        return '<a class="tipright" href="%s" target="_blank">%s<span>%s, %s et al, %s, %s</span></a>' %(self.url(), self.short_name, self.title, self.authors[0:30], self.journal, self.pub_date)

# This histotype class is now a choices tuple within the Dependency class:
# class Histotype(models.Model):
#    histotype   = models.CharField('Histotype', max_length=10, primary_key=True, db_index=True)
#    full_name   = models.CharField('Histotype', max_length=30)

NAME='_name'

class Dependency(models.Model):
    """ Dependency = Driver-Target interactions """
    # Values for the histotype choices CharField. The two letter codes at right are used for faster transfer to webbrowser.
    HISTOTYPE_CHOICES = (
      ("BONE",                               "Bone"),        #  "Bo"),  was "BONE", in R - but using Bone, as Achilles has some non-Osteosarcoma bone cell-lines
      ("BREAST",                             "Breast"),#        "Br"),
      ("CENTRAL_NERVOUS_SYSTEM",             "CNS"),#           "CN"),
#      ("CERVICAL",                           "Cervical"),#      "Ce"), # In Campbell, Not in Achilles
      ("CERVIX",                             "Cervix"),#        "Ce"), # Changed from Cervical to Cervix, Sept 2016. In Campbell, Not in Achilles      
	  ("ENDOMETRIUM",                        "Endometrium"),#   "En"),  BUT only 2 cell lines so not analysed by R ?
	  ("HAEMATOPOIETIC_AND_LYMPHOID_TISSUE", "Blood & Lymph"),# "HL"),
      ("HEADNECK",                           "Head & Neck"),#   "HN"), # In Campbell, Not in Achilles
	  ("INTESTINE",                          "Intestine"),#     "In"),
	  ("KIDNEY",                             "Kidney"),#        "Ki"), # kidney not in results even though 10 cell lines      
      ("LARGE_INTESTINE",                    "Large Intestine"), # Instead of Intestine.
      ("LUNG",                               "Lung"),#          "Lu"),
      ("OESOPHAGUS",                         "Esophagus"),#     "Es"),  # or "Oesophagus"
      # ("OSTEOSARCOMA",                       "Osteosarcoma"),#  "Os"),  was "BONE", in R, and using Bone as Achilles has non-osteoscarcoma bone cancer cell lines.
      ("OVARY",                              "Ovary"),#         "Ov"),
      # More added below for Achilles data - may need to add these to the index template
	  ("PANCREAS", 	                         "Pancreas"),#      "Pa"),
      # ("LIVER",                            "Liver"),#         "Li"), only 1 cell line so not analysed by R
	  ("PLEURA",                             "Pleura"),#        "Pl"), PLEURA is in PANCAN dependencies, separate from LUNG.
	  ("PROSTATE",                           "Prostate"),#      "Pr"),
	  ("SKIN",                               "Skin"),#          "Sk"),
	  ("SOFT_TISSUE",                        "Soft tissue"),#   "So"), only 2 celllines so not analysed by R ?
	  ("STOMACH",                            "Stomach"),#       "St"),
	  ("URINARY_TRACT",                      "Urinary tract"),# "Ur"),
      ("PANCAN",                             "Pan cancer"),#    "PC"),
    )

    class Meta:
        
        unique_together = (('driver', 'target', 'histotype', 'study'),) # Note: needs the comma at end to keep it as tuple of tuples.
        # The 'target_variant' is no longer part of unique key, as only keeping the variant with the lowest wilcox_p value
        verbose_name_plural = "Dependencies" # Otherwise the Admin page just adds a 's', ie. 'Dependencys'

    # driver_name = models.ForeignKey(Gene, verbose_name='Driver gene name', db_column='driver_name', to_field='gene_name', related_name='+', db_index=True, on_delete=models.PROTECT)
    # target_name = models.ForeignKey(Gene, verbose_name='Target gene name', db_column='target_name', to_field='gene_name', related_name='+', db_index=True, on_delete=models.PROTECT)
    # Changing to using entrez_ids as primary key in Gene table:
    driver = models.ForeignKey(Gene, verbose_name='Driver entrez', db_column='driver', to_field='entrez_id', related_name='+', db_index=True, on_delete=models.PROTECT)
    target = models.ForeignKey(Gene, verbose_name='Target entrez', db_column='target', to_field='entrez_id', related_name='+', db_index=True, on_delete=models.PROTECT)
        
    target_variant = models.CharField('Achilles gene variant_number', max_length=2, blank=True) # As Achilles has some genes entered with 2 or 3 variants.
    mutation_type = models.CharField('Mutation type', max_length=10)  # Set this to 'Both' for now.
    wilcox_p    = models.FloatField('Wilcox P-value', db_index=True)  # WAS: DecimalField('Wilcox P-value', max_digits=12, decimal_places=9). Index on wilcox_p because this is the order_by clause for the dependency result query.
    effect_size = models.FloatField('Effect size', db_index=True)
    
    za = models.FloatField('zA', db_index=True, default=-999.99)
    zb = models.FloatField('zB', db_index=True, default=-999.99)
    zdiff = models.FloatField('zDelta Score', db_index=True, default=-999.99)
    
    # Change this later to a Character when next rebuild table, as can't alter table columns in SQLite
    # interaction = models.NullBooleanField('Functional interaction', db_index=True, ) # True if there is a known functional interaction between driver and target (from string-db.org interaction database). Allows null (ie. for unknown) values
    # Need to update the "add_ensembl_proteinids_and_stringdb.py" and "views.py" script field name too (as can't change field type in sqlite):
    interaction = models.CharField('String interaction', max_length=10, blank=True)  # Medium, High, Highest (or 4,7,9) for 400,700,900
    
    # interaction = models.CharField('Functional interaction', max_length=10, db_index=True, ) # For (Medium, High, Higher) if there is a known functional interaction between driver and target (from string-db.org interaction database). Allows null (ie. for unknown) values
    study       = models.ForeignKey(Study, verbose_name='PubMed ID', db_column='pmid', to_field='pmid', on_delete=models.PROTECT, db_index=True)
    
    # No longer need to store this table_name:
    # study_table = models.CharField('Study Table', max_length=10) # The table in Campbell(2016) that the initial data is from.
    
    # 'HAEMATOPOIETIC_AND_LYMPHOID_TISSUE' is 35 characters long:
    histotype   = models.CharField('Histotype', max_length=35, choices=HISTOTYPE_CHOICES, db_index=True )   # also optional "default" parameter
    # Previously used a ForeignKey to a separate Histotype class:
    # histotype   = models.ForeignKey(Histotype, verbose_name='Histotype', db_column='histotype', to_field='histotype', related_name='+', db_index=True, on_delete=models.PROTECT)
    # Now using a choices field instead of the above Foreign key to a separate table. 
    # could also add as a validator for a web form, eg: validators=[validate_histotype_choice],
        
    boxplot_data = models.TextField('Boxplot data in CSV format', blank=True, default='') # The cell-lines and zscores for plotting the boxplot with javascript SVG.
    
    def is_valid_histotype(h): # was:    def is_valid_histotype(h):    
       for row in Dependency.HISTOTYPE_CHOICES:
          if row[0] == h: return True
       return False
       
# ?????? - maybe use a static method?    
    def histotype_full_name(h):  # was:     def histotype_full_name(h):
        for row in Dependency.HISTOTYPE_CHOICES:
            if row[0] == h: return row[1]
        return "Unknown"
       
#    def __str__(self):
#        return self.target.gene_name
    
    # Based on: https://groups.google.com/forum/#!topic/django-users/SzYgjbrYVCI
    def __setattr__(self, name, value):
        if name == 'histotype':
            found = False
            for row in Dependency.HISTOTYPE_CHOICES:
                if row[0] == value:
                    found = True
                    break
            if not found: raise ValueError('Invalid value "%s" for histotype choices: %s' %(value, Dependency.HISTOTYPE_CHOICES))
        models.Model.__setattr__(self, name, value)
        

class Comment(models.Model):
    """ Stores feedback (comments and queries) from the "Contact" page, in case sending the email fails """
    name        = models.CharField('Name', max_length=50) # Otional help_text="Please use the following format: <em>YYYY-MM-DD</em>."
    email       = models.CharField('Email', max_length=50)
    # interest    = models.TextField('Interest') # Area of interest of person making the comment
    comment     = models.TextField('Comment')
    ip          = models.CharField('IP address', max_length=30) # To help block/blacklist any spam messages.
    date        = models.DateTimeField('Date', default=timezone.now, editable=False,)  # Use: django.utils.timezone.now() and set USE_TZ=True in settings.py. Alternatively default=datetime.now or default=timezone.now  


# NOTES:
# =====
# For ForeignKeys:
#   if don't need the ForeignKey indexed, then add: db_index=False 
#   if use db_column='name' then won't append an '_id' to the column name
#   set related_name='+' so that Django will not create a backwards relation
# Maybe add a 'db_constraint=False' to not enforce foreign key

# primary key could be: driver + target + 

# To use extra id field in the Gene table, use just:   
#    driver      = models.ForeignKey(Gene, verbose_name='Driver gene', related_name='driver_gene', db_index=True, on_delete=models.PROTECT)
#    target      = models.ForeignKey(Gene, verbose_name='Target gene', related_name='target_gene', db_index=True, on_delete=models.PROTECT)

#    plot        =  models.CharField or models.SlkugField or models.ImageField or just use the driver name for now.

# To ensure unique: use 'unique_together':
# class Meta:
#        unique_together = (('driver', 'target'),)
# Alternatively this CompositeField is not in Django 1.9, but should be in future versions:
#    driver_target = models.CompositeField(('driver', 'target'), primary_key = True)

# Alternative actions to take when foreign key is deleted:
# on_delete=models.CASCADE
# on_delete=models.PROTECT      Prevent deletion of the referenced object by raising ProtectedError, a subclass of django.db.IntegrityError.
# on_delete=models.DO_NOTHING   Take no action. If your database backend enforces referential integrity, this will cause an IntegrityError unless you manually add an SQL ON DELETE constraint to the database field.